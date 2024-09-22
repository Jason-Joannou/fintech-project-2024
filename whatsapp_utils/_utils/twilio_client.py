import os

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()


class TwilioClient:
    """
    docstring
    """

    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

    def send_mesage_notification(self, to: str, body: str):
        """
        docstring
        """
        print(to)
        print(self.from_number)
        print(body)
        message = self.client.messages.create(to=to, from_=self.from_number, body=body)

        print(f"Message sent: {message.sid}")

    def send_conversational_message(self, message: str):
        """
        docstring
        """
        twiml = MessagingResponse()
        twiml.message(message)  # Create the TwiML message
        return str(twiml)  # Return the entire TwiML response as a string
