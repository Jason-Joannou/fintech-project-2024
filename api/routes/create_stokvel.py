from flask import Blueprint, Response, redirect, render_template, request, url_for
# from sqlalchemy.exc import SQLAlchemyError

# from api.schemas.onboarding import OnboardUserSchema
# from database.queries import insert_user, insert_wallet

create_stokvel_bp = Blueprint("create_stokvel", __name__)

BASE_ROUTE = "/create_stokvel"


@create_stokvel_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel() -> Response:
    """
    docstring
    """
    return redirect(
        url_for(f'{BASE_ROUTE.removeprefix("/")}.success_stokvel_creation')
    )

@create_stokvel_bp.route("/success_stokvel_creation")
def success_stokvel_creation() -> str:
    """
    docstrings
    """
    return render_template("stokvel_success.html")

@create_stokvel_bp.route("/failed_stokvel_creation")
def failed_stokvel_creation() -> str:
    """
    docstring
    """
    return render_template("stokvel_failed.html")
