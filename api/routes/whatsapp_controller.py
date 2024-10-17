from flask import Blueprint, request

from whatsapp_utils._utils.state_manager import MessageStateManager

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"


@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
def whatsapp() -> str:
    """
    Handle Incoming WhatsApp Messages
    Processes user requests based on the current state managed through WhatsApp interactions.
    ---
    tags:
      - WhatsApp
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - Body
            - From
          properties:
            Body:
              type: string
              description: The content of the incoming WhatsApp message.
              example: "Check my balance"
            From:
              type: string
              description: The phone number of the user sending the message.
              example: "+27821234567"
    responses:
      200:
        description: Successfully processed the user request and returned a response message.
        schema:
          type: string
          example: "Your balance is R500."
      400:
        description: Bad request. The message body or sender information is missing.
        schema:
          type: string
          example: "Invalid request. Please send a valid message."
      500:
        description: Internal server error. Something went wrong while processing the request.
        schema:
          type: string
          example: "An error occurred while processing your request. Please try again."
    """
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")

    state_manager = MessageStateManager(user_number=from_number)
    msg = state_manager.processes_user_request(user_action=incoming_msg)

    return str(msg)
