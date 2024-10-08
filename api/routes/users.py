from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection
from database.stokvel_queries.queries import get_all_applications
from database.user_queries.queries import (
    find_user_by_number,
    get_account_details,
    get_total_number_of_users,
    update_user_name,
    update_user_surname,
)
from whatsapp_utils._utils.twilio_messenger import send_notification_message

db_conn = SQLiteConnection(database="./database/test_db.db")
users_bp = Blueprint("users", __name__)

BASE_ROUTE = "/users"


@users_bp.route(BASE_ROUTE)
def user_info() -> str:
    """
    docstring
    """
    return "User Info API. This API endpoint is used for getting user information"


@users_bp.route(f"{BASE_ROUTE}/total_users", methods=["GET"])
def get_all_users() -> str:
    """
    This endpoint returns the number of users in the database.
    """
    try:
        user_count = get_total_number_of_users()
        msg = f"The total number of users registered and participating in the stokvel system are {user_count}"
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_all_users.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/view_account_details", methods=["POST"])
def get_account_details_endpoint() -> str:
    """
    This endpoint returns account details of a user based on their phone number.
    The phone number should be provided as a query parameter.
    """
    phone_number = request.json.get(
        "user_number"
    )  # Get the phone number from the query parameters

    if not phone_number:
        return (
            jsonify({"error": "Phone number is required."}),
            400,
        )  # Return an error if no phone number is provided

    try:
        user_details = get_account_details(
            phone_number
        )  # Call the function and store the result

        if user_details:
            # Prepare the notification message
            notification_message = (
                f"Welcome {user_details['u.user_name']} {user_details['u.user_surname']}!\n\n"
                f"Your user ID: {user_details['u.user_id']}\n"
                f"Your wallet ID: {user_details['uw.user_wallet']}\n"
                f"Your wallet balance: {user_details['uw.UserBalance']}\n\n"
            )

            # Send the notification message to the user via WhatsApp
            send_notification_message(
                to=f"whatsapp:{user_details['u.user_number']}",
                body=notification_message,
            )

            # Return the user details along with the sent notification status
            return (
                jsonify(
                    {
                        "user_details": user_details,
                        "message": "Notification sent successfully!",
                        "notification_message": notification_message,
                    }
                ),
                200,
            )

        else:
            return (
                jsonify({"error": "User not found."}),
                404,
            )  # Return an error if user is not found
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_account_details_endpoint.__name__}: {e}")
        return jsonify({"error": msg}), 500  # Return internal server error


@users_bp.route(f"{BASE_ROUTE}/admin/update_username", methods=["POST"])
def update_user_name_endpoint():

    phone_number = request.json.get("user_number")
    new_name = request.args.get("user_input")

    # Call the function to update the user's name
    result = update_user_name(phone_number, new_name)

    if "No user found" in result:
        return (
            jsonify({"message": result}),
            404,
        )  # Return a 404 error if no user is found

    # Prepare the notification message
    notification_message = (
        f"Your name has been updated successfully to: {new_name}!\n"
        f"If you have any questions, feel free to reach out."
    )

    # Send the notification message to the user via WhatsApp
    send_notification_message(to=f"whatsapp:{phone_number}", body=notification_message)

    return jsonify({"message": result, "notification": notification_message}), 200


@users_bp.route(f"{BASE_ROUTE}/admin/update_usersurname", methods=["POST"])
def update_user_surname_endpoint():
    phone_number = request.json.get("user_number")
    new_surname = request.json.get("user_input")

    # Call the function to update the user's surname
    result = update_user_surname(phone_number, new_surname)

    if "No user found" in result:
        return (
            jsonify({"message": result}),
            404,
        )  # Return a 404 error if no user is found

    # Prepare the notification message
    notification_message = (
        f"Your surname has been updated successfully to: {new_surname}!\n"
        f"If you have any questions, feel free to reach out."
    )

    # Send the notification message to the user via WhatsApp
    send_notification_message(to=f"whatsapp:{phone_number}", body=notification_message)

    return jsonify({"message": result, "notification": notification_message}), 200


@users_bp.route(f"{BASE_ROUTE}/fund_wallet", methods=["POST"])
def example_fund_wallet() -> str:
    """
    This is an example endpoint on how we would manage post requests from the state manager.
    """
    try:
        user_number = request.json.get("user_number")
        send_notification_message(
            to=user_number,
            body="Thank you, we are currently processing your request...",
        )
        ammount = request.json.get("user_input")
        msg = f"Your wallet has been funded with R{ammount}."
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {example_fund_wallet.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/update_user", methods=["GET"])
def approval_update_login() -> str:
    """
    docstrings
    """
    return render_template("update_user_login.html")


@users_bp.route(f"{BASE_ROUTE}/update_user/update", methods=["POST"])
def update_user_details() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        requesting_number = requesting_number = request.form.get(
            "requesting_number"
        ).lstrip("0")
        print("req no " + requesting_number)
        user_id = find_user_by_number(requesting_number)
        applications = get_all_applications(user_id=user_id)
        print(applications)

        return render_template("update_user.html", requesting_number=requesting_number)

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("users.failed_user_update"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("users.failed_user_update"))


@users_bp.route(f"{BASE_ROUTE}/update_user/success_user_update")
def success_user_update() -> str:
    """
    docstrings
    """
    action = "Profile Update"
    success_message = "Update to profile completed"
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    return render_template(
        "action_success_template.html",
        action=action,
        success_message=success_message,
        success_next_step_message=success_next_step_message,
    )


@users_bp.route(f"{BASE_ROUTE}/update_user/failed_user_update")
def failed_user_update() -> str:
    """
    docstring
    """
    action = "User update"
    failed_message = "We could not update your profile. Please try again."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please go back and try again."  # Define a better message here - depending on what needs to happen next

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )
