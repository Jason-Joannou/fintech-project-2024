from flask import Blueprint, request

from database.user_queries.queries import check_if_number_exists_sqlite
from whatsapp_utils._utils.action_handlers import handle_action
from whatsapp_utils._utils.cache import Cache
from whatsapp_utils._utils.message_config import (
    GREET_MESSAGE_REGISTERED,
    GREET_MESSAGE_UNREGISTERED,
)
from whatsapp_utils._utils.twilio_messenger import send_conversational_message

cache = Cache()

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"


@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
def whatsapp() -> str:
    """
    docstring
    """
    incoming_msg = request.values.get("Body", "").lower()
    from_number = request.values.get("From", "")

    user = cache.get(from_number)
    if user is None:
        user = check_if_number_exists_sqlite(from_number=from_number)
        if user:
            cache.set(from_number, user)

    if user:
        print("here registered")
        if incoming_msg in ["hi", "hello"]:
            msg = send_conversational_message(GREET_MESSAGE_REGISTERED["message"])
        else:
            msg = handle_action(from_number=from_number, action=incoming_msg)

    else:
        print("User not registered")
        if incoming_msg in ["hi", "hello"]:
            msg = send_conversational_message(
                message=GREET_MESSAGE_UNREGISTERED["message"]
            )
        else:
            msg = handle_action(from_number=from_number, action=incoming_msg)

    return str(msg)
