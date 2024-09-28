from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for, make_response
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number, find_number_by_userid
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
    stokvel_name = request.form.get('stokvel_name')
    action = request.form.get('action')

    requesting_number = request.form.get('requesting_number')  # Get from form - this is the phone number of the admin that is processing the apps
    admin_id = request.form.get('admin_id')

    # applicant_cell_number = find_number_by_userid(application_joiner_id)

    if action == 'approve':
        # print(application_id, ' Approved')
        # update_application_status(application_id, 'Approved')
        try:
            declined_applications_list = insert_stokvel_member(application_id= application_id, stokvel_id=application_stokvel_id, user_id=application_joiner_id)
            update_stokvel_members_count(application_stokvel_id)

            if declined_applications_list is not None and len(declined_applications_list)>0:
                error_message = "The stokvel is full. No new members can be added"

                # Prepare the notification message
                app_declined_notification_message = (
                    f"Application to join the stokvel: {stokvel_name}!\n\n"
                    f"Application declined.\n"
                    f"Please contact the admin or apply for another stokvel\n"
                )

                for number in declined_applications_list:
                    pass
                    # Send the notification message
                    # send_notification_message(
                    #     to=f"whatsapp:{number}", body=app_declined_notification_message
                    # )

                return redirect(url_for("approve_stokvel.failed_approval_sv_full", error_message = error_message))
            
            
            else:
                # Prepare the notification message
                app_accepted_notification_message = (
                    f"Welcome to the stokvel: {stokvel_name}!\n\n"
                    f"Your application approved - please expect contribution authorization request shortly.\n"
                )

                # Send the notification message
                # send_notification_message(
                #     to=f"whatsapp:{applicant_cell_number}", body=app_accepted_notification_message
                # )
        
        except Exception as e:
            print(f"General Error occurred during insert operations: {e}")
            error_string = str(e)
            if "stokvel_full" in str(error_string):
                error_message = "The stokvel is full. No new members can be added"
            else:
                error_message = "An unknown integrity error occurred."
            return redirect(url_for("approve_stokvel.failed_approval_sv_full", error_message = error_message))

    elif action == 'decline':
        # print(application_id, ' Declined')
        update_application_status(application_id, 'Declined')
        # send whatsapp to applicant

        # Prepare the notification message
        app_declined_notification_message = (
            f"Application to join the stokvel: {stokvel_name}!\n\n"
            f"Application declined.\n"
            f"Please contact the admin or apply for another stokvel\n"
        )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{applicant_cell_number}", body=app_declined_notification_message
        # )


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


@approve_stokvel_bp.route("/failed_approval_sv_full")
def failed_approval_sv_full() -> str:
    """
    docstring
    """
    """
    docstring
    """

    action = "Application Approval"
    if request.args.get("error_message"):
        error_message = request.args.get("error_message")
    else:
        error_message = "User onboarding failed. Please try again later."
    failed_message = error_message
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)