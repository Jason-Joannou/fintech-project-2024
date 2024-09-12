from flask import Blueprint

stokvel_info_bp = Blueprint("stokvel_info", __name__)

base_route = "/stokvel_info"


@stokvel_info_bp.route(base_route)
def stokvel_info():
    return "Stokvel Info API. This API endpoint is used for getting stokvel information"