from flask import Blueprint

stokvel_info_bp = Blueprint("stokvel_info", __name__)

BASE_ROUTE = "/stokvel_info"


@stokvel_info_bp.route(BASE_ROUTE)
def stokvel_info():
    """
    docstring
    """
    return "Stokvel Info API. This API endpoint is used for getting stokvel information"
