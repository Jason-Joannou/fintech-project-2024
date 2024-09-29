from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database.queries import find_user_by_number2
from database.stokvel_queries import get_all_applications, update_application_status, insert_stokvel_member, update_stokvel_members_count

# from api.schemas.onboarding import JoinStokvelSchema


update_user_details_bp = Blueprint("update_user_details", __name__)

BASE_ROUTE = "/update_user"
        
@update_user_details_bp.route(BASE_ROUTE)
def approval_update_login() -> str:
    """
    docstrings
    """
    return render_template("update_user_login.html")

@update_user_details_bp.route(f"{BASE_ROUTE}/update", methods=["POST"])
def update_user_details() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        requesting_number = requesting_number = request.form.get("requesting_number").lstrip('0')
        print('req no ' + requesting_number)
        user_id = find_user_by_number2(requesting_number)
        applications = get_all_applications(user_id=user_id)
        print(applications)

        return render_template("update_user.html", requesting_number = requesting_number)

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("update_user_details.failed_user_update"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("update_user_details.failed_user_update"))

# @update_user_details_bp.route(f"{BASE_ROUTE}/process_update", methods=["POST"])
# def process_update():
#     application_id = request.form.get('application_id')
#     application_stokvel_id = request.form.get('stokvel_id')
#     print('stokvelid - ', application_stokvel_id)
#     application_joiner_id = request.form.get('user_id')
#     print('stokvelid - ', application_joiner_id)
#     action = request.form.get('action')


#     if action == 'approve':
#         print(application_id, ' Approved')
#         update_application_status(application_id, 'Approved')

#         insert_stokvel_member(
#             application_stokvel_id,
#             application_joiner_id
#         )

#         update_stokvel_members_count(
#             application_stokvel_id
#         )
        
#         #send approved message to user

#     elif action == 'decline':
#         # Logic to decline the application
#         print(application_id, ' Declined')
#         update_application_status(application_id, 'Declined')

#         #send declined message to user


    
#     user_id = request.form.get('user_id')
#     requesting_number = request.form.get('requesting_id')
#     applications = get_all_applications(user_id=user_id)

#     return render_template("approve_applications.html", requesting_number = requesting_number, user_id=user_id, applications=applications)


@update_user_details_bp.route("/success_user_update")
def success_user_update() -> str:
    """
    docstrings
    """
    action = "Profile Update"
    success_message = "Update to profile completed"
    success_next_step_message = "Please navigate back to WhatsApp for further functions."


    return render_template("action_success_template.html", 
                           action = action,
                           success_message = success_message,
                           success_next_step_message = success_next_step_message)

@update_user_details_bp.route("/failed_user_update")
def failed_user_update() -> str:
    """
    docstring
    """
    action = "User update"
    failed_message = "We could not update your profile. Please try again."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please go back and try again."  # Define a better message here - depending on what needs to happen next


    return render_template("action_failed_template.html", 
                           action = action,
                           failed_message = failed_message,
                           failed_next_step_message = failed_next_step_message)