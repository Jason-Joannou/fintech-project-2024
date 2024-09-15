from flask import Blueprint, redirect, render_template, request, url_for

onboarding_bp = Blueprint("onboarding", __name__)

BASE_ROUTE = "/onboard"


@onboarding_bp.route(BASE_ROUTE)
def onboarding():
    """
    docstring
    """
    return render_template("onboarding_template.html")


@onboarding_bp.route(f"{BASE_ROUTE}/users", methods=["POST"])
def onboard_user():
    """
    docstring
    """

    name = request.form["name"]
    surname = request.form["surname"]
    cell_number = request.form["cellphone_number"]
    id_number = request.form["id_number"]

    print(name ,  ' ', surname,' ', cell_number,' ', id_number)


    return redirect(url_for('onboarding.success_user_creation'))


@onboarding_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel():
    """
    docstring
    """
    return redirect(url_for(f'{BASE_ROUTE.removeprefix("/")}.success_stockvel_creation'))


@onboarding_bp.route("/success_user_creation")
def success_user_creation():
    """
    docstring
    """
    return render_template("user_onboarding_success.html")


@onboarding_bp.route("/success_stockvel_creation")
def success_stockvel_creation():
    """
    docstring
    """
    return "Stockvel created successfully!"
