from flask import (
    Blueprint,
    Response,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import SQLAlchemyError

import requests

from api.schemas.onboarding import JoinStokvelSchema, RegisterStokvelSchema
from database.stokvel_queries.queries import (
    check_application_pending_approved,
    get_admin_by_stokvel,
    get_all_applications,
    get_all_stokvels,
    get_stokvel_id_by_name,
    insert_admin,
    insert_stokvel,
    insert_stokvel_join_application,
    insert_stokvel_member,
    update_application_status,
    update_stokvel_members_count,
    get_iso_with_default_time,
    format_contribution_period_string,
    add_url_token,
    calculate_number_periods,
    double_number_periods_for_same_daterange
)

from database.user_queries.queries import (
    find_number_by_userid,
    find_user_by_number,
    get_linked_stokvels,
    find_wallet_by_userid
)

from database.contribution_payout_queries import (
    insert_member_contribution_parameters,
    insert_stokvel_payouts_parameters
)
from whatsapp_utils._utils.twilio_messenger import send_notification_message

stokvel_bp = Blueprint("stokvel", __name__)

BASE_ROUTE = "/stokvel"

node_server_initiate_grant = "http://localhost:3000/incoming-payment-setup"
node_server_initiate_stokvelpayout_grant = "http://localhost:3000/incoming-payment-setup-stokvel-payout"


@stokvel_bp.route(BASE_ROUTE)
def stokvel() -> str:
    """
    docstrings
    """
    return "Stokvel API. This API endpoint for all things stokvel related!"


@stokvel_bp.route(f"{BASE_ROUTE}/change_contribution", methods=["POST"])
def update_stokvel_contribution() -> str:
    """
    This is an example endpoint on how we would manage post requests from the state manager.
    """
    try:
        user_number = request.json.get("user_number")
        user_input = request.json.get("user_input")
        stokvel_name = request.json.get("stokvel_selection")
        send_notification_message(
            to=user_number,
            body="Thank you, we are currently processing your request...",
        )
        msg = f"You contribution amount has been succesfully updated to R{user_input} for {stokvel_name}."
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {update_stokvel_contribution.__name__}: {e}")
        return msg


@stokvel_bp.route(f"{BASE_ROUTE}/admin/change_stokvel_name", methods=["POST"])
def change_stokvel_name() -> str:
    """
    This is an example endpoint on how we would manage post requests from the state manager.
    """
    try:
        user_number = request.json.get("user_number")
        user_input = request.json.get("user_input")
        # stokvel_name = request.json.get("stokvel_selection")
        send_notification_message(
            to=user_number,
            body="Thank you, we are currently processing your request...",
        )
        msg = f"Your stokvel name has been succesfully updated to {user_input}."
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {update_stokvel_contribution.__name__}: {e}")
        return msg


@stokvel_bp.route(f"{BASE_ROUTE}/my_stokvels", methods=["POST"])
def my_stokvels_dynamic_state():
    """
    Create a dynamic state based on the user's linked stokvels for the MY_STOKVELS state.
    """
    user_number = request.json.get("user_number")

    # Retrieve the linked stokvels and admin status
    linked_accounts = get_linked_stokvels(user_number)

    # Initialize variables for the dynamic state
    valid_actions = []
    state_selection = {}
    current_stokvels = []

    # Loop through linked accounts and dynamically build the state
    for i, (stokvel_name, admin_ind) in enumerate(linked_accounts, 1):
        valid_actions.append(str(i))  # Action is the index as a string
        current_stokvels.append(stokvel_name)

        # Depending on admin status, select the appropriate next state
        if admin_ind == 1:
            state_selection[str(i)] = "stokvel_actions_admin"
        else:
            state_selection[str(i)] = "stokvel_actions_user"

    # Add the "back_state" as the last action
    last_action = len(linked_accounts) + 1
    valid_actions.append(str(last_action))
    state_selection[str(last_action)] = "back_state"

    # Create the message to display the available stokvels
    stokvel_names = [
        f"{i}. {stokvel_name}" for i, (stokvel_name, _) in enumerate(linked_accounts, 1)
    ]
    message = (
        "Please choose one of your stokvels:\n"
        + "\n".join(stokvel_names)
        + f"\n{last_action}. Back"
    )

    # Build the final state
    my_stokvels = {
        "tag": "my_stokvels",
        "message": message,
        "valid_actions": valid_actions,
        "state_selection": state_selection,
        "current_stokvels": current_stokvels,
    }

    return jsonify(my_stokvels)


@stokvel_bp.route(f"{BASE_ROUTE}/join_stokvel", methods=["GET"])
def join_stokvel() -> str:
    """
    docstrings
    """

    stokvel_list = get_all_stokvels()

    return render_template("stokvel_search.html", stokvel_list=stokvel_list)


@stokvel_bp.route(f"{BASE_ROUTE}/join_stokvel/apply_to_join", methods=["POST"])
def apply_to_join_stokvel() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:

        joiner_data = JoinStokvelSchema(**request.form.to_dict())

        user_id = find_user_by_number(joiner_data.requesting_number)

        stokvel_id = get_stokvel_id_by_name(joiner_data.stokvel_name)
        stokvel_admin_cell_number = get_admin_by_stokvel(stokvel_id=stokvel_id)
        user_contribution = joiner_data.user_contribution

        # stokvel_admin_cell_number = find_number_by_userid(user_id=stokvel_admin_number)

        print(
            stokvel_id,
            " user id applying",
            user_id,
            " admin number = ",
            stokvel_admin_cell_number,
        )

        if not check_application_pending_approved(user_id, stokvel_id):
            # check if a user is either already approved/inserted into stokvel or if they have already applied and applic is pending
            insert_stokvel_join_application(stokvel_id=stokvel_id, user_id=user_id, user_contribution = user_contribution)

        else:
            print("you have already applied to join this application")
            error_message = "You are already a member or \nyou have already applied to join this stokvel. Please apply to join another stokvel."
            return redirect(
                url_for(
                    "stokvel.failed_stokvel_join_application",
                    error_message=error_message,
                )
            )

        # Prepare the notification message
        joiner_notification_message = (
            f"You have applied to join the {joiner_data.stokvel_name}.\n\n"
            f"Application has been sent to the admin.\n"
            f"Thank you for applying to join!"
        )

        admin_notification_message = (
            f"A user has applied to join your stokvel: {joiner_data.stokvel_name}.\n\n"
            f"Please review their application.\n"
            f"Thank you!"
        )

        # Send the notification message
        send_notification_message(
            to=f"whatsapp:{joiner_data.requesting_number}",
            body=joiner_notification_message,
        )

        # Send the notification message
        send_notification_message(
            to=f"whatsapp:{stokvel_admin_cell_number}", body=admin_notification_message
        )
        return redirect(url_for("stokvel.success_stokvel_join_application"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("stokvel.failed_stokvel_join_application"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        error_string = str(e)

        if "'NoneType' object is not subscriptable" in str(error_string):
            error_message = (
                "This cellphone number does not exist in the system. Please try again."
            )
        else:
            error_message = "An unknown error occurred."
        return redirect(
            url_for(
                "stokvel.failed_stokvel_join_application",
                error_message=error_message,
            )
        )  # tis was changed


@stokvel_bp.route(f"{BASE_ROUTE}/join_stokvel/success_stokvel_join")
def success_stokvel_join_application() -> str:
    """
    docstrings
    """
    action = "Application"
    success_message = "Application to join selected stokvel has been sent."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    return render_template(
        "action_success_template.html",
        action=action,
        success_message=success_message,
        success_next_step_message=success_next_step_message,
    )


@stokvel_bp.route(f"{BASE_ROUTE}/join_stokvel/failed_stokvel_join")
def failed_stokvel_join_application() -> str:
    """
    docstring
    """
    action = "Application"
    if request.args.get("error_message"):
        error_message = request.args.get("error_message")
    else:
        error_message = "Application to join has failed. Please try again later."
    failed_message = error_message
    # Define a better message here - depending on what needs to happen next
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )


@stokvel_bp.route(f"{BASE_ROUTE}/create_stokvel", methods=["GET"])
def create_stokvel_base() -> str:
    """
    docstring
    """
    return render_template("stokvel_creation_template.html")


@stokvel_bp.route(f"{BASE_ROUTE}/create_stokvel/stokvels", methods=["POST"])
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
            total_contributions = 0,
            start_date=stokvel_data.start_date,
            end_date= stokvel_data.end_date,
            payout_frequency_duration=stokvel_data.payout_frequency_duration,
            contribution_period=stokvel_data.contribution_period,
            created_at = None,
            updated_at = None,
        )

        stokvel_data.stokvel_id = inserted_stokvel_id

        print('stokvel created id = ')
        print(stokvel_data.stokvel_id)

        print('Printing requseting number id = ')
        print(stokvel_data.requesting_number)

        user_id = find_user_by_number(stokvel_data.requesting_number)

    #region Commented out old inserts


        # add member - get whatsapp number
        # insert_stokvel_member(
        #     application_id=None,
        #     stokvel_id=inserted_stokvel_id,
        #     user_id = find_user_by_number(stokvel_data.requesting_number)
        # )

        # #update the number of contributors
        # update_stokvel_members_count(stokvel_id=inserted_stokvel_id)


        # # add admin - get whatsapp number
        # insert_admin(
        #     stokvel_id=inserted_stokvel_id,
        #     stokvel_name= stokvel_data.stokvel_name,
        #     user_id = find_user_by_number(stokvel_data.requesting_number),
        #     total_contributions=0,
        #     total_members=1
        # )
    #endregion


    #region USER CONTRIBUTION GRANT THINGS

        print(get_iso_with_default_time(stokvel_data.start_date), ' ', get_iso_with_default_time(stokvel_data.end_date))

        number_payout_periods_between_start_end_date = calculate_number_periods(stokvel_data.payout_frequency_duration, 
                                                                         start_date= stokvel_data.start_date, end_date= stokvel_data.end_date)
        
        number_contribution_periods_between_start_end_date = calculate_number_periods(stokvel_data.contribution_period, 
                                                                         start_date= stokvel_data.start_date, end_date= stokvel_data.end_date)

        print(number_payout_periods_between_start_end_date)
        print(number_contribution_periods_between_start_end_date)

        print("USER CONTRIBUTION GRANT FUNCTIONALITY")

        payload = {
            "value": str(int(stokvel_data.min_contributing_amount*100)), #multiply by 100 because the asset scale is 2?
            "stokvel_contributions_start_date": get_iso_with_default_time(stokvel_data.start_date),
            "walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "sender_walletAddressURL": find_wallet_by_userid( user_id= user_id),
            "payment_periods": number_contribution_periods_between_start_end_date, #how many contributions are going to be made
            "payment_period_length": format_contribution_period_string(stokvel_data.payout_frequency_duration),
            "number_of_periods":str(1)
        }

        print("REQUEST: ")
        print(payload)

        response = requests.post(node_server_initiate_grant, json=payload)

        print(response)

        print("RESPONSE: \n", response.json())
        print("REDIRECT USER FOR AUTH: ", response.json()['recurring_grant']['interact']['redirect'])

        initial_continue_uri_contribution = response.json()['continue_uri']
        initial_continue_token_contribution = response.json()['continue_token']['value']
        initial_payment_quote_contribution = response.json()['quote_id']
    
    #endregion

    #region WALLET PAYOUT GRANT THINGS


        payment_period_duration_converted, number_periods = double_number_periods_for_same_daterange(period=stokvel_data.payout_frequency_duration)

        payload_payout = {
            "value": str(int(1)), #create an initial payment of 1c
            "stokvel_contributions_start_date": get_iso_with_default_time(stokvel_data.start_date),
            "walletAddressURL": find_wallet_by_userid( user_id= user_id),
            "sender_walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "payment_periods": number_payout_periods_between_start_end_date*2, #how many contributions are going to be made
            "payment_period_length": payment_period_duration_converted,
            "number_of_periods": str(number_periods)
        }

        print("PAYOUT SET UP REQUEST: ")
        print(payload_payout)

        response_payout_grant = requests.post(node_server_initiate_stokvelpayout_grant, json=payload_payout)
        print(response_payout_grant)


        # quote_json = ""
        
        initial_continue_uri_stokvel = response_payout_grant.json()['continue_uri']
        initial_continue_token_stokvel = response_payout_grant.json()['continue_token']['value']
        initial_quote_stokvel = response_payout_grant.json()['quote_id']


        # # # update_token_things()


        # print("RESPONSE: \n", response.json())
        print("\n \n \nREDIRECT STOKVEL AGENT FOR AUTH: ", response_payout_grant.json()['recurring_grant']['interact']['redirect'])

        # #On grant accept, redirect to the logic to: add status active and forward date payments

    #endregion

    #region INSERTS USER IN TABLES
        # insert_stokvel_member(
        #     application_id=None,
        #     stokvel_id=inserted_stokvel_id,
        #     user_id = find_user_by_number(stokvel_data.requesting_number),
        #     user_contribution=stokvel_data.min_contributing_amount,
        #     user_token='initial_continue_token_contribution',
        #     user_url='initial_continue_uri_contribution',
        #     user_quote_id='initial_payment_quote_contribution',
        #     stokvel_quote_id='initial_quote_stokvel',
        #     stokvel_token='initial_continue_token_stokvel',
        #     stokvel_url='initial_continue_uri_stokvel'
        # )

        insert_stokvel_member(
            application_id=None,
            stokvel_id=inserted_stokvel_id,
            user_id = find_user_by_number(stokvel_data.requesting_number),
            user_contribution=stokvel_data.min_contributing_amount,
            user_token=initial_continue_token_contribution,
            user_url=initial_continue_uri_contribution,
            user_quote_id=initial_payment_quote_contribution,
            stokvel_quote_id=initial_quote_stokvel,
            stokvel_token=initial_continue_token_stokvel,
            stokvel_url=initial_continue_uri_stokvel,
            stokvel_initial_payment_needed = 1
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

        #generate contribution dates
        insert_member_contribution_parameters(
            stokvel_id=stokvel_data.stokvel_id,
            start_date= stokvel_data.start_date,
            payout_period=stokvel_data.contribution_period
        )


        #generate payouts
        insert_stokvel_payouts_parameters(
            stokvel_id=stokvel_data.stokvel_id,
            start_date=stokvel_data.start_date,
            payout_period=stokvel_data.payout_frequency_duration
        )

        #endregion


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

        # Send the notification message UNCOMMENT LATER!!
        # send_notification_message(
        #     to=f"whatsapp:{stokvel_data.requesting_number}", body=notification_message
        # )
        return redirect(url_for("stokvel.success_stokvel_creation"))

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("stokvel.failed_stokvel_creation"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        error_string = str(e)

        if "'NoneType' object is not subscriptable" in str(error_string):
            error_message = (
                "This cellphone number does not exist in the system. Please try again."
            )
        elif "STOKVELS.stokvel_name" in str(error_string):
            error_message = (
                "This stokvel already exists in the system. Please choose another name."
            )
        else:
            error_message = "An unknown error occurred."
        return redirect(
            url_for("stokvel.failed_stokvel_creation", error_message=error_message)
        )  # tis was changed


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_stokvel/success_stokvel_creation", methods=["GET"]
)
def success_stokvel_creation() -> str:
    """
    docstrings
    """
    action = "Stokvel Creation"
    success_message = "Stokvel created successfully."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    return render_template(
        "action_success_template.html",
        action=action,
        success_message=success_message,
        success_next_step_message=success_next_step_message,
    )


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_stokvel/failed_stokvel_creation", methods=["GET"]
)
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
    # Define a better message here - depending on what needs to happen next
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )


@stokvel_bp.route(f"{BASE_ROUTE}/approvals", methods=["GET"])
def approval_login() -> str:
    """
    docstrings
    """
    return render_template("approval_login.html")


@stokvel_bp.route(f"{BASE_ROUTE}/approvals/manage_approvals", methods=["POST"])
def approve_stokvels() -> Response:
    """
    Handles onboarding of a new user.
    """
    try:
        requesting_number = request.form.get("requesting_number")
        # print('req no ' + requesting_number)
        admin_id = find_user_by_number(requesting_number.lstrip("0"))
        applications = get_all_applications(user_id=admin_id)
        # print(applications)
        return redirect(
            url_for(
                "stokvel.display_applications",
                admin_id=admin_id,
                requesting_number=requesting_number,
                applications=applications,
            )
        )

    except SQLAlchemyError as sql_error:
        print(f"SQL Error occurred during insert operations: {sql_error}")
        return redirect(url_for("stokvel.failed_approval_login"))

    except Exception as e:
        print(f"General Error occurred during insert operations: {e}")
        return redirect(url_for("stokvel.failed_approval_login"))


@stokvel_bp.route(f"{BASE_ROUTE}/approvals/process_applications", methods=["POST"])
def process_application():
    """
    docstring
    """
    application_id = request.form.get("application_id")
    application_stokvel_id = request.form.get("stokvel_id")
    application_joiner_id = request.form.get("user_id")
    stokvel_name = request.form.get("stokvel_name")
    action = request.form.get("action")
    user_contribution = request.form.get("user_contribution")

    requesting_number = request.form.get(
        "requesting_number"
    )  # Get from form - this is the phone number of the admin that is processing the apps
    admin_id = request.form.get("admin_id")

    applicant_cell_number = find_number_by_userid(application_joiner_id)
    print("applicant cell number: ", applicant_cell_number)

    if action == "approve":
        # print(application_id, ' Approved')
        # update_application_status(application_id, 'Approved')
        try:
            declined_applications_list = insert_stokvel_member(
                application_id=application_id,
                stokvel_id=application_stokvel_id,
                user_id=application_joiner_id,
                user_contribution=user_contribution
            )
            update_stokvel_members_count(application_stokvel_id)

            if (
                declined_applications_list is not None
                and len(declined_applications_list) > 0
            ):
                error_message = "The stokvel is full. No new members can be added"

                # Prepare the notification message
                app_declined_notification_message = (
                    f"Application to join the stokvel: {stokvel_name}!\n\n"
                    f"Application declined.\n"
                    f"Please contact the admin or apply for another stokvel\n"
                )

                for number in declined_applications_list:
                    # Send the notification message
                    send_notification_message(
                        to=f"whatsapp:{number}", body=app_declined_notification_message
                    )

                return redirect(
                    url_for(
                        "stokvel.failed_approval_sv_full",
                        error_message=error_message,
                    )
                )

            # Prepare the notification message
            app_accepted_notification_message = (
                f"Welcome to the stokvel: {stokvel_name}!\n\n"
                f"Your application approved - please expect contribution authorization request shortly.\n"
            )

            # Send the notification message
            send_notification_message(
                to=f"whatsapp:{applicant_cell_number}",
                body=app_accepted_notification_message,
            )

        except Exception as e:
            print(f"General Error occurred during insert operations: {e}")
            error_string = str(e)
            if "stokvel_full" in str(error_string):
                error_message = "The stokvel is full. No new members can be added"
            else:
                error_message = "An unknown integrity error occurred."
            return redirect(
                url_for(
                    "stokvel.failed_approval_sv_full",
                    error_message=error_message,
                )
            )

    elif action == "decline":
        # print(application_id, ' Declined')
        update_application_status(application_id, "Declined")
        # send whatsapp to applicant

        # Prepare the notification message
        app_declined_notification_message = (
            f"Application to join the stokvel: {stokvel_name}!\n\n"
            f"Application declined.\n"
            f"Please contact the admin or apply for another stokvel\n"
        )

        # Send the notification message
        send_notification_message(
            to=f"whatsapp:{applicant_cell_number}",
            body=app_declined_notification_message,
        )

    # Redirect to a route that fetches the latest applications with the requesting_number
    return redirect(
        url_for(
            "stokvel.display_applications",
            admin_id=admin_id,
            requesting_number=requesting_number,
        )
    )


@stokvel_bp.route(f"{BASE_ROUTE}/approvals/applications", methods=["GET"])
def display_applications():
    """
    docstring
    """
    admin_id = request.args.get("admin_id")  # Get admin_id from query parameters
    requesting_number = request.args.get(
        "requesting_number"
    )  # Get requesting_number from query parameters

    applications = get_all_applications(user_id=admin_id)

    response = make_response(
        render_template(
            "approve_applications.html",
            requesting_number=requesting_number,
            admin_id=admin_id,
            applications=applications,
        )
    )
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, proxy-revalidate"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@stokvel_bp.route(f"{BASE_ROUTE}/approvals/failed_approval_login")
def failed_approval_login() -> str:
    """
    docstring
    """
    action = "Approval Login"
    failed_message = "We could not process your login."  # Define a better message here - depending on what went wrong
    failed_next_step_message = "Please go back and try again."  # Define a better message here - depending on what needs to happen next

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )


@stokvel_bp.route(f"{BASE_ROUTE}/approvals/failed_approval_sv_full")
def failed_approval_sv_full() -> str:
    """
    docstring
    """

    action = "Application Approval"
    if request.args.get("error_message"):
        error_message = request.args.get("error_message")
    else:
        error_message = "User onboarding failed. Please try again later."
    failed_message = error_message
    # Define a better message here - depending on what needs to happen next
    failed_next_step_message = "Please navigate back to WhatsApp for further functions."

    return render_template(
        "action_failed_template.html",
        action=action,
        failed_message=failed_message,
        failed_next_step_message=failed_next_step_message,
    )


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_stokvel/success_contribution_grant_confirmed", methods=["GET"]
)
def success_user_interactive_grant_accepted() -> str:
    """
    docstrings
    """
    action = "Stokvel contributions have been accepted"
    success_message = "Your contributions will be processed at the specifed periods."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    #add initial payment logic here

    return render_template(
        "action_success_template.html",
        action=action,
        success_message=success_message,
        success_next_step_message=success_next_step_message,
    )
