from flask import Blueprint, jsonify
from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.user_queries.queries import get_total_number_of_users

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
