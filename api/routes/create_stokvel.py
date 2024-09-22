from flask import Blueprint

create_stokvel_bp = Blueprint("create_stokvel", __name__)

BASE_ROUTE = "/create_stokvel"


@create_stokvel_bp.route(BASE_ROUTE)
def create_stokvel() -> str:
    """
    docstrings
    """
    return "Join Stokvel API. This API endpoint is used for joining a stokvel"
