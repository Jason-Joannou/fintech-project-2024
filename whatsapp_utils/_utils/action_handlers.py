from .twilio_messenger import send_conversational_message


def handle_action(from_number, action):
    """
    docstring
    """
    if action == "1":
        print("Here")
        send_conversational_message("Please register through our online portal: https://stokvels.com")
        # Need to get a list of all available stockvels
    elif action == "2":
        pass
    else:
        pass
