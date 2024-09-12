from flask import Blueprint

user_info_bp = Blueprint("user_info", __name__)

BASE_ROUTE = "/user_info"


@user_info_bp.route(BASE_ROUTE)
def user_info():
    """
    docstring
    """
    return "User Info API. This API endpoint is used for getting user information"


@user_info_bp.route(f"{BASE_ROUTE}/all_users", methods=["POST"])
def get_all_users():
    """
    docstring
    """
    return "Get all users API. This API endpoint is used for getting all users"