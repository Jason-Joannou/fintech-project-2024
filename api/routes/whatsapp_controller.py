from flask import Blueprint, request

from database.user_queries.queries import check_if_number_exists_sqlite
from whatsapp_utils._utils.action_handlers import handle_action
from whatsapp_utils._utils.cache import Cache
from whatsapp_utils._utils.state_manager import MessageStateManager
from whatsapp_utils._utils.twilio_messenger import send_conversational_message

cache = Cache()

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"


@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
def whatsapp() -> str:
    """
    docstring
    """
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")

    state_manager = MessageStateManager(user_number=from_number)
    msg = state_manager.processes_user_request(user_action=incoming_msg)

    return str(msg)
