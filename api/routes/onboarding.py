from flask import Blueprint, request, jsonify

onboarding_bp = Blueprint("onboarding", __name__)

base_route = "/onboard"


@onboarding_bp.route(base_route)
def onboarding():
    return "Onboarding API. This API endpoint is used for onboarding users and stokvels ( on creation )"

@onboarding_bp.route(f"{base_route}/users", methods=['POST'])
def onboard_user():
    return "Complete Onboarding endpoint"

@onboarding_bp.route(f"{base_route}/stokvels", methods=['POST'])
def onboard_stokvel():
    return "Complete Onboarding endpoint"
