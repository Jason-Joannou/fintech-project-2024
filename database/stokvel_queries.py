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

            print(stokvels)


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
                'updated_at': stokvel[9],
                'start_date':stokvel[10],
                'end_date':stokvel[11],
                'payout_frequency_int':stokvel[12],
                'payout_frequency_period':stokvel[13],
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

def update_stokvel_members_count(stokvel_id):
    """
    Updates the stokvel members count
    """

    count_query = "SELECT COUNT(*) FROM group_members WHERE stokvel_id = :stokvel_id;"
    parameters = {
        "stokvel_id": stokvel_id
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected to the database for stokvel members update")
            
            cursor = conn.execute(text(count_query), parameters)
            total_members = cursor.fetchone()[0]
            
            update_query = "UPDATE STOKVELS SET total_members = :total_members WHERE stokvel_id = :stokvel_id;"
            
            update_parameters = {
                "stokvel_id": stokvel_id,
                "total_members": total_members
            }
            
            conn.execute(text(update_query), update_parameters)
            conn.commit() 
            
            print(f"Updated total_members for stokvel_id {stokvel_id} to {total_members}")
            
    except Exception as e:
        print(f"An error occurred: {e}")


def insert_stokvel_join_application(
    stokvel_id: int, #unique constraint here
    user_id: int,
    AppStatus: Optional[str] = None,
    AppDate: Optional[str] = None,
):
    """
    docstring
    """

    if AppDate is None:
        AppDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if AppStatus is None:
        AppStatus = "Application Submitted"

    insert_query = """
        INSERT INTO STOKVEL_MEMBERS (
            id, stokvel_id, user_id, AppStatus, AppDate
        ) VALUES (
            :id, :stokvel_id, :user_id, :AppStatus, :AppDate
        )
        """
    
    parameters = {
        "id" : None,
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "AppStatus": AppStatus,
        "AppDate": AppDate
    }

    try:
        with sqlite_conn.connect() as conn:
            if stokvel_id is None:
                stokvel_current_id = get_next_unique_id(conn, 'APPLICATIONS', 'id')
                parameters['stokvel_id'] = stokvel_current_id

            print("Connected in application insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
                print('insert application successful')

            else:
                print("Insert failed.")
            
            return stokvel_current_id
        
    except sqlite3.Error as e:
        print(f"Error occurred during insert application: {e}")
        raise Exception(f"SQLiteError occurred during inserting a application: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a application: {e}")  # Stops execution by raising the error