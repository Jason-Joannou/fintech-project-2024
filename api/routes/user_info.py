from flask import Blueprint

user_info_bp = Blueprint("user_info", __name__)

base_route = "/user_info"


@user_info_bp.route(base_route)
def user_info():
    return "User Info API. This API endpoint is used for getting user information"


@user_info_bp.route(f"{base_route}/all_users", methods=["POST"])
def get_all_users():
    return "Get all users API. This API endpoint is used for getting all users"