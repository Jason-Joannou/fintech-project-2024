from flask import Blueprint

users_bp = Blueprint("users", __name__)

BASE_ROUTE = "/users"


@users_bp.route(BASE_ROUTE)
def user_info() -> str:
    """
    docstring
    """
    return "User Info API. This API endpoint is used for getting user information"


@users_bp.route(f"{BASE_ROUTE}/all_users", methods=["POST"])
def get_all_users() -> str:
    """
    docstring
    """
    return "Get all users API. This API endpoint is used for getting all users"
