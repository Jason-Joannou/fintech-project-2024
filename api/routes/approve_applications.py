from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number
from database.stokvel_queries import get_all_applications, update_application_status, insert_stokvel_member, update_stokvel_members_count

# from api.schemas.onboarding import JoinStokvelSchema


approve_stokvel_bp = Blueprint("approve_stokvel", __name__)

BASE_ROUTE = "/approvals"
        
@approve_stokvel_bp.route(BASE_ROUTE)
def approval_login() -> str:
    """
    docstrings
    """
    return render_template("approval_login.html")

@approve_stokvel_bp.route(f"{BASE_ROUTE}/manage_approvals", methods=["POST"])
def approve_stokvels() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:

        requesting_number = request.form.get("requesting_number")
        print('req no ' + requesting_number)
        admin_id = find_user_by_number(requesting_number.lstrip('0'))
        applications = get_all_applications(user_id=admin_id)
        print(applications)
        return render_template("approve_applications.html", requesting_number = requesting_number, admin_id=admin_id, applications=applications)

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("approve_stokvel.failed_approval_login"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("approve_stokvel.failed_approval_login"))

@approve_stokvel_bp.route(f"{BASE_ROUTE}/process_applications", methods=["POST"])
def process_application():
    application_id = request.form.get('application_id')
    application_stokvel_id = request.form.get('stokvel_id')
    application_joiner_id = request.form.get('user_id')
    action = request.form.get('action')


    if action == 'approve':
        print(application_id, ' Approved')
        
        update_application_status(application_id, 'Approved')

        insert_stokvel_member(
            application_stokvel_id,
            application_joiner_id
        )

        update_stokvel_members_count(
            application_stokvel_id
        )
        # user_id = request.form.get('user_id') #this needs to be the admin id, not the applicant id
        requesting_number = request.form.get('requesting_number')
        admin_id = request.form.get('admin_id')
        applications = get_all_applications(user_id=admin_id)

        print(admin_id, ' ', requesting_number, ' ', applications)
        #send approved message to user
        return render_template("approve_applications.html", requesting_number = requesting_number, admin_id=admin_id, applications=applications)


    elif action == 'decline':
        # Logic to decline the application
        print(application_id, ' Declined')
        
        update_application_status(application_id, 'Declined')

        requesting_number = request.form.get('requesting_number')
        admin_id = request.form.get('admin_id')
        applications = get_all_applications(user_id=admin_id)

        print(admin_id, ' ', requesting_number, ' ', applications)

        return render_template("approve_applications.html", requesting_number = requesting_number, admin_id=admin_id, applications=applications)


        #send declined message to user

    # user_id = request.form.get('user_id')
    # requesting_number = request.form.get('requesting_number')
    # applications = get_all_applications(user_id=user_id)



# @approve_stokvel_bp.route("/success_approval_login")
# def success_stokvel_join_application() -> str:
#     """
#     docstrings
#     """
#     action = "Login"
#     success_message = "Application to join selected stokvel has been sent."
#     success_next_step_message = "Please navigate back to WhatsApp for further functions."


#     return render_template("action_success_template.html", 
#                            action = action,
#                            success_message = success_message,
#                            success_next_step_message = success_next_step_message)

@approve_stokvel_bp.route("/failed_approval_login")
def failed_approval_login() -> str:
    """
    docstring
    """
    action = "Approval Login"
    failed_message = "We could not process your login."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please go back and try again."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)