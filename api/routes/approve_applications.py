from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for, make_response
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number
from database.stokvel_queries import get_all_applications, update_application_status, insert_stokvel_member, update_stokvel_members_count

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
        # print('req no ' + requesting_number)
        admin_id = find_user_by_number(requesting_number.lstrip('0'))
        applications = get_all_applications(user_id=admin_id)
        # print(applications)
        return redirect(url_for('approve_stokvel.display_applications', admin_id=admin_id, requesting_number=requesting_number, applications=applications))

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

    requesting_number = request.form.get('requesting_number')  # Get from form
    admin_id = request.form.get('admin_id')

    if action == 'approve':
        # print(application_id, ' Approved')
        update_application_status(application_id, 'Approved')
        insert_stokvel_member(application_stokvel_id, application_joiner_id)
        update_stokvel_members_count(application_stokvel_id)

    elif action == 'decline':
        # print(application_id, ' Declined')
        update_application_status(application_id, 'Declined')

    # Redirect to a route that fetches the latest applications with the requesting_number
    return redirect(url_for('approve_stokvel.display_applications', admin_id=admin_id, requesting_number=requesting_number))

@approve_stokvel_bp.route(f"{BASE_ROUTE}/applications", methods=["GET"])
def display_applications():
    admin_id = request.args.get('admin_id')  # Get admin_id from query parameters
    requesting_number = request.args.get('requesting_number')  # Get requesting_number from query parameters

    applications = get_all_applications(user_id=admin_id)

    response = make_response(render_template("approve_applications.html", requesting_number=requesting_number, admin_id=admin_id, applications=applications))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

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