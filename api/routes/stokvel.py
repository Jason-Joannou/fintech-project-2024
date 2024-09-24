from flask import Blueprint

stokvel_bp = Blueprint("stokvels", __name__)

BASE_ROUTE = "/stokvels"


@stokvel_bp.route(BASE_ROUTE)
def stokvel() -> str:
    """
    docstrings
    """
    return "Stokvel API. This API endpoint for all things stokvel related!"
