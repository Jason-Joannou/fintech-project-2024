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
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
    except Exception as e:
        print(f"Error occurred during insert: {e}")


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

            # Confirm the number of rows affected
            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
    except Exception as e:
        print(f"Error occurred during insert: {e}")
