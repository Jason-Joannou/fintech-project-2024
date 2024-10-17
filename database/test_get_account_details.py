from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

# Use the provided SQLite connection
sqlite_conn = SQLiteConnection(database="./database/test_db.db")


def get_account_details(phone_number: str):
    """
    Retrieve account details for a user based on their phone number.
    """
    from_number = extract_whatsapp_number(from_number=phone_number)
    print(f"Extracted phone number: {from_number}")

    query = """
    SELECT user_id, user_number, user_name, user_surname, ILP_wallet, MOMO_wallet, created_at
    FROM USERS u
    WHERE u.user_number = :user_number
    """

    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_number": from_number})
        result = cursor.fetchone()
        print(f"Query result: {result}")

        if result is None:
            print("No user found for this phone number.")
            return None

        print(f"Number of fields returned: {len(result)}")

        # Create a dictionary with column names as keys and the corresponding values
        user_details = {
            "user_id": result[0],
            "user_number": result[1],
            "user_name": result[2],
            "user_surname": result[3],
            "ILP_wallet": result[4],
            "MOMO_wallet": result[5],
            "created_at": result[6],
        }

        return user_details  # Return the complete user details
