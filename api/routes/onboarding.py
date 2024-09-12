from flask import Blueprint

onboarding_bp = Blueprint("onboarding", __name__)

BASE_ROUTE = "/onboard"


@onboarding_bp.route(BASE_ROUTE)
def onboarding():
    """
    docstring
    """
    return "Onboarding API. This API endpoint is used for onboarding users and stokvels ( on creation )"

@onboarding_bp.route(f"{BASE_ROUTE}/users", methods=['POST'])
def onboard_user():
    """
    docstring
    """
    return "Complete Onboarding endpoint"

@onboarding_bp.route(f"{BASE_ROUTE}/stokvels", methods=['POST'])
def onboard_stokvel():
    """
    docstring
    """
    return "Complete Onboarding endpoint"
