from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection
from database.stokvel_queries.queries import get_all_applications
from database.user_queries.queries import find_user_by_number, get_total_number_of_users, get_user_interest
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

@users_bp.route(f"{BASE_ROUTE}/user_total_interest", methods=["POST"])
def user_total_interest() -> float:
    """
    This endpoint returns the total for a user in a stokvel in the savings period.
    """
    try:
        interest = get_user_interest()
        msg = f"Your total interest in this Stokvel is: R{interest}"
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_all_users.__name__}: {e}")
        return msg
    
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
