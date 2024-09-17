from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import insert_user, insert_wallet
from utils.user import User
from utils.wallet import Wallet
from whatsapp_utils._utils.twilio_messenger import send_notification_message

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
    Handles onboarding of a new user.
    """
    try:
        name = request.form["name"]
        surname = request.form["surname"]
        cell_number = request.form["cellphone_number"]
        id_number = request.form["id_number"]

        user = User(
            name=name,
            surname=surname,
            cell_number=cell_number,
            id_number=id_number,
            wallet_id="",
        )
        wallet = Wallet(user.id_number, user_wallet="ILP_test_string", user_balance=100)

        insert_user(
            user_id=user.id_number,
            user_number=user.cell_number,
            user_surname=user.surname,
            user_name=user.name,
            ilp_wallet=wallet.id,
        )
        insert_wallet(
            user_id=user.id_number,
            user_wallet=wallet.id,
            userbalance=wallet.user_balance,
        )
        # Prepare the notification message
        notification_message = (
            f"Welcome {user.name} {user.surname}!\n\n"
            f"Your user ID: {user.id_number}\n"
            f"Your wallet ID: {wallet.id}\n"
            f"Your wallet balance: {wallet.user_balance}\n\n"
            f"Thank you for registering with us!"
        )

        # Send the notification message
        send_notification_message(
            to=f"whatsapp:{user.cell_number}", body=notification_message
        )
        return redirect(url_for("onboarding.success_user_creation"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("onboarding.failed_user_creation"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("onboarding.failed_user_creation"))


@onboarding_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel():
    """
    docstring
    """
    return redirect(
        url_for(f'{BASE_ROUTE.removeprefix("/")}.success_stockvel_creation')
    )


@onboarding_bp.route("/success_user_creation")
def success_user_creation():
    """
    docstring
    """
    return render_template("user_onboarding_success.html")


@onboarding_bp.route("/failed_user_creation")
def failed_user_creation():
    """
    docstring
    """
    return render_template("user_onboarding_failed.html")


@onboarding_bp.route("/success_stockvel_creation")
def success_stockvel_creation():
    """
    docstring
    """
    return "Stockvel created successfully!"
