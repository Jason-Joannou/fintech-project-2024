from flask import Blueprint

join_stokvel_bp = Blueprint("join_stokvel", __name__)

BASE_ROUTE = "/join_stokvel"


@join_stokvel_bp.route(BASE_ROUTE)
def join_stokvel() -> str:
    """
    docstrings
    """
    return "Join Stokvel API. This API endpoint is used for joining a stokvel"
