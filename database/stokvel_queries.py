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


def insert_stokvel(
    stokvel_id: int,
    stokvel_name: str, #unique constraint here
    ILP_wallet: str,
    MOMO_wallet: str,
    total_members: int,
    min_contributing_amount: float,
    max_number_of_contributors: int,
    Total_contributions: float,
    start_date: str,
    end_date: str,
    payout_frequency_int: int,
    payout_frequency_period: str,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,


) -> int:
    # Need to look at refactoring this

    """
    Inserts a new stokvel into the STOKVELS table AND returns the retrieved id of the stokvel

    Args:
        stokvel_id (int): The stokvel's ID.
        stokvel_name (str): The stokvel's name. Unique constraint.
        ILP_wallet (str): The stokvel's ILP wallet address.
        MOMO_wallet (str): The stokvel's MOMO wallet address.
        total_members (int): The total number of members in the stokvel.
        min_contributing_amount (float): The minimum amount a member can contribute to the stokvel.
        max_number_of_contributors (int): The maximum number of contributors to the stokvel.
        Total_contributions (float): The total amount of contributions made to the stokvel.
        created_at (Optional[str], optional): The time the stokvel was created. Defaults to None.
        updated_at (Optional[str], optional): The time the stokvel was last updated. Defaults to None.
    """

    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_query = """
        INSERT INTO STOKVELS (
            stokvel_id, stokvel_name, ILP_wallet, MOMO_wallet, total_members, 
            min_contributing_amount, max_number_of_contributors, total_contributions, start_date, end_date, payout_frequency_int, payout_frequency_period,
            created_at, updated_at
        ) VALUES (
            :stokvel_id, :stokvel_name, :ILP_wallet, :MOMO_wallet, :total_members, 
            :min_contributing_amount, :max_number_of_contributors, :total_contributions, :start_date, :end_date, :payout_frequency_int, :payout_frequency_period,
            :created_at, :updated_at
        )
        """

    # Parameter dictionary for executing the query
    parameters = {
        "stokvel_id": stokvel_id,
        "stokvel_name": stokvel_name,
        "ILP_wallet": ILP_wallet,
        "MOMO_wallet": MOMO_wallet,
        "total_members": total_members,
        "min_contributing_amount": min_contributing_amount,
        "max_number_of_contributors": max_number_of_contributors,
        "total_contributions": Total_contributions,
        "created_at": created_at,
        "updated_at": updated_at,
        "start_date": start_date,
        "end_date": end_date,
        "payout_frequency_int": payout_frequency_int,
        "payout_frequency_period": payout_frequency_period
    }

    stokvel_current_id = ""

    try:
        with sqlite_conn.connect() as conn:
            if stokvel_id is None:
                stokvel_current_id = get_next_unique_id(conn, 'STOKVELS', 'stokvel_id')
                parameters['stokvel_id'] = stokvel_current_id

            print("Connected in stokvel insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
                print('insert stokvel successful')

            else:
                print("Insert failed.")
            
            return stokvel_current_id
        
    except sqlite3.Error as e:
        print(f"Error occurred during insert stokvel: {e}")
        raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error
    

def insert_stokvel_member(
    stokvel_id: int, #unique constraint here
    user_id: int,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> None:
    # Need to look at refactoring this

    """
    Inserts a new stokvel member into the STOKVEL_MEMBERS table.

    Args:
        stokvel_id (int): The unique ID of the stokvel.
        user_id (int): The unique ID of the user.
        created_at (str, optional): The timestamp when the user was created. Defaults to current time if not provided.
        updated_at (str, optional): The timestamp when the user was last updated. Defaults to current time if not provided.

    Raises:
        Exception: If an error occurs during insert.
    """
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_query = """
        INSERT INTO STOKVEL_MEMBERS (
            stokvel_id, user_id, created_at, updated_at
        ) VALUES (
            :stokvel_id, :user_id, :created_at, :updated_at
        )
        """

    # Parameter dictionary for executing the query
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "created_at": created_at,
        "updated_at": updated_at
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in stokvel_members insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"SQLiteError occurred during inserting a stokvel member: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a stokvel member: {e}")  # Stops execution by raising the error

def get_all_stokvels():
    """
    Retrieve all stokvels from database
    """
    try:
        with sqlite_conn.connect() as conn:

            print("Connected in stokvel_members insert")
            cursor = conn.execute(text('SELECT * FROM stokvels;'))
            stokvels = cursor.fetchall()


        stokvels_list = [
            {
                'stokvel_id': stokvel[0],
                'stokvel_name': stokvel[1],
                'ILP_wallet': stokvel[2],
                'MOMO_wallet': stokvel[3],
                'total_members': stokvel[4],
                'min_contributing_amount': stokvel[5],
                'max_number_of_contributors': stokvel[6],
                'total_contributions': stokvel[7],
                'created_at': stokvel[8],
                'updated_at': stokvel[9]
            } for stokvel in stokvels
        ]

        return stokvels_list
    
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"SQLiteError occurred during inserting a user: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a user: {e}")  # Stops execution by raising the error
    
def insert_admin(
    stokvel_id: int, #unique constraint here
    stokvel_name: str,
    user_id: int,
    total_contributions: int,
    total_members: int,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> None:
    # Need to look at refactoring this
    """
    Inserts a member as a stokvel admin.
    """
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_query = """
        INSERT INTO ADMIN (
            id, stokvel_id, stokvel_name, user_id, total_contributions, total_members
        ) VALUES (
            :id, :stokvel_id, :stokvel_name, :user_id, :total_contributions, :total_members
        )
        """

    # Parameter dictionary for executing the query
    parameters = {
        "id": None,
        "stokvel_id": stokvel_id,
        "stokvel_name":stokvel_name,
        "user_id": user_id,
        "total_contributions": total_contributions,
        "total_members": total_members,
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in stokvel_admin insert")
            parameters['id'] = get_next_unique_id(conn, 'ADMIN', 'id')

            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")
    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"SQLiteError occurred during inserting a admin: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a admin: {e}")  # Stops execution by raising the error