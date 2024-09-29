from flask import Blueprint, jsonify, request

from database.sqlite_connection import SQLiteConnection
from database.user_queries.queries import get_linked_stokvels
from whatsapp_utils._utils.twilio_messenger import send_notification_message

stokvel_bp = Blueprint("stokvels", __name__)

BASE_ROUTE = "/stokvels"


@stokvel_bp.route(BASE_ROUTE)
def stokvel() -> str:
    """
    docstrings
    """
    return "Stokvel API. This API endpoint for all things stokvel related!"


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
