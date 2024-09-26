from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number
from database.stokvel_queries import get_all_stokvels, insert_stokvel_join_application, get_stokvel_id_by_name, get_admin_by_stokvel

from api.schemas.onboarding import JoinStokvelSchema


join_stokvel_bp = Blueprint("join_stokvel", __name__)

BASE_ROUTE = "/join_stokvel"
        
@join_stokvel_bp.route(BASE_ROUTE)
def join_stokvel() -> str:
    """
    docstrings
    """

    stokvel_list = get_all_stokvels()

    return render_template("stokvel_search.html", stokvel_list=stokvel_list)

@join_stokvel_bp.route(f"{BASE_ROUTE}/apply_to_join", methods=["POST"])
def apply_to_join_stokvel() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:

        joiner_data = JoinStokvelSchema(
            **request.form.to_dict()
        )  

        user_id = find_user_by_number(joiner_data.requesting_number)

        # Add to application


        # Add the below to the database after authorizing the join
        # insert_stokvel_member(
        #     stokvel_id=joiner_data.stokvel_id,
        #     user_id=user_id,
        # )

        # update_stokvel_members_count(
        #     stokvel_id=joiner_data.stokvel_id
        # )

        print("testing")

        stokvel_id = get_stokvel_id_by_name(joiner_data.stokvel_name)
        stokvel_admin_number = get_admin_by_stokvel(stokvel_id=stokvel_id)

        # print(str(stokvel_id) + " test " + stokvel_admin_number)


        insert_stokvel_join_application(stokvel_id=stokvel_id, user_id=user_id)



        # Prepare the notification message
        joiner_notification_message = (
            f"You have applied to join the {joiner_data.stokvel_name}.\n\n"
            f"Application has been sent to the admin.\n"
            # # f"ILP Wallet: ILP_TEST\n"
            # # f"MOMO Wallet: MOMO_TEST\n"
            # f"Total Members: {stokvel_data.total_members}\n"
            # f"Minimum Contribution Amount: {stokvel_data.min_contributing_amount}\n\n"
            f"Thank you for applying to join!"
        )

        admin_notification_message = (
            f"A user has applied to join your stokvel: {joiner_data.stokvel_name}.\n\n"
            f"Please authorize their application.\n"
            # # f"ILP Wallet: ILP_TEST\n"
            # # f"MOMO Wallet: MOMO_TEST\n"
            # f"Total Members: {stokvel_data.total_members}\n"
            # f"Minimum Contribution Amount: {stokvel_data.min_contributing_amount}\n\n"
            f"Thank you!"
        )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{user_data.cellphone_number}", body=notification_message
        # )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{stokvel_admin_number}", body=notification_message
        # )
        return redirect(url_for("join_stokvel.success_stokvel_join_application"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("join_stokvel.failed_stokvel_join_application"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("join_stokvel.failed_stokvel_join_application"))

@join_stokvel_bp.route("/success_stokvel_join")
def success_stokvel_join_application() -> str:
    """
    docstrings
    """
    action = "Application"
    success_message = "Application to join selected stokvel has been sent."
    success_next_step_message = "Please navigate back to WhatsApp for further functions."


    return render_template("action_success_template.html", 
                           action = action,
                           success_message = success_message,
                           success_next_step_message = success_next_step_message)

@join_stokvel_bp.route("/failed_stokvel_join")
def failed_stokvel_join_application() -> str:
    """
    docstring
    """
    action = "Application"
    failed_message = "We could not process your application."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)