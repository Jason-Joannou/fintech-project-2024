from .twilio_client import TwilioClient


twilio_client = TwilioClient()

def send_notification_message(to, body):
    """
    docstring
    """
    twilio_client.send_mesage_notification(to, body)

def send_conversational_message(message):
    """
    docstring
    """
    return twilio_client.send_conversational_message(message)