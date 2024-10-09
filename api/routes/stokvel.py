import requests
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

from api.schemas.onboarding import JoinStokvelSchema, RegisterStokvelSchema
from database.contribution_payout_queries import (
    insert_member_contribution_parameters,
    insert_stokvel_payouts_parameters,
    update_stokvel_token_uri,
)
from database.stokvel_queries.queries import (
    add_url_token,
    calculate_number_periods,
    check_application_pending_approved,
    double_number_periods_for_same_daterange,
    format_contribution_period_string,
    get_admin_by_stokvel,
    get_all_applications,
    get_all_stokvels,
    get_deposits_per_stokvel,
    get_iso_with_default_time,
    get_nr_of_active_users_per_stokvel,
    get_stokvel_constitution,
    get_stokvel_details,
    get_stokvel_id_by_name,
    get_stokvel_member_details,
    get_user_deposits_and_payouts_per_stokvel,
    insert_admin,
    insert_stokvel,
    insert_stokvel_join_application,
    insert_stokvel_member,
    update_adhoc_contribution_parms,
    update_application_status,
    update_max_nr_of_contributors,
    update_member_grantaccepted,
    update_stokvel_grantaccepted,
    update_stokvel_members_count,
    update_stokvel_name,
)
from database.user_queries.queries import (
    find_number_by_userid,
    find_user_by_number,
    find_wallet_by_userid,
    get_linked_stokvels,
    get_stokvel_monthly_interest,
)
from whatsapp_utils._utils.twilio_messenger import send_notification_message

stokvel_bp = Blueprint("stokvel", __name__)

BASE_ROUTE = "/stokvel"

node_server_initiate_grant = "http://localhost:3000/incoming-payment-setup"
node_server_initiate_stokvelpayout_grant = (
    "http://localhost:3000/incoming-payment-setup-stokvel-payout"
)

node_server_create_initial_payment = (
    "http://localhost:3000/create-initial-outgoing-payment"
)


@stokvel_bp.route(BASE_ROUTE)
def stokvel() -> str:
    """
    docstrings
    """
    return "Stokvel API. This API endpoint for all things stokvel related!"


@stokvel_bp.route(f"{BASE_ROUTE}/stokvel/stokvel_summary", methods=["POST"])
def get_user_total_deposit():
    """
    This endpoint returns the total deposits of a user for a given stokvel.
    The user's phone number and stokvel name should be provided as query parameters.
    """
    phone_number = request.json.get(
        "user_number"
    )  # Get the phone number from query parameters
    stokvel_name = request.json.get(
        "stokvel_selection"
    )  # Get the stokvel name from query parameters

    try:
        # Fetch total deposits for the user and stokvel
        result = get_user_deposits_and_payouts_per_stokvel(
            phone_number=phone_number, stokvel_name=stokvel_name
        )
        deposit_details = result["total_deposits"]
        total_deposit_details = result["total_payouts"]
        active_users_count = get_nr_of_active_users_per_stokvel(stokvel_name)

        if "error" in deposit_details:
            raise ValueError(deposit_details["error"])

        # Return an error if no data is found
        if "error" in active_users_count:
            raise ValueError(active_users_count["error"])

        # Prepare the notification message
        notification_message = (
            f"📊 Stokvel Summary\n\n"
            f"Stokvel Name: {total_deposit_details['stokvel_name']}\n"
            f"Total Deposits in Stokvel: R{total_deposit_details['total_deposits']:.2f}\n"
            f"Your Total Deposits: R{deposit_details['total_deposits']:.2f}\n"
            f"Number of Active Users in Stokvel: {active_users_count['nr_of_active_users']}\n\n"
            "Thank you for being a part of our community!\n"
        )

        # Return the deposit details along with the sent notification status
        return notification_message

    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_user_deposits_and_payouts_per_stokvel.__name__}: {e}")
        print(f"Error in {get_nr_of_active_users_per_stokvel.__name__}: {e}")
        print(f"Error in {get_deposits_per_stokvel.__name__}: {e}")
        return jsonify({"error": msg}), 500  # Return internal server error


@stokvel_bp.route(f"{BASE_ROUTE}/stokvel/view_constitution", methods=["POST"])
def get_stokvels_constitution_handler():
    """
    This endpoint returns the stokvels constitution
    """
    phone_number = request.json.get(
        "user_number"
    )  # Get the phone number from query parameters
    stokvel_name = request.json.get(
        "stokvel_selection"
    )  # Get the stokvel name from query parameters

    try:
        # Fetch total deposits for the user and stokvel
        stokvel_constitution = get_stokvel_constitution(phone_number, stokvel_name)

        if "error" in stokvel_constitution:
            raise ValueError(stokvel_constitution["error"])

        # Prepare the notification message
        notification_message = (
            f"Stokvel Constitution\n\n"
            f"Stokvel Name: {stokvel_constitution['stokvel_name']}\n"
            f"Minimum Contributing Amount for Stokvel: R{stokvel_constitution['minimum_contributing_amount']:.2f}\n"
            f"Maximum Number of Contributors: R{stokvel_constitution['max_number_of_contributors']:.2f}\n"
            f"Creation Date of Stokvel: {stokvel_constitution['creation_date']}\n\n"
            "Thank you for being a part of our community!\n"
        )

        # Return the deposit details along with the sent notification status
        return notification_message

    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {get_stokvel_constitution.__name__}: {e}")
        return msg  # Return internal server error


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
def change_stokvel_name_endpoint() -> str:
    """
    Endpoint to change the stokvel name.
    """
    try:
        user_number = request.json.get("user_number")
        new_stokvel_name = request.json.get(
            "user_input"
        )  # This will be the new stokvel name
        stokvel_name = request.json.get("stokvel_selection")  # The current stokvel name

        if not user_number or not new_stokvel_name or not stokvel_name:
            return jsonify({"error": "Missing required fields"}), 400

        # Call the update function
        update_stokvel_name(stokvel_name=stokvel_name, new_stokvelname=new_stokvel_name)

        # Send notification to the user
        send_notification_message(
            to=user_number,
            body=f"Your stokvel name has been successfully updated to {new_stokvel_name}.",
        )

    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error in {change_stokvel_name_endpoint.__name__}: {e}")
        return jsonify({"error": msg}), 500


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
            insert_stokvel_join_application(
                stokvel_id=stokvel_id,
                user_id=user_id,
                user_contribution=user_contribution,
            )

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
        # send_notification_message(
        #     to=f"whatsapp:{joiner_data.requesting_number}",
        #     body=joiner_notification_message,
        # )

        # Send the notification message
        # send_notification_message(
        #     to=f"whatsapp:{stokvel_admin_cell_number}", body=admin_notification_message
        # )
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
            stokvel_id=None,
            stokvel_name=stokvel_data.stokvel_name,  # unique constraint here
            ILP_wallet="ILP_TEST",
            MOMO_wallet="MOMO_TEST",
            total_members=stokvel_data.total_members,
            min_contributing_amount=stokvel_data.min_contributing_amount,
            max_number_of_contributors=stokvel_data.max_number_of_contributors,  # stokvel_data.max_number_of_contributors,
            total_contributions=0,
            start_date=stokvel_data.start_date,
            end_date=stokvel_data.end_date,
            payout_frequency_duration=stokvel_data.payout_frequency_duration,
            contribution_period=stokvel_data.contribution_period,
            created_at=None,
            updated_at=None,
        )

        stokvel_data.stokvel_id = inserted_stokvel_id

        print("stokvel created id = ")
        print(stokvel_data.stokvel_id)

        print("Printing requseting number id = ")
        print(stokvel_data.requesting_number)

        user_id = find_user_by_number(stokvel_data.requesting_number)

        # region Commented out old inserts

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
        # endregion

        # region USER CONTRIBUTION GRANT THINGS

        print(
            get_iso_with_default_time(stokvel_data.start_date),
            " ",
            get_iso_with_default_time(stokvel_data.end_date),
        )

        number_payout_periods_between_start_end_date = calculate_number_periods(
            stokvel_data.payout_frequency_duration,
            start_date=stokvel_data.start_date,
            end_date=stokvel_data.end_date,
        )

        number_contribution_periods_between_start_end_date = calculate_number_periods(
            stokvel_data.contribution_period,
            start_date=stokvel_data.start_date,
            end_date=stokvel_data.end_date,
        )
        print("contrib payout params")
        print(stokvel_data.contribution_period)
        print(stokvel_data.payout_frequency_duration)

        print(number_payout_periods_between_start_end_date)
        print(number_contribution_periods_between_start_end_date)

        print("USER CONTRIBUTION GRANT FUNCTIONALITY")

        payload = {
            "value": str(
                int(stokvel_data.min_contributing_amount * 100)
            ),  # multiply by 100 because the asset scale is 2?
            "stokvel_contributions_start_date": get_iso_with_default_time(
                stokvel_data.start_date
            ),
            "walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "sender_walletAddressURL": find_wallet_by_userid(user_id=user_id),
            "payment_periods": number_contribution_periods_between_start_end_date,  # how many contributions are going to be made
            "payment_period_length": format_contribution_period_string(
                stokvel_data.contribution_period
            ),
            "length_between_periods": (
                "T30"
                if format_contribution_period_string(stokvel_data.contribution_period)
                == "S"
                else "1"
            ),
            "user_id": user_id,
            "stokvel_id": stokvel_data.stokvel_id,
        }
        print("REQUEST: ")
        print(payload)

        response = requests.post(node_server_initiate_grant, json=payload)

        print(response)

        print("RESPONSE: \n", response.json())
        print(
            "REDIRECT USER FOR AUTH: ",
            response.json()["recurring_grant"]["interact"]["redirect"],
        )

        initial_continue_uri_contribution = response.json()["continue_uri"]
        initial_continue_token_contribution = response.json()["continue_token"]["value"]
        initial_payment_quote_contribution = response.json()["quote_id"]

        # endregion

        # region WALLET PAYOUT GRANT THINGS

        payment_period_duration_converted, number_periods = (
            double_number_periods_for_same_daterange(
                period=stokvel_data.payout_frequency_duration
            )
        )

        payload_payout = {
            "value": str(int(1)),  # create an initial payment of 1c
            "stokvel_contributions_start_date": get_iso_with_default_time(
                stokvel_data.start_date
            ),
            "walletAddressURL": find_wallet_by_userid(user_id=user_id),
            "sender_walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "payment_periods": number_payout_periods_between_start_end_date
            * 2,  # how many contributions are going to be made
            "payment_period_length": payment_period_duration_converted,
            "number_of_periods": str(number_periods),
            "user_id": user_id,
            "stokvel_id": stokvel_data.stokvel_id,
        }

        print("PAYOUT SET UP REQUEST: ")
        print(payload_payout)

        response_payout_grant = requests.post(
            node_server_initiate_stokvelpayout_grant, json=payload_payout
        )
        print(response_payout_grant)

        # quote_json = ""

        initial_continue_uri_stokvel = response_payout_grant.json()["continue_uri"]
        initial_continue_token_stokvel = response_payout_grant.json()["continue_token"][
            "value"
        ]
        initial_quote_stokvel = response_payout_grant.json()["quote_id"]

        # # # update_token_things()

        # print("RESPONSE: \n", response.json())
        print(
            "\n \n \nREDIRECT STOKVEL AGENT FOR AUTH: ",
            response_payout_grant.json()["recurring_grant"]["interact"]["redirect"],
        )

        # #On grant accept, redirect to the logic to: add status active and forward date payments

        # endregion

        # region INSERTS USER IN TABLES
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
            user_id=find_user_by_number(stokvel_data.requesting_number),
            user_contribution=stokvel_data.min_contributing_amount,
            user_token=initial_continue_token_contribution,
            user_url=initial_continue_uri_contribution,
            user_quote_id=initial_payment_quote_contribution,
            stokvel_quote_id=initial_quote_stokvel,
            stokvel_token=initial_continue_token_stokvel,
            stokvel_url=initial_continue_uri_stokvel,
            stokvel_initial_payment_needed=1,
        )

        # update the number of contributors
        update_stokvel_members_count(stokvel_id=inserted_stokvel_id)

        # add admin - get whatsapp number
        insert_admin(
            stokvel_id=inserted_stokvel_id,
            stokvel_name=stokvel_data.stokvel_name,
            user_id=find_user_by_number(stokvel_data.requesting_number),
            total_contributions=0,
            total_members=1,
        )

        # generate contribution dates
        insert_member_contribution_parameters(
            stokvel_id=stokvel_data.stokvel_id,
            start_date=stokvel_data.start_date,
            payout_period=stokvel_data.contribution_period,
        )

        # generate payouts
        insert_stokvel_payouts_parameters(
            stokvel_id=stokvel_data.stokvel_id,
            start_date=stokvel_data.start_date,
            payout_period=stokvel_data.payout_frequency_duration,
        )

        # endregion

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
            stokvel_dict = get_stokvel_details(stokvel_id=application_stokvel_id)
            print(stokvel_dict)

            # region USER CONTRIBUTION GRANT THINGS

            # Use stokvel_dict to retrieve values for start_date, end_date, and contribution_amount
            print(
                get_iso_with_default_time(stokvel_dict.get("start_date")),
                " ",
                get_iso_with_default_time(stokvel_dict.get("end_date")),
            )

            # Calculate number of payout periods and contribution periods between start and end dates
            number_payout_periods_between_start_end_date = calculate_number_periods(
                stokvel_dict.get("payout_frequency_duration"),
                start_date=stokvel_dict.get("start_date"),
                end_date=stokvel_dict.get("end_date"),
            )

            number_contribution_periods_between_start_end_date = (
                calculate_number_periods(
                    stokvel_dict.get("contribution_period"),
                    start_date=stokvel_dict.get("start_date"),
                    end_date=stokvel_dict.get("end_date"),
                )
            )

            print(number_payout_periods_between_start_end_date)
            print(number_contribution_periods_between_start_end_date)

            print("USER CONTRIBUTION GRANT FUNCTIONALITY")

            # Prepare the payload for user contribution grant
            payload = {
                "value": str(
                    int(user_contribution) * 100
                ),  # Multiply by 100 due to asset scale
                "stokvel_contributions_start_date": get_iso_with_default_time(
                    stokvel_dict.get("start_date")
                ),
                "walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
                "sender_walletAddressURL": find_wallet_by_userid(
                    user_id=application_joiner_id
                ),
                "payment_periods": number_contribution_periods_between_start_end_date,  # How many contributions to make
                "payment_period_length": format_contribution_period_string(
                    stokvel_dict.get("contribution_period")
                ),
                "length_between_periods": (
                    "T30"
                    if format_contribution_period_string(
                        stokvel_dict.get("contribution_period")
                    )
                    == "S"
                    else "1"
                ),
                "user_id": application_joiner_id,
                "stokvel_id": application_stokvel_id,
            }
            print("REQUEST: ")
            print(payload)

            # Send POST request for contribution grant
            response = requests.post(node_server_initiate_grant, json=payload)
            print(response)

            print("RESPONSE: \n", response.json())
            print(
                "REDIRECT USER FOR AUTH: ",
                response.json()["recurring_grant"]["interact"]["redirect"],
            )

            # Extract initial continue URI and token for contributions
            initial_continue_uri_contribution = response.json()["continue_uri"]
            initial_continue_token_contribution = response.json()["continue_token"][
                "value"
            ]
            initial_payment_quote_contribution = response.json()["quote_id"]

            # endregion

            # region WALLET PAYOUT GRANT THINGS

            # Prepare values for payout grant using stokvel_dict
            payment_period_duration_converted, number_periods = (
                double_number_periods_for_same_daterange(
                    period=stokvel_dict.get("payout_frequency_duration")
                )
            )

            # Prepare the payload for payout grant
            payload_payout = {
                "value": str(int(1)),  # Create an initial payment of 1c
                "stokvel_contributions_start_date": get_iso_with_default_time(
                    stokvel_dict.get("start_date")
                ),
                "walletAddressURL": find_wallet_by_userid(
                    user_id=application_joiner_id
                ),
                "sender_walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
                "payment_periods": number_payout_periods_between_start_end_date
                * 2,  # Double the number of payout periods
                "payment_period_length": payment_period_duration_converted,
                "number_of_periods": str(number_periods),
                "user_id": application_joiner_id,
                "stokvel_id": application_stokvel_id,
            }

            print("PAYOUT SET UP REQUEST: ")
            print(payload_payout)

            # Send POST request for payout grant
            response_payout_grant = requests.post(
                node_server_initiate_stokvelpayout_grant, json=payload_payout
            )
            print(response_payout_grant)

            # Extract initial continue URI and token for payouts
            initial_continue_uri_stokvel = response_payout_grant.json()["continue_uri"]
            initial_continue_token_stokvel = response_payout_grant.json()[
                "continue_token"
            ]["value"]
            initial_quote_stokvel = response_payout_grant.json()["quote_id"]

            print(
                "\n \n \nREDIRECT STOKVEL AGENT FOR AUTH: ",
                response_payout_grant.json()["recurring_grant"]["interact"]["redirect"],
            )

            # endregion

            # region INSERTS USER IN TABLES

            declined_applications_list = insert_stokvel_member(
                application_id=application_joiner_id,
                stokvel_id=application_stokvel_id,
                user_id=application_joiner_id,
                user_contribution=user_contribution,
                user_token=initial_continue_token_contribution,
                user_url=initial_continue_uri_contribution,
                user_quote_id=initial_payment_quote_contribution,
                stokvel_quote_id=initial_quote_stokvel,
                stokvel_token=initial_continue_token_stokvel,
                stokvel_url=initial_continue_uri_stokvel,
                stokvel_initial_payment_needed=1,
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
                    pass
                    # Send the notification message
                    # send_notification_message(
                    #     to=f"whatsapp:{number}", body=app_declined_notification_message
                    # )

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
            # send_notification_message(
            #         to=f"whatsapp:{applicant_cell_number}",
            #         body=app_accepted_notification_message,
            #     )

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
        # send_notification_message(
        #     to=f"whatsapp:{applicant_cell_number}",
        #     body=app_declined_notification_message,
        # )

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


@stokvel_bp.route(f"{BASE_ROUTE}/stokvel_total_interest", methods=["POST"])
def stokvel_total_interest() -> str:
    """
    This enpoint returns the total stokvel interest in the savings period.
    """
    stokvel_name = request.json.get(
        "stokvel_selection"
    )  # Get the stokvel name from query parameters

    try:
        # fetch stokvel id
        stokvel_id = get_stokvel_id_by_name(stokvel_name)
        # get monthly interest values
        interest_dict = get_stokvel_monthly_interest(stokvel_id)
        # get total accumulated interest for the period
        stkvl_interest = sum(interest_dict.values())
        msg = f"The total interest for this Stokvel is: R{stkvl_interest}"
        return msg
    except Exception as e:
        msg = "There was an error performing that action, please try the action again."
        print(f"Error: {e}")
        return msg
    

@stokvel_bp.route(f"{BASE_ROUTE}/stokvel/admin/change_member_number", methods=["POST"])
def change_max_nr_of_contrributors() -> str:
    """
    Endpoint to change the maximum number of contributors for a stokvel.
    """
    try:
        user_number = request.json.get("user_number")
        max_nr_of_contributors = request.json.get("user_input")  # Renamed for clarity
        stokvel_name = request.json.get("stokvel_selection")

        if not user_number or not max_nr_of_contributors or not stokvel_name:
            return jsonify({"error": "Missing required fields"}), 400

        # Update the max number of contributors
        update_max_nr_of_contributors(
            stokvel_name=stokvel_name, max_nr_of_contributors=max_nr_of_contributors
        )

        # Send notification to the user
        send_notification_message(
            to=user_number,
            body=f"Max number of contributors has been updated to {max_nr_of_contributors}.",
        )

    except Exception as e:
        msg = "There was an error performing that action, please try again."
        print(f"Error in {update_max_nr_of_contributors.__name__}: {e}")
        return jsonify({"error": msg}), 500


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_stokvel/user_interactive_grant_response", methods=["GET"]
)
def user_interactive_grant_handle() -> str:
    """
    Handle the success or rejection of stokvel contributions.
    """

    # Extract query parameters
    result = request.args.get("result")  # For grant_rejected
    hash_value = request.args.get("hash")  # For the confirmation hash
    interact_ref = request.args.get(
        "interact_ref"
    )  # For the interact_ref when confirmed
    user_id = request.args.get("user_id")
    stokvel_id = request.args.get("stokvel_id")

    action = "Stokvel contributions grant has been accepted"
    success_message = "Your contributions will be processed at the specified periods."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    if result == "grant_rejected":
        action = "Stokvel contributions grant has been rejected"
        failed_message = "Unfortunately, your contributions were not accepted."
        failed_next_step_message = "Please contact support or try again."

        return render_template(
            "action_failed_template.html",
            action=action,
            failed_message=failed_message,
            failed_next_step_message=failed_next_step_message,
        )

    if hash_value and interact_ref:
        print(f"Confirmed with interact_ref: {interact_ref}")
        update_member_grantaccepted(
            user_id=user_id,
            stokvel_id=stokvel_id,
            active_status="active",
            user_interaction_ref=interact_ref,
        )

        return render_template(
            "action_success_template.html",
            action=action,
            success_message=success_message,
            success_next_step_message=success_next_step_message,
        )


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_stokvel/stokvel_interactive_grant_response", methods=["GET"]
)
def stokvel_interactive_grant_handle() -> str:
    """
    Handle the success or rejection of stokvel contributions.
    """

    # Extract query parameters
    result = request.args.get("result")  # For grant_rejected
    hash_value = request.args.get("hash")  # For the confirmation hash
    interact_ref = request.args.get(
        "interact_ref"
    )  # For the interact_ref when confirmed
    user_id = request.args.get("user_id")
    stokvel_id = request.args.get("stokvel_id")

    action = "Stokvel payout grant has been accepted"
    success_message = "Your payout will be processed at the specified periods."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    if result == "grant_rejected":
        action = "Stokvel payouts grant has been rejected"
        failed_message = "Unfortunately, users payouts were not accepted."
        failed_next_step_message = "Please contact support or try again."

        return render_template(
            "action_failed_template.html",
            action=action,
            failed_message=failed_message,
            failed_next_step_message=failed_next_step_message,
        )

    if hash_value and interact_ref:
        print(f"Confirmed with interact_ref: {interact_ref}")
        update_stokvel_grantaccepted(
            user_id=user_id,
            stokvel_id=stokvel_id,
            stokvel_payout_active_status="active",
            stokvel_interaction_ref=interact_ref,
        )

        print("add initial payment")

        stokvel_members_details = get_stokvel_member_details(stokvel_id, user_id)

        payload = {
            "quote_id": stokvel_members_details.get("stokvel_quote_id"),
            "continueUri": stokvel_members_details.get("stokvel_payment_URI"),
            "continueAccessToken": stokvel_members_details.get("stokvel_payment_token"),
            "walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "interact_ref": stokvel_members_details.get("stokvel_interaction_ref"),
        }

        response = requests.post(node_server_create_initial_payment, json=payload)

        print("RESPONSE: \n", response.json())

        new_token = response.json()["token"]
        new_uri = response.json()["manageurl"]

        update_stokvel_token_uri(stokvel_id, user_id, new_token, new_uri)

        return render_template(
            "action_success_template.html",
            action=action,
            success_message=success_message,
            success_next_step_message=success_next_step_message,
        )


@stokvel_bp.route(f"{BASE_ROUTE}/adhoc_payment_grant_accept", methods=["GET"])
def adhoc_payment_grant_handle() -> str:
    """
    Handle the success or rejection of stokvel contributions.
    """
    # Extract query parameters
    result = request.args.get("result")  # For grant_rejected
    hash_value = request.args.get("hash")  # For the confirmation hash
    interact_ref = request.args.get(
        "interact_ref"
    )  # For the interact_ref when confirmed
    user_id = request.args.get("user_id")
    stokvel_id = request.args.get("stokvel_id")
    quote_id = request.args.get("quote_id")

    action = "Stokvel adhoc payment has been accepted and will be processed."
    success_message = "Your payout will be processed at the specified periods."
    success_next_step_message = (
        "Please navigate back to WhatsApp for further functions."
    )

    if result == "grant_rejected":
        action = "Stokvel payouts grant has been rejected"
        failed_message = "Unfortunately, users payouts were not accepted."
        failed_next_step_message = "Please contact support or try again."

        return render_template(
            "action_failed_template.html",
            action=action,
            failed_message=failed_message,
            failed_next_step_message=failed_next_step_message,
        )

    if hash_value and interact_ref:
        print(f"Confirmed with interact_ref: {interact_ref}")
        print("add adhoc payment")

        stokvel_members_details = get_stokvel_member_details(
            stokvel_id, user_id
        )  # use here to get the details

        try:
            payload = {
                "quote_id": quote_id,
                "continueUri": stokvel_members_details.get("adhoc_contribution_uri"),
                "continueAccessToken": stokvel_members_details.get(
                    "adhoc_contribution_token"
                ),
                "walletAddressURL": find_wallet_by_userid(user_id=user_id),
                "interact_ref": interact_ref,
            }

            response = requests.post(node_server_create_initial_payment, json=payload)

            print("RESPONSE: \n", response.json())

            if response.json()["payment"]["failed"] == False:
                # TO DO: ADD PAYMENT TO TRANSACION TABLE
                print("payment was successful")
                pass

            return render_template(
                "action_success_template.html",
                action=action,
                success_message=success_message,
                success_next_step_message=success_next_step_message,
            )
        except Exception as e:
            print(e)
            action = "Adhoc paymnet has failed"
            failed_message = "Unfortunately, we could not process payment"
            failed_next_step_message = "Please contact support or try again."

            return render_template(
                "action_failed_template.html",
                action=action,
                failed_message=failed_message,
                failed_next_step_message=failed_next_step_message,
            )


@stokvel_bp.route(
    f"{BASE_ROUTE}/create_adhoc_payment", methods=["POST"]
)  # would need to change this to take in actual parameters...
def adhoc_payment_test():
    node_end_point = "http://localhost:3000/adhoc-payment-setup"  # Fixed URL
    user_id = 980618  # Fixed user_id
    stokvel_id = 18  # Fixed stokvel_id

    try:
        payload = {
            "value": "500",
            "stokvel_contributions_start_date": "2024-10-09T16:52:30.123Z",
            "walletAddressURL": "https://ilp.rafiki.money/alices_stokvel",
            "sender_walletAddressURL": "https://ilp.rafiki.money/bob_account",
            "user_id": user_id,
            "stokvel_id": stokvel_id,
        }

        response = requests.post(node_end_point, json=payload)

        # Check for response status
        response.raise_for_status()  # Raises an error for 4xx/5xx responses

        # Ensure keys exist in the response
        response_data = response.json()
        adhoc_continue_uri = response_data.get("continue_uri")
        adhoc_continue_token = response_data.get("continue_token", {}).get("value")

        print("RESPONSE: \n", response_data)

        # Ensure both URI and token are valid before proceeding
        if adhoc_continue_uri and adhoc_continue_token:
            update_adhoc_contribution_parms(
                stokvel_id=stokvel_id,
                user_id=user_id,
                url=adhoc_continue_uri,
                token=adhoc_continue_token,
            )
            return {"message": "Success", "data": response_data}, 200
        else:
            return {"error": "Missing continue_uri or continue_token"}, 400

    except requests.exceptions.RequestException as req_error:
        print("Request error occurred:", req_error)
        return {
            "error": str(req_error)
        }, 500  # Return a JSON response with request error

    except Exception as e:
        print("Error occurred:", e)  # Print the error for debugging
        return {"error": str(e)}, 500  # Return a JSON response with an error message
