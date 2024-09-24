from flask import Blueprint, request

from whatsapp_utils._utils.state_manager import MessageStateManager

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"


@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
def whatsapp() -> str:
    """
    Handle incoming WhatsApp messages and process user requests based on the current state.

    This method is triggered by a POST request to the WhatsApp webhook endpoint. It retrieves the
    incoming message and the sender's phone number, manages the user's state using the
    `MessageStateManager`, and processes the user's action based on their current state. The
    appropriate response is then generated and returned.

    Returns:
        str: A string containing the response message to be sent back to the user via WhatsApp.
    """
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")

    state_manager = MessageStateManager(user_number=from_number)
    msg = state_manager.processes_user_request(user_action=incoming_msg)

    return str(msg)
