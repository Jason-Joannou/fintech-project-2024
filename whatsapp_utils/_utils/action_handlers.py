from .twilio_messenger import send_conversational_message


def handle_action(from_number: str, action: str):
    """
    docstring
    """
    if action == "1":
        msg = send_conversational_message(
            "Please register through our online portal: https://stokvels.com"
        )
        # Need to get a list of all available stockvels
    elif action == "2":
        pass
    else:
        msg = send_conversational_message(
            "Sorry, I don't understand. Please activate the service by sending 'Hi' or 'Hello'"
        )
        print("Invalid message, please activate the service by sending 'Hi' or 'Hello'")

    return msg
