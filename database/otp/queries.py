from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection

db_conn = SQLiteConnection("./database/test_db.db")


def insert_new_otp(
    phone_number: str,
    otp: int,
    expires_at: str = (datetime.now() + timedelta(minutes=2)).strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
) -> None:
    """
    Inserts a new OTP record into the otps table.

    Args:
        phone_number (str): The user's phone number.
        otp (int): The generated OTP.
        expires_at (str): The expiration timestamp for the OTP in 'YYYY-MM-DD HH:MM:SS' format.
    """

    query = """
    INSERT INTO otps (user_number, otp, created_at, expires_at, is_verified)
    VALUES (:phone_number, :otp, CURRENT_TIMESTAMP, :expires_at, FALSE);
    """

    with db_conn.get_engine().connect() as conn:
        conn.begin()
        conn.execute(
            text(query),
            {"phone_number": phone_number, "otp": otp, "expires_at": expires_at},
        )
        conn.commit()


def fetch_existing_otp(phone_number: str) -> Optional[Dict]:
    """
    Fetches the existing OTP for a given phone number.

    Args:
        phone_number (str): The user's phone number.

    Returns:
        dict: A dictionary containing the OTP details or None if no OTP exists.
    """
    query = "SELECT otp, expires_at FROM otps WHERE user_number = :phone_number AND is_verified = FALSE ORDER BY created_at DESC LIMIT 1;"

    with db_conn.get_engine().connect() as conn:
        conn.begin()
        result = conn.execute(text(query), {"phone_number": phone_number}).fetchone()
        conn.commit()
        return result if result else None


def update_successful_opt(phone_number: str) -> None:
    """
    docstring
    """

    query = text(
        """
    UPDATE OTPS
    SET is_verified = True
    WHERE user_number = :phone_number"""
    )

    with db_conn.get_engine().connect() as conn:
        conn.begin()
        conn.execute(query, {"phone_number": phone_number})
        conn.commit()
