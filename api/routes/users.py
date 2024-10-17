from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection
from database.stokvel_queries.queries import (
    get_all_applications,
    get_stokvel_id_by_name,
    get_user_deposits_and_payouts_per_stokvel,
)
from database.user_queries.queries import (
    find_user_by_number,
    get_account_details,
    get_total_number_of_users,
    get_user_interest,
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
    User Info API
    Provides general information about the user API endpoints.
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns a message about the user API.
        schema:
          type: string
          example: "User Info API. This API endpoint is used for getting user information."
    """
    return "User Info API. This API endpoint is used for getting user information"


@users_bp.route(f"{BASE_ROUTE}/total_users", methods=["GET"])
def get_all_users() -> str:
    """
    Get Total Number of Users
    Retrieves the total count of users in the system.
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns the total number of users.
        schema:
          type: string
          example: "The total number of users registered and participating in the stokvel system are 150"
      500:
        description: Internal server error. An error occurred while fetching user count.
        schema:
          type: string
          example: "There was an error performing that action, please try the action again."
    """
    try:
        user_count = get_total_number_of_users()
        msg = f"The total number of users registered and participating in the stokvel system are {user_count}"
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_all_users.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/user_total_interest", methods=["POST"])
def user_total_interest() -> str:
    """
    Get User Total Interest
    Retrieves the total interest earned by a user in a specified stokvel.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_number
            - stokvel_selection
          properties:
            user_number:
              type: string
              description: The user's phone number.
              example: "+27821234567"
            stokvel_selection:
              type: string
              description: The name of the stokvel.
              example: "Community Savings Club"
    responses:
      200:
        description: Returns the total interest earned by the user in the stokvel.
        schema:
          type: string
          example: "Your total interest in this Stokvel is: R500"
      500:
        description: Internal server error. An error occurred while fetching interest data.
        schema:
          type: string
          example: "There was an error performing that action, please try the action again."
    """
    phone_number = request.json.get(
        "user_number"
    )  # Get the phone number from the query parameters
    stokvel_name = request.json.get(
        "stokvel_selection"
    )  # Get the stokvel name from query parameters

    try:
        # get stokvel_id an user_id
        stokvel_id = get_stokvel_id_by_name(stokvel_name)
        user_id = find_user_by_number(phone_number)
        # get total interest for the user relating to the selected stokvel
        interest = get_user_interest(user_id, stokvel_id)
        msg = f"Your total interest in this Stokvel is: R{interest}"
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_all_users.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/view_account_details", methods=["POST"])
def get_account_details_endpoint() -> str:
    """
    View User Account Details
    Retrieves account details of a user based on their phone number.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_number
          properties:
            user_number:
              type: string
              description: The user's phone number.
              example: "+27821234567"
    responses:
      200:
        description: Returns account details of the user.
        schema:
          type: string
          example: "Welcome John Doe! Your user ID: 1234, Wallet ID: abc123, Balance: R500."
      500:
        description: Internal server error. An error occurred while retrieving account details.
        schema:
          type: string
          example: "There was an error performing that action, please try the action again."
    """
    phone_number = request.json.get(
        "user_number"
    )  # Get the phone number from the query parameters

    try:
        user_details = get_account_details(
            phone_number
        )  # Call the function and store the result

        # Prepare the notification message
        notification_message = (
            f"Welcome {user_details['u.user_name']} {user_details['u.user_surname']}!\n\n"
            f"Your user ID: {user_details['u.user_id']}\n"
            f"Your wallet ID: {user_details['uw.user_wallet']}\n"
            f"Your wallet balance: {user_details['uw.UserBalance']}\n\n"
        )

        return notification_message

    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_account_details_endpoint.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/admin/update_username", methods=["POST"])
def update_user_name_endpoint():
    """
    Update User Name
    Updates the user's name based on their phone number.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_number
            - user_input
          properties:
            user_number:
              type: string
              description: The user's phone number.
              example: "+27821234567"
            user_input:
              type: string
              description: The new name to update for the user.
              example: "John"
    responses:
      200:
        description: Successfully updated the user's name.
        schema:
          type: string
          example: "Your name has been updated successfully to: John!"
      500:
        description: Internal server error. An error occurred while updating the user's name.
        schema:
          type: string
          example: "There was an error performing that action, please try the action again."
    """

    phone_number = request.json.get("user_number")
    new_name = request.json.get("user_input")

    # Call the function to update the user's name
    try:
        update_user_name(phone_number, new_name)

        # Prepare the notification message
        notification_message = (
            f"Your name has been updated successfully to: {new_name}!"
        )

        return notification_message
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {update_user_name_endpoint.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/admin/update_usersurname", methods=["POST"])
def update_user_surname_endpoint():
    """
    Update User Surname
    Updates the user's surname based on their phone number.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_number
            - user_input
          properties:
            user_number:
              type: string
              description: The user's phone number.
              example: "+27821234567"
            user_input:
              type: string
              description: The new surname to update for the user.
              example: "Doe"
    responses:
      200:
        description: Successfully updated the user's surname.
        schema:
          type: string
          example: "Your surname has been updated successfully to: Doe!"
      500:
        description: Internal server error. An error occurred while updating the user's surname.
        schema:
          type: string
          example: "There was an error performing that action, please try the action again."
    """
    phone_number = request.json.get("user_number")
    new_surname = request.json.get("user_input")

    # Call the function to update the user's surname
    try:
        update_user_surname(phone_number, new_surname)

        # Prepare the notification message
        notification_message = (
            f"Your surname has been updated successfully to: {new_surname}!"
        )

        return notification_message
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {update_user_surname_endpoint.__name__}: {e}")
        return msg


@users_bp.route(f"{BASE_ROUTE}/update_user", methods=["GET"])
def approval_update_login() -> str:
    """
    Update User Login
    Renders a login page for users who wish to update their profile details.
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns the login page for user profile update.
        content:
          text/html:
            example: "<html>...</html>"
    """
    return render_template("update_user_login.html")


@users_bp.route(f"{BASE_ROUTE}/update_user/update", methods=["POST"])
def update_user_details() -> Response:
    """
    Update User Details
    Processes the request to update user details based on their login and provided information.
    ---
    tags:
      - Users
    parameters:
      - in: formData
        name: requesting_number
        type: string
        required: true
        description: The phone number of the user requesting an update.
        example: "+27821234567"
    responses:
      200:
        description: Successfully renders the user update page with the requesting user's details.
        content:
          text/html:
            example: "<html>...</html>"
      302:
        description: Redirects to the failed user update page in case of errors.
        content:
          text/html:
            example: "<html>...</html>"
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
    Success User Update
    Displays a success message after a user successfully updates their profile.
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns the success page indicating the user update was successful.
        content:
          text/html:
            example: "<html>Profile Update: Update to profile completed. Please navigate back to WhatsApp for further functions.</html>"
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
    Failed User Update
    Displays a message if the user's profile update fails.
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns a failure page indicating the user update was unsuccessful.
        content:
          text/html:
            example: "<html>User update: We could not update your profile. Please try again. Please go back and try again.</html>"
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
