from whatsapp_utils._utils.message_config import REGISTERED_NUMBER

# Need to add messages states as we go
MESSAGE_STATES = {
    "base_state": ["Hi", "Hello"],
    "unrecognized_state": "Sorry, I don't understand that action.",
    "registered_number_state": REGISTERED_NUMBER,
}
