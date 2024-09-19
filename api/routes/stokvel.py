from flask import Blueprint

join_stokvel_bp = Blueprint("stokvels", __name__)

BASE_ROUTE = "/stokvels"


@join_stokvel_bp.route(BASE_ROUTE)
def stokvel() -> str:
    """
    docstrings
    """
    return "Stokvel API. This API endpoint for all things stokvel related!"
