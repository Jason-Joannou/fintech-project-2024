# from .sql_connection import sql_connection
import sqlite3
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()


def get_total_number_of_users() -> int:
    """
    docstrings
    """
    engine = sqlite_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            query = text("SELECT COUNT(DISTINCT user_id) FROM USERS")
            result = conn.execute(query)
            user_count = result.scalar()

            transaction.commit()

            return user_count
        except Exception as e:
            transaction.rollback()
            print(f"There was an error retreiving the SQL error: {e}")
            return 0


def check_if_number_exists_sqlite(from_number: str) -> bool:
    """
    docstring
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = "SELECT * FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()
        if result:
            return True

        return False


def check_if_number_is_admin(from_number: str) -> bool:
    """
    docstring
    """
    from_number = extract_whatsapp_number(from_number=from_number)

    query = """
    SELECT COUNT(*)
    FROM USERS u
    JOIN ADMIN a ON u.user_id = a.user_id
    WHERE u.user_number = :user_number
    """

    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_number": from_number})
        result = cursor.fetchone()

    return result[0] >= 1


def get_linked_stokvels(user_number):
    """
    Get the stokvels a user is linked to, and check if they are an admin.
    """
    user_number = extract_whatsapp_number(from_number=user_number)
    query = """
    SELECT
        a.stokvel_name,
        CASE
            WHEN b.user_id IN (
                SELECT user_id
                FROM USERS
                WHERE user_number = :user_number
            )
            THEN 1
            ELSE 0
        END AS admin_ind
    FROM STOKVELS as a
    LEFT JOIN ADMIN as b ON a.stokvel_id = b.stokvel_id
    WHERE a.stokvel_id IN (
        SELECT stokvel_id
        FROM STOKVEL_MEMBERS
        WHERE user_id IN (
            SELECT user_id FROM USERS WHERE user_number = :user_number
        )
    );
    """

    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_number": user_number})
        result = cursor.fetchall()

    # Process the results into a list of (stokvel_name, admin_ind)
    linked_accounts = [(row[0], row[1]) for row in result]

    return linked_accounts


def find_user_by_number(from_number: str) -> Optional[str]:
    """
    docstring
    """
    # from_number = "0"+str(from_number)
    # print(from_number)
    print(from_number)
    query = "SELECT user_id FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return result

        return None


def find_number_by_userid(user_id: str) -> Optional[str]:
    """
    docstring
    """
    # from_number = "0"+str(from_number)
    # print(from_number)
    print(user_id)
    query = "SELECT user_number FROM USERS WHERE user_id = :user_id"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_id": user_id})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return result

        return None


def insert_user(
    user_id: str,
    user_number: str,
    user_name: str,
    user_surname: str,
    ilp_wallet: str,
    momo_wallet: str = "test",
    verified_kyc: int = 1,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> None:
    # Need to look at refactoring this

    """
    Inserts a new user into the USERS table.

    Args:
        user_id (int): The user's ID.
        user_number (str): The user's number.
        user_name (str): The user's name.
        user_surname (str): The user's surname.
        ILP_wallet (str): The user's ILP wallet.
        MOMO_wallet (str): The user's MOMO wallet.
        verified_KYC (int): KYC verification status (0 or 1).
        created_at (str, optional): The timestamp when the user was created. Defaults to current time if not provided.
        updated_at (str, optional): The timestamp when the user was last updated. Defaults to current time if not provided.
    """
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_query = """
    INSERT INTO USERS (
        user_id, user_number, user_name, user_surname, ILP_wallet,
        MOMO_wallet, verified_KYC, created_at, updated_at
    ) VALUES (
        :user_id, :user_number, :user_name, :user_surname, :ILP_wallet,
        :MOMO_wallet, :verified_KYC, :created_at, :updated_at
    )
    """

    parameters = {
        "user_id": user_id,
        "user_number": user_number,
        "user_name": user_name,
        "user_surname": user_surname,
        "ILP_wallet": ilp_wallet,
        "MOMO_wallet": momo_wallet,
        "verified_KYC": verified_kyc,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in user insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")

    except sqlite3.IntegrityError as integrity_error:
        # Catch integrity errors such as unique constraint violations
        print(f"IntegrityError during insert: {integrity_error}")

    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise e

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e


def insert_wallet(user_id: str, user_wallet: str, user_balance: float) -> None:
    """
    Inserts a new user wallet into the USER_WALLET table.

    Args:
        user_id (int): The user's ID.
        user_wallet (str): The user's wallet address.
        userbalance (float): The user's balance in the wallet.
    """

    insert_query = """
    INSERT INTO USER_WALLET (
        user_id, user_wallet, UserBalance
    ) VALUES (
        :user_id, :user_wallet, :UserBalance
    )
    """

    parameters = {
        "user_id": user_id,
        "user_wallet": user_wallet,
        "UserBalance": user_balance,
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in wallet insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()
            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise e
    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e

def get_account_details(phone_number: str):
    """
    Retrieve account details for a user based on their phone number.
    """
    from_number = extract_whatsapp_number(from_number=phone_number)
    print(f"Extracted phone number: {from_number}")

    query = """
    SELECT 
        u.user_id, 
        u.user_number, 
        u.user_name, 
        u.user_surname, 
        uw.user_wallet, 
        uw.UserBalance, 
        u.created_at
    FROM 
        USERS u
    JOIN 
        USER_WALLET uw ON u.user_id = uw.user_id
    WHERE 
        u.user_number = :user_number;
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
            "u.user_id": result[0],
            "u.user_number": result[1],
            "u.user_name": result[2],
            "u.user_surname": result[3],
            "uw.user_wallet": result[4],
            "uw.UserBalance": result[5],
            "u.created_at": result[6],
        }

        #print(f"User details: {user_details}")
        return user_details  # Return the complete user details

def update_user_name(phone_number: str, new_name: str):
    """
    Update the user's name based on their phone number.

    Args:
        phone_number (str): The user's phone number.
        new_name (str): The new name to update.

    Returns:
        str: Success or failure message.
    """
    formatted_number = extract_whatsapp_number(from_number=phone_number)

    # SQL query to update user name
    update_query = """
    UPDATE USERS
    SET user_name = :new_name
    WHERE user_number = :user_number;
    """

    with sqlite_conn.connect() as conn:
        result = conn.execute(text(update_query), {"new_name": new_name, "user_number": formatted_number})

        if result.rowcount == 0:
            return f"No user found with phone number: {phone_number}"

        return f"User name updated successfully for phone number: {phone_number}"

def update_user_surname(phone_number: str, new_surname: str):
    """
    Update the user's surname based on their phone number.

    Args:
        phone_number (str): The user's phone number.
        new_surname (str): The new surname to update.

    Returns:
        str: Success or failure message.
    """
    formatted_number = extract_whatsapp_number(from_number=phone_number)

    # SQL query to update user surname
    update_query = """
    UPDATE USERS
    SET user_surname = :new_surname
    WHERE user_number = :user_number;
    """

    with sqlite_conn.connect() as conn:
        result = conn.execute(text(update_query), {"new_surname": new_surname, "user_number": formatted_number})

        if result.rowcount == 0:
            return f"No user found with phone number: {phone_number}"

        return f"User surname updated successfully for phone number: {phone_number}"
