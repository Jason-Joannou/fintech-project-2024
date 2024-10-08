# from .sql_connection import sql_connection
import sqlite3
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from .sqlite_connection import SQLiteConnection
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from datetime import datetime

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()


def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(
        text(f"SELECT MAX({id_column}) FROM {table_name}")
    ).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1


def check_if_number_exists_sqlite(from_number: str) -> bool:
    """
    docstring
    """
    from_number = from_number.split(":")[1]
    query = "SELECT * FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return True

        return False
    
def find_user_by_number(from_number: str) -> bool:
    """
    docstring UNCOMMENT LATER
    """
    from_number = from_number.split(":")[1]
    query = "SELECT user_id FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()
        print(result)
        if result:
            return result

        return None


def find_user_by_number2(from_number: str) -> Optional[str]:
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

def find_wallet_by_userid(user_id: str) -> Optional[str]:
    """
    docstring
    """
    # from_number = "0"+str(from_number)
    # print(from_number)
    print(user_id)
    query = "SELECT ILP_wallet FROM USERS WHERE user_id = :user_id"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_id": user_id})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return result

        return None

def check_if_id_number_exists_sqlite(user_id: str) -> bool:
    """
    Check if a given user_id exists in the USERS table.

    Parameters
    ----------
    user_id : str
        The user_id to check.

    Returns
    -------
    bool
        True if the user_id exists, False otherwise.
    """
    user_id = user_id.split(":")[1]
    query = "SELECT * FROM USERS WHERE id_number = :id_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_id": user_id})
        result = cursor.fetchone()
        print(result)
        if result:
            return True

        return False

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
        raise sqlite3.IntegrityError(f"IntegrityError during insert: {integrity_error}")
    
    except sqlite3.Error as e:
        # print(f"Error occurred during insert: {e}")
        raise Exception(f"SQLiteError occurred during inserting a user: {e}")  # Stops execution by raising the error

    except Exception as e:
        # print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a user: {e}")  # Stops execution by raising the error



def insert_wallet(
        user_id: str,
        user_wallet: str,
        user_balance: float) -> None:
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
        raise Exception(f"SQLiteError occurred during inserting a wallet: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a wallet: {e}")  # Stops execution by raising the error
    


