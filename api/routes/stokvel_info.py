from flask import Blueprint, request, jsonify

user_info_bp = Blueprint("stokvel_info", __name__)

base_route = "/stokvel_info"


@user_info_bp.route(base_route)
def stokvel_info():
    return "Stokvel Info API. This API endpoint is used for getting stokvel information"