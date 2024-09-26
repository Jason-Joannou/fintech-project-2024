import random
from datetime import datetime

from database.otp.queries import (
    fetch_existing_otp,
    insert_new_otp,
    update_successful_opt,
)
from whatsapp_utils._utils.twilio_messenger import send_notification_message


def generate_otp():
    """
    docstring
    """
    return str(random.randint(100000, 999999))


def has_otp_expired(otp_record) -> bool:
    """
    Checks if the OTP has expired.

    Args:
        otp_record: The OTP record fetched from the database.

    Returns:
        bool: True if the OTP has expired, False otherwise.
    """
    expires_at = otp_record[1]  # Adjust according to your DB access method
    print(expires_at)
    print(datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.now())
    return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.now()


def send_otp_to_number(phone_number: str) -> str:

    existing_otp = fetch_existing_otp(phone_number)
    if existing_otp and not has_otp_expired(existing_otp):
        return "otp_pending"

    otp = generate_otp()
    msg = f"Hi, please use this otp for verification: {otp}"
    formatted_number = f"whatsapp:{phone_number}"
    # Need to insert opt into db
    insert_new_otp(phone_number=phone_number, otp=otp)
    # Need to check that there is only one occurance of the insertion
    send_notification_message(to=formatted_number, body=msg)

    return "otp_sent"


def verify_otp(phone_number: str, otp: str) -> str:

    existing_otp = fetch_existing_otp(phone_number)
    print(existing_otp)
    if existing_otp and has_otp_expired(existing_otp):
        return "otp_expired"

    print(existing_otp)
    if otp == str(existing_otp[0]):
        update_successful_opt(phone_number=phone_number)
        return "otp_valid"

    return "opt_invalid"
