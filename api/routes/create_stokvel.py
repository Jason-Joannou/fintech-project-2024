from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from api.schemas.onboarding import RegisterStokvelSchema
from database.queries import insert_stokvel

create_stokvel_bp = Blueprint("create_stokvel", __name__)

BASE_ROUTE = "/create_stokvel"


@create_stokvel_bp.route(BASE_ROUTE)
def create_stokvel_base() -> str:
    """
    docstring
    """
    return render_template("stokvel_creation_template.html")

@create_stokvel_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        stokvel_data = RegisterStokvelSchema(
            **request.form.to_dict()
        )  # ** unpacks the dictionary

        insert_stokvel(
            stokvel_id = None,
            stokvel_name = stokvel_data.stokvel_name, #unique constraint here
            ILP_wallet = "ILP_TEST",
            MOMO_wallet = "MOMO_TEST",
            total_members = stokvel_data.total_members,
            min_contributing_amount = stokvel_data.min_contributing_amount,
            max_number_of_contributors = stokvel_data.max_number_of_contributors,
            Total_contributions = 0,
            created_at = None,
            updated_at = None,
        )

        # Possibly handle adding the creator as a member automatically?

        # Prepare the notification message
        notification_message = (
            f"Congratulations {stokvel_data.stokvel_name} has been registered successfully!\n\n"
            f"Your Stokvel ID: {stokvel_data.stokvel_id}\n"
            # f"ILP Wallet: ILP_TEST\n"
            # f"MOMO Wallet: MOMO_TEST\n"
            f"Total Members: {stokvel_data.total_members}\n"
            f"Minimum Contribution Amount: {stokvel_data.min_contributing_amount}\n\n"
            f"Thank you for creating a Stokvel with us!"
        )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{user_data.cellphone_number}", body=notification_message
        # )
        return redirect(url_for("create_stokvel.success_stokvel_creation"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("create_stokvel.failed_stokvel_creation"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("create_stokvel.failed_stokvel_creation"))

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
