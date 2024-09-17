from .twilio_client import TwilioClient

twilio_client = TwilioClient()


def send_notification_message(to: str, body: str):
    """
    docstring
    """
    twilio_client.send_mesage_notification(to, body)


def send_conversational_message(message: str):
    """
    docstring
    """
    return twilio_client.send_conversational_message(message)
