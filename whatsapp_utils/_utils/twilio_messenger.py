from whatsapp_utils._utils.twilio_client import TwilioClient

twilio_client = TwilioClient()


def send_notification_message(to: str, body: str):
    """
    Sends an SMS notification to the specified phone number.

    Parameters:
    to (str): The recipient's phone number in E.164 format.
    body (str): The content of the SMS message to be sent.

    Returns:
    None
    """
    twilio_client.send_mesage_notification(to, body)


def send_conversational_message(message: str):
    """
    Sends a conversational message using Twilio's TwiML response format.

    Parameters:
    message (str): The content of the conversational message.

    Returns:
    str: The TwiML response as a string, which can be returned as part of an HTTP
    response to Twilio's webhook for handling conversational interactions.
    """
    return twilio_client.send_conversational_message(message)
