from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number
from database.stokvel_queries import get_all_stokvels, insert_stokvel_join_application, get_stokvel_id_by_name, get_admin_by_stokvel, get_all_applications, update_application_status

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

        requesting_number = requesting_number = request.form.get("requesting_number").lstrip('0')
        print('req no ' + requesting_number)
        user_id = find_user_by_number(requesting_number)
        applications = get_all_applications(user_id=user_id)
        print(applications)
        return render_template("approve_applications.html", requesting_number = requesting_number, user_id=user_id, applications=applications)

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("approve_stokvel.failed_approval_login"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("approve_stokvel.failed_approval_login"))

@approve_stokvel_bp.route(f"{BASE_ROUTE}/process_applications", methods=["POST"])
def process_application():
    application_id = request.form.get('application_id')
    action = request.form.get('action')

    if action == 'approve':
        # Logic to approve the application
        print(application_id, ' Approved')
        update_application_status(application_id, 'Approved')
    elif action == 'decline':
        # Logic to decline the application
        print(application_id, ' Declined')
        update_application_status(application_id, 'Declined')


    
    user_id = request.form.get('user_id')
    requesting_number = request.form.get('requesting_id')
    applications = get_all_applications(user_id=user_id)

    return render_template("approve_applications.html", requesting_number = requesting_number, user_id=user_id, applications=applications)


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