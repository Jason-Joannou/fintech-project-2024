from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import get_all_stokvels, find_user_by_number, insert_stokvel_member


join_stokvel_bp = Blueprint("join_stokvel", __name__)

BASE_ROUTE = "/join_stokvel"
        
@join_stokvel_bp.route(BASE_ROUTE)
def join_stokvel() -> str:
    """
    docstrings
    """
    return render_template("stokvel_search.html")

@join_stokvel_bp.route(f"{BASE_ROUTE}/stokvels", methods=["POST"])
def onboard_stokvel() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        user_number = 879856523,
        user_id = find_user_by_number(user_number)

        insert_stokvel_member(
            stokvel_id=10000,
            user_id=user_id,
        )
        # Possibly handle adding the creator as a member automatically?

        # Prepare the notification message
        notification_message = (
            f"Congratulations you have successfully joined the selected stokvel.\n\n"
            # f"Your Stokvel ID: {stokvel_data.stokvel_id}\n"
            # # f"ILP Wallet: ILP_TEST\n"
            # # f"MOMO Wallet: MOMO_TEST\n"
            # f"Total Members: {stokvel_data.total_members}\n"
            # f"Minimum Contribution Amount: {stokvel_data.min_contributing_amount}\n\n"
            f"Thank you for joining a Stokvel with us!"
        )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{user_data.cellphone_number}", body=notification_message
        # )
        return redirect(url_for("join_stokvel.success_stokvel_join"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("join_stokvel.failed_stokvel_join"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("join_stokvel.failed_stokvel_join"))

@join_stokvel_bp.route("/success_stokvel_join")
def success_stokvel_join() -> str:
    """
    docstrings
    """
    return render_template("join_success.html")

@join_stokvel_bp.route("/failed_stokvel_join")
def failed_stokvel_join() -> str:
    """
    docstring
    """
    return render_template("join_failed.html")