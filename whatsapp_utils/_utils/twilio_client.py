import os

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()


class TwilioClient:
    """
    A client wrapper for interacting with the Twilio API to send SMS notifications
    and handle conversational messages using TwiML.
    """

    def __init__(self):
        """
        Initializes the Twilio client using credentials from environment variables.
        The credentials include the account SID, authentication token, and the
        Twilio phone number from which messages will be sent.
        """
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

    def send_mesage_notification(self, to: str, body: str) -> None:
        """
        Sends an SMS message to a specified phone number.

        Parameters:
        to (str): The recipient's phone number in E.164 format.
        body (str): The content of the SMS message.

        Returns:
        None
        """
        self.client.messages.create(to=to, from_=self.from_number, body=body)

    def send_conversational_message(self, message: str) -> str:
        """
        Creates a conversational message using Twilio's TwiML response format.

        Parameters:
        message (str): The text of the message to be sent in the conversation.

        Returns:
        str: The TwiML response as a string, which can be returned as part
        of an HTTP response to Twilio's webhook.
        """
        twiml = MessagingResponse()
        twiml.message(message)  # Create the TwiML message.
        return str(twiml)  # Return the entire TwiML response as a string.
