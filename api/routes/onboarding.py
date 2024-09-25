from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from api.schemas.onboarding import OnboardUserSchema
from database.queries import insert_user, insert_wallet
# from whatsapp_utils._utils.twilio_messenger import send_notification_message

onboarding_bp = Blueprint("onboarding", __name__)

BASE_ROUTE = "/onboard"


@onboarding_bp.route(BASE_ROUTE)
def onboarding() -> str:
    """
    docstring
    """
    return render_template("onboarding_template.html")


@onboarding_bp.route(f"{BASE_ROUTE}/users", methods=["POST"])
def onboard_user() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        user_data = OnboardUserSchema(
            **request.form.to_dict()
        )  # ** unpacks the dictionary

        #verify_wallet() <- send request to the wallet for verification

        insert_user(
            user_id=user_data.id_number,
            user_number=user_data.cellphone_number,
            user_surname=user_data.surname,
            user_name=user_data.name,
            ilp_wallet=user_data.wallet_id,
        )
        insert_wallet(
            user_id=user_data.id_number,
            user_wallet=user_data.wallet_id,
            user_balance=100, #how should we fund user wallets initially?
        )
        # Prepare the notification message
        notification_message = (
            f"Welcome {user_data.name} {user_data.surname}!\n\n"
            f"Your user ID: {user_data.id_number}\n"
            f"Your wallet ID: {user_data.wallet_id}\n"
            f"Your wallet balance: {100}\n\n"
            f"Thank you for registering with us!"
        )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{user_data.cellphone_number}", body=notification_message
        # )
        return redirect(url_for("onboarding.success_user_creation"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("onboarding.failed_user_creation"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("onboarding.failed_user_creation"))



@onboarding_bp.route("/success_user_creation")
def success_user_creation() -> str:
    action = "Onboarding"
    success_message = "User onboarding successful! You are ready to start using the application."
    success_next_step_message = "Please navigate back to WhatsApp for further functions."


    return render_template("action_success_template.html", 
                           action = action,
                           success_message = success_message,
                           success_next_step_message = success_next_step_message)


@onboarding_bp.route("/failed_user_creation")
def failed_user_creation() -> str:
    """
    docstring
    """

    action = "Onboarding"
    failed_message = "User onboarding failed. Please try again later."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)