from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class TwilioClient:
    """
    docstring
    """

    def __init__(self):
        self.client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')

    def send_mesage(self, to, body):
        """
        docstring
        """
        message = self.client.messages.create(
            to=to,
            from_=self.from_number,
            body=body
        )

        print(f"Message sent: {message.sid}")