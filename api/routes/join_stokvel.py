from flask import Blueprint

join_stokvel_bp = Blueprint("join_stokvel", __name__)

base_route = "/join_stokvel"


@join_stokvel_bp.route(base_route)
def join_stokvel():
    return "Join Stokvel API. This API endpoint is used for joining a stokvel"