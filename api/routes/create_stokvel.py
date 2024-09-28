from flask import Blueprint, Response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from api.schemas.onboarding import RegisterStokvelSchema
from database.stokvel_queries import insert_stokvel, insert_stokvel_member, insert_admin, update_stokvel_members_count
from database.queries import find_user_by_number

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

        # Create a stokvel object
        
        inserted_stokvel_id = insert_stokvel(
            stokvel_id = None,
            stokvel_name = stokvel_data.stokvel_name, #unique constraint here
            ILP_wallet = "ILP_TEST",
            MOMO_wallet = "MOMO_TEST",
            total_members = stokvel_data.total_members,
            min_contributing_amount = stokvel_data.min_contributing_amount,
            max_number_of_contributors = stokvel_data.max_number_of_contributors,#stokvel_data.max_number_of_contributors,
            Total_contributions = 0,
            start_date=stokvel_data.start_date,
            end_date= stokvel_data.end_date,
            payout_frequency_int=stokvel_data.payout_frequency_int,
            payout_frequency_period=stokvel_data.payout_frequency_period,
            created_at = None,
            updated_at = None,
        )

        stokvel_data.stokvel_id = inserted_stokvel_id

        print('stokvel created id = ')
        print(stokvel_data.stokvel_id)

        print('Printing requseting number id = ')
        print(stokvel_data.requesting_number)

        user_id = find_user_by_number(stokvel_data.requesting_number)



        # add member - get whatsapp number
        insert_stokvel_member(
            application_id=None,
            stokvel_id=inserted_stokvel_id,
            user_id = find_user_by_number(stokvel_data.requesting_number)
        )

        #update the number of contributors
        update_stokvel_members_count(stokvel_id=inserted_stokvel_id)


        # add admin - get whatsapp number
        insert_admin(
            stokvel_id=inserted_stokvel_id,
            stokvel_name= stokvel_data.stokvel_name,
            user_id = find_user_by_number(stokvel_data.requesting_number),
            total_contributions=0,
            total_members=1
        )



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
        error_string = str(e)
        
        if "'NoneType' object is not subscriptable" in str(error_string):
            error_message = "This cellphone number does not exist in the system. Please try again."
        elif "STOKVELS.stokvel_name" in str(error_string):
            error_message = "This stokvel already exists in the system. Please choose another name."
        else:
            error_message = "An unknown error occurred."
        return redirect(url_for("create_stokvel.failed_stokvel_creation", error_message = error_message)) #tis was changed

@create_stokvel_bp.route("/success_stokvel_creation")
def success_stokvel_creation() -> str:
    """
    docstrings
    """
    action = "Stokvel Creation"
    success_message = "Stokvel created successfully."
    success_next_step_message = "Please navigate back to WhatsApp for further functions."


    return render_template("action_success_template.html", 
                           action = action,
                           success_message = success_message,
                           success_next_step_message = success_next_step_message)

@create_stokvel_bp.route("/failed_stokvel_creation")
def failed_stokvel_creation() -> str:
    """
    docstring
    """
    action = "Stokvel Registration"
    if request.args.get("error_message"):
        error_message = request.args.get("error_message")
    else:
        error_message = "Stokvel could not be registered. Please try again later."
    failed_message = error_message
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)
