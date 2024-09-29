from flask import Blueprint, request

from database.sqlite_connection import SQLiteConnection
from database.user_queries.queries import get_total_number_of_users
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
