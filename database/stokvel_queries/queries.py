import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()


def get_user_deposits_and_payouts_per_stokvel(phone_number: str, stokvel_name: str):
    """
    Retrieve total deposit and payout details for a specific user and stokvel based on stokvel name.

    Args:
        phone_number (str): The user's phone number.
        stokvel_name (str): The name of the stokvel to filter by.

    Returns:
        dict: A dictionary containing the user's total deposit and payout amounts.
    """
    from_number = extract_whatsapp_number(from_number=phone_number)

    # Updated query to find total deposits and payouts for a specific user and stokvel
    query = """
    SELECT
        SUM(CASE WHEN t.tx_type = 'DEPOSIT' THEN t.amount ELSE 0 END) AS total_deposits,
        SUM(CASE WHEN t.tx_type = 'PAYOUT' THEN t.amount ELSE 0 END) AS total_payouts
    FROM
        USERS u
    JOIN
        TRANSACTIONS t ON u.user_id = t.user_id
    WHERE
        u.user_number = :user_number
        AND t.stokvel_id = (SELECT stokvel_id FROM STOKVELS WHERE stokvel_name = :stokvel_name)
    GROUP BY
        u.user_id;
    """

    # Executing the query using the SQLite connection
    with sqlite_conn.connect() as conn:
        result = conn.execute(
            text(query), {"user_number": from_number, "stokvel_name": stokvel_name}
        ).fetchone()

        if not result:
            return {
                "error": f"No data found for the given user number and stokvel name: {stokvel_name}."
            }

        # Building the result dictionary from the query response
        return {
            "total_deposits": result[0],  # The total deposit amount for the user
            "total_payouts": result[1],   # The total payout amount for the user
        }


def get_deposits_per_stokvel(stokvel_name: str):
    """
    Retrieve total deposit details for a specific stokvel based on its name.

    Args:
        stokvel_name (str): The name of the stokvel.

    Returns:
        dict: A dictionary containing the total deposit amount for the given stokvel.
    """
    # Updated query to fetch the total deposits using stokvel_id from the STOKVELS table
    query = """
    SELECT
        SUM(t.amount) AS total_deposits
    FROM
        TRANSACTIONS t
    WHERE
        t.stokvel_id = (SELECT stokvel_id FROM STOKVELS WHERE stokvel_name = :stokvel_name)
        AND t.tx_type = 'DEPOSIT'
    GROUP BY
        t.stokvel_id;
    """

    # Executing the query using the SQLite connection
    with sqlite_conn.connect() as conn:
        result = conn.execute(text(query), {"stokvel_name": stokvel_name}).fetchone()

        if not result:
            return {
                "error": f"No data found for the given stokvel name: {stokvel_name}"
            }

        # Building the result dictionary from the query response
        return {
            "stokvel_name": stokvel_name,
            "total_deposits": result[0],
        }


def get_nr_of_active_users_per_stokvel(stokvel_name: str):
    """
    Retrieve the number of active members for a specific stokvel based on its name.

    Args:
        stokvel_name (str): The name of the stokvel.

    Returns:
        dict: A dictionary containing the number of active members in the stokvel.
    """
    # Corrected query to fetch the count of active members for the stokvel
    query = """
    SELECT
        COUNT(sm.user_id) as nr_of_active_users_in_stokvel
    FROM
        STOKVEL_MEMBERS sm
    WHERE
        sm.stokvel_id = (SELECT s.stokvel_id FROM STOKVELS s WHERE s.stokvel_name = :stokvel_name)
        AND sm.active_status = 'active';
    """
    # Executing the query using the SQLite connection
    with sqlite_conn.connect() as conn:
        result = conn.execute(text(query), {"stokvel_name": stokvel_name}).fetchone()

        if not result or result[0] is None:
            return {
                "error": f"No data found for the given stokvel name: {stokvel_name}"
            }

        # Building the result dictionary from the query response
        return {
            "stokvel_name": stokvel_name,
            "nr_of_active_users": result[0],
        }


def get_stokvel_constitution(phone_number: str, stokvel_name: str):
    """
    Retrieve minimum contribution amount and maximum number of members for a specific stokvel based on its name and user's phone number.

    Args:
        phone_number (str): The user's phone number.
        stokvel_name (str): The name of the stokvel to filter by.

    Returns:
        dict: A dictionary containing the stokvel's constitution details, including the minimum contribution amount,
              maximum number of contributors, and creation date.
    """
    # Step 1: Format the phone number (if necessary, similar to `extract_whatsapp_number`)
    formatted_number = extract_whatsapp_number(phone_number)

    # Step 2: SQL query to find stokvel details using USERS to validate membership
    query = """
    SELECT
        s.min_contributing_amount AS minimum_contributing_amount,
        s.max_number_of_contributors AS max_number_of_contributors,
        s.created_at AS creation_date
    FROM
        STOKVELS s
    JOIN
        STOKVEL_MEMBERS sm ON s.stokvel_id = sm.stokvel_id
    JOIN
        USERS u ON sm.user_id = u.user_id
    WHERE
        s.stokvel_name = :stokvel_name
        AND u.user_number = :user_number;
    """

    # Step 3: Execute the query using the SQLite connection
    with sqlite_conn.connect() as conn:
        result = conn.execute(
            text(query), {"stokvel_name": stokvel_name, "user_number": formatted_number}
        ).fetchone()

        if not result:
            return {
                "error": f"No data found for the given stokvel name: {stokvel_name} and phone number: {phone_number}."
            }

        # Step 4: Build the result dictionary from the query response
        return {
            "stokvel_name": stokvel_name,
            "minimum_contributing_amount": result[0],
            "max_number_of_contributors": result[1],
            "creation_date": result[2],
        }


def get_stokvel_id_by_name(stokvel_name) -> Optional[str]:
    """
    docstring
    """
    print(stokvel_name)
    query = "SELECT stokvel_id FROM STOKVELS WHERE stokvel_name = :stokvel_name"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"stokvel_name": stokvel_name})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return result

        return None


def get_admin_by_stokvel(stokvel_id):
    """
    Returns admins cellphone number
    """
    print(stokvel_id)
    query = """
        SELECT
            u.user_number
        FROM
            USERS u
        WHERE
            u.user_id = (SELECT a.user_id FROM ADMIN a WHERE a.stokvel_id = :stokvel_id);
    """
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"stokvel_id": stokvel_id})
        result = cursor.fetchone()[0]
        print(result)
        if result:
            return result
        return None
    

def get_iso_with_default_time(date_string: str) -> str:
    try:
        # Try parsing the date string with time
        date_object = datetime.fromisoformat(date_string)
    except ValueError:
        # If no time is provided, append 12:00 AM (00:00:00) and parse again
        date_object = datetime.fromisoformat(date_string + 'T00:00:00')
    
    # Return the date in ISO format with Z for UTC timezone
    return date_object.isoformat() + 'Z'

def format_contribution_period_string(contribution_period: str):
    if contribution_period == "Days":
        contribution_period = "D"
    elif contribution_period == "Months":
        contribution_period = "M"
    elif contribution_period == "Weeks":
        contribution_period = "W"
    elif contribution_period == "Years":
        contribution_period = "Y"
    elif contribution_period == "30 Seconds":
        contribution_period = "S"
    return contribution_period
    

# def get_all_applications(user_id):
#     """
#     docstring
#     """
#     query = """
#         SELECT
#             a.id,
#             a.stokvel_id,
#             a.user_id,
#             a.user_contribution,
#             a.AppStatus,
#             a.AppDate,
#             u.user_number,
#             u.user_name,
#             u.user_surname,
#             s.stokvel_name
#         FROM APPLICATIONS a
#         JOIN USERS u ON a.user_id = u.user_id
#         JOIN STOKVELS s ON a.stokvel_id = s.stokvel_id
#         JOIN ADMIN ad ON s.stokvel_id = ad.stokvel_id  -- Join ADMIN to check admin link
#         WHERE ad.user_id = :user_id          -- Check if requesting number is an admin
#         AND a.AppStatus = 'Application Submitted'    -- Application status filter
#     """

#     with sqlite_conn.connect() as conn:
#         cursor = conn.execute(text(query), {"user_id": user_id})
#         result = cursor.fetchall()

#         applications = [
#             {
#                 "id": i[0],
#                 "stokvel_id": i[1],
#                 "user_id": i[2],
#                 "AppStatus": i[3],
#                 "AppDate": i[4],
#                 "user_number": i[5],
#                 "user_name": i[6],
#                 "user_surname": i[7],
#                 "stokvel_name": i[8],
#             }
#             for i in result
#         ]

#         return applications


def get_all_applications(user_id):
    """
    Fetches all applications for a stokvel where the user is an admin.
    Returns the applications, including user contributions.
    """
    query = """
        SELECT
            a.id,
            a.stokvel_id,
            a.user_id,
            a.user_contribution,
            a.AppStatus,
            a.AppDate,
            u.user_number,
            u.user_name,
            u.user_surname,
            s.stokvel_name
        FROM APPLICATIONS a
        JOIN USERS u ON a.user_id = u.user_id
        JOIN STOKVELS s ON a.stokvel_id = s.stokvel_id
        JOIN ADMIN ad ON s.stokvel_id = ad.stokvel_id  -- Join ADMIN to check admin link
        WHERE ad.user_id = :user_id                    -- Check if requesting number is an admin
        AND a.AppStatus = 'Application Submitted'      -- Application status filter
    """

    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"user_id": user_id})
        result = cursor.fetchall()

        applications = [
            {
                "id": i[0],
                "stokvel_id": i[1],
                "user_id": i[2],
                "user_contribution": i[3],  # Add user contribution here
                "AppStatus": i[4],
                "AppDate": i[5],
                "user_number": i[6],
                "user_name": i[7],
                "user_surname": i[8],
                "stokvel_name": i[9],
            }
            for i in result
        ]

        return applications



def insert_stokvel(
    stokvel_id: Optional[int],
    stokvel_name: str,  # unique constraint here
    ILP_wallet: str,
    MOMO_wallet: str,
    total_members: Optional[int],
    min_contributing_amount: float,
    max_number_of_contributors: int,
    total_contributions: float,
    start_date: str,
    end_date: str,
    payout_frequency_duration: str,
    contribution_period: str,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> str:
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
            stokvel_id,
            stokvel_name,
            ILP_wallet,
            MOMO_wallet,
            total_members,
            min_contributing_amount,
            max_number_of_contributors,
            total_contributions,
            start_date,
            end_date,
            payout_frequency_duration,
            contribution_period,
            created_at,
            updated_at
        ) VALUES (
            :stokvel_id,
            :stokvel_name,
            :ILP_wallet,
            :MOMO_wallet,
            :total_members,
            :min_contributing_amount,
            :max_number_of_contributors,
            :total_contributions,
            :start_date,
            :end_date,
            :payout_frequency_duration,
            :contribution_period,
            :created_at,
            :updated_at
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
        "total_contributions": total_contributions,
        "created_at": created_at,
        "updated_at": updated_at,
        "start_date": start_date,
        "end_date": end_date,
        "payout_frequency_duration": payout_frequency_duration,
        "contribution_period": contribution_period,
    }

    stokvel_current_id = ""

    try:
        with sqlite_conn.connect() as conn:
            if stokvel_id is None:
                stokvel_current_id = get_next_unique_id(conn, "STOKVELS", "stokvel_id")
                parameters["stokvel_id"] = stokvel_current_id

            print("Connected in stokvel insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
                print("insert stokvel successful")

            else:
                print("Insert failed.")

            return stokvel_current_id

    except sqlite3.Error as e:
        print(f"Error occurred during insert stokvel: {e}")
        raise e

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e


def check_if_stokvel_member(user_id, stokvel_id):
    """
    Checks if a user is already a member of a stokvel
    """
    query = f"SELECT * FROM STOKVEL_MEMBERS WHERE user_id = {user_id} AND stokvel_id = {stokvel_id}"

    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query))
        result = cursor.fetchall()

        if len(result) > 0:
            return True

        return False


# def insert_stokvel_member(
#     application_id: Optional[int],
#     stokvel_id: Optional[str],  # unique constraint here
#     user_id: Optional[str],
#     user_contribution: Optional[float],
#     user_token: Optional[str],
#     user_url:  Optional[str],
#     user_quote_id: Optional[str],
#     stokvel_token:Optional[str],
#     stokvel_url:Optional[str],
#     strokvel_quote_id:Optional[str],
#     created_at: Optional[str] = None,
#     updated_at: Optional[str] = None,
# ) -> List:
#     """
#     Inserts a new stokvel member into the STOKVEL_MEMBERS table.
#     Raises:
#         Exception: If an error occurs during insert.
#     """
#     # Need to look at refactoring this

#     print("user id from inserting member: ", user_id)

#     if created_at is None:
#         created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     if updated_at is None:
#         updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     insert_query = """
#         INSERT INTO STOKVEL_MEMBERS (
#             stokvel_id, user_id, user_contribution, created_at, updated_at
#         ) VALUES (
#             :stokvel_id, :user_id, : user_contribution, :created_at, :updated_at
#         )
#         """

#     # Parameter dictionary for executing the query
#     parameters = {
#         "stokvel_id": stokvel_id,
#         "user_id": user_id,
#         "user_contribution":user_contribution,
#         "created_at": created_at,
#         "updated_at": updated_at,
#     }
#     declined_applications_list = []
#     try:
#         with sqlite_conn.connect() as conn:
#             print("Connected in stokvel_members insert")
#             if check_available_space_in_stokvel(stokvel_id):
#                 if not check_if_stokvel_member(user_id, stokvel_id):
#                     update_application_status(application_id, "Approved")
#                     conn.execute(text(insert_query), parameters)
#                     conn.commit()
#                 else:
#                     print(
#                         f"could not insert, user {user_id} is already a member of this stokvel {stokvel_id}"
#                     )
#                     raise sqlite3.Error("User is already a member of this stokvel")
#             else:
#                 print(f"Could not insert, stokvel {stokvel_id} is full")

#                 # Find the most recently accepted application for the stokvel
#                 latest_application_query = """
#                     SELECT * FROM APPLICATIONS
#                     WHERE stokvel_id = :stokvel_id AND AppStatus = 'Approved'
#                     ORDER BY AppDate DESC
#                     LIMIT 1
#                 """
#                 latest_application = conn.execute(
#                     text(latest_application_query), {"stokvel_id": stokvel_id}
#                 ).fetchone()

#                 print("latest app = ", latest_application)

#                 if latest_application:
#                     print("AGAIN latest app = ", latest_application)

#                     latest_created_at = latest_application[4]
#                     print(
#                         f"Latest accepted application created at: {latest_created_at}"
#                     )

#                     # Decline all applications after the latest accepted application
#                     decline_applications_query = """
#                         UPDATE APPLICATIONS
#                         SET AppStatus = 'Declined'
#                         WHERE stokvel_id = :stokvel_id AND AppDate > :latest_created_at
#                     """
#                     conn.execute(
#                         text(decline_applications_query),
#                         {
#                             "stokvel_id": stokvel_id,
#                             "latest_created_at": latest_created_at,
#                         },
#                     )

#                     conn.commit()

#                     # Fetch IDs of the declined applications after the update
#                     # declined_apps_query = """
#                     #     SELECT id, AppStatus, user_id FROM APPLICATIONS
#                     #     WHERE stokvel_id = :stokvel_id AND AppStatus = 'Declined' AND AppDate > :latest_created_at
#                     # """

#                     declined_users_query = """
#                         SELECT u.user_number FROM APPLICATIONS a
#                         JOIN USERS u ON a.user_id = u.user_id
#                         WHERE a.stokvel_id = :stokvel_id AND a.AppStatus = 'Declined' AND a.AppDate > :latest_created_at
#                     """

#                     declined_apps_numbers = conn.execute(
#                         text(declined_users_query),
#                         {
#                             "stokvel_id": stokvel_id,
#                             "latest_created_at": latest_created_at,
#                         },
#                     ).fetchall()

#                     # print(declined_apps_numbers)

#                     # Store the IDs of the declined applications
#                     declined_applications_list = [
#                         app[0] for app in declined_apps_numbers
#                     ]
#                     print("Declined Applications IDs:", declined_applications_list)

#         return declined_applications_list

#     except sqlite3.Error as e:
#         print(f"Error occurred during insert: {e}")
#         raise e
#     except Exception as e:
#         print(f"Error occurred during insert: {e}")
#         raise e


def insert_stokvel_member(
    application_id: Optional[int],
    stokvel_id: Optional[str],
    user_id: Optional[str],
    user_contribution: Optional[float],
    user_token: Optional[str],
    user_url: Optional[str],
    user_quote_id: Optional[str],
    stokvel_token: Optional[str],
    stokvel_url: Optional[str],
    stokvel_quote_id: Optional[str],
    stokvel_initial_payment_needed:Optional[int],
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> List:
    """
    Inserts a new stokvel member into the STOKVEL_MEMBERS table, accounting for token, URL, and quote fields.
    Raises:
        Exception: If an error occurs during insert.
    """

    print("User ID from inserting member: ", user_id)

    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if updated_at is None:
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Updated insert query with actual database column names
    insert_query = """
        INSERT INTO STOKVEL_MEMBERS (
            stokvel_id, user_id, contribution_amount, user_payment_token, user_payment_URI, user_quote_id, 
            stokvel_payment_token, stokvel_payment_URI, stokvel_quote_id, stokvel_initial_payment_needed, created_at, updated_at
        ) VALUES (
            :stokvel_id, :user_id, :contribution_amount, :user_payment_token, :user_payment_URI, :user_quote_id, 
            :stokvel_payment_token, :stokvel_payment_URI, :stokvel_quote_id, :stokvel_initial_payment_needed, :created_at, :updated_at
        )
    """

    # Parameter dictionary for executing the query, with the correct column names
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "contribution_amount": user_contribution,
        "user_payment_token": user_token,
        "user_payment_URI": user_url,
        "user_quote_id": user_quote_id,
        "stokvel_payment_token": stokvel_token,
        "stokvel_payment_URI": stokvel_url,
        "stokvel_quote_id": stokvel_quote_id,
        "stokvel_initial_payment_needed":1,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    declined_applications_list = []

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in stokvel_members insert")
            if check_available_space_in_stokvel(stokvel_id):
                if not check_if_stokvel_member(user_id, stokvel_id):
                    update_application_status(application_id, "Approved") #what is going on here lol - issue: members are applying to be in their own stokvel and there is an error?
                    conn.execute(text(insert_query), parameters)
                    conn.commit()
                else:
                    print(
                        f"Could not insert, user {user_id} is already a member of this stokvel {stokvel_id}"
                    )
                    raise sqlite3.Error("User is already a member of this stokvel")
            else:
                print(f"Could not insert, stokvel {stokvel_id} is full")

                # Handle declined applications logic here

        return declined_applications_list

    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise e
    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e
    
def check_update_stokvel_initial_payout_required(stokvel_id, user_id):
    query = """
    SELECT stokvel_initial_payout_required 
    FROM STOKVEL_MEMBERS 
    WHERE user_id = :user_id AND stokvel_id = :stokvel_id
    """
    parameters = {
        "user_id": user_id,
        "stokvel_id": stokvel_id
    }

    try:
        with sqlite_conn.connect() as conn:
            result = conn.execute(text(query), parameters)
            payout_required = result.fetchone()  # Fetch one record

            if payout_required is None:
                print(f"No record found for stokvel_id: {stokvel_id} and user_id: {user_id}")
                return None

            print(f"Initial payout required: {payout_required[0]}")
            return payout_required[0]  # Return the value of `stokvel_initial_payout_required`

    except sqlite3.Error as e:
        print(f"Error retrieving stokvel initial payout: {e}")
        raise e

def update_stokvel_initial_payout_required_to_zero(stokvel_id, user_id):
    update_query = """
    UPDATE STOKVEL_MEMBERS
    SET stokvel_initial_payout_required = 0
    WHERE stokvel_id = :stokvel_id AND user_id = :user_id
    """
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id
    }

    try:
        with sqlite_conn.connect() as conn:
            result = conn.execute(text(update_query), parameters)
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Successfully updated stokvel_initial_payout_required to 0 for stokvel_id: {stokvel_id} and user_id: {user_id}")
            else:
                print(f"No records found to update for stokvel_id: {stokvel_id} and user_id: {user_id}")
                
    except sqlite3.Error as e:
        print(f"Error updating stokvel initial payout required: {e}")
        raise e



def get_all_stokvels():
    """
    Retrieve all stokvels from database
    """
    try:
        with sqlite_conn.connect() as conn:

            print("Connected in stokvel_members insert")
            cursor = conn.execute(text("SELECT * FROM stokvels;"))
            stokvels = cursor.fetchall()

            # print(stokvels)

        stokvels_list = [
            {
                "stokvel_id": stokvel[0],
                "stokvel_name": stokvel[1],
                "ILP_wallet": stokvel[2],
                "MOMO_wallet": stokvel[3],
                "total_members": (
                    stokvel[4] if stokvel[4] is not None else 0
                ),  # Set to 0 if None
                "min_contributing_amount": stokvel[5],
                "max_number_of_contributors": stokvel[6],
                "total_contributions": stokvel[7],
                "created_at": stokvel[8],
                "updated_at": stokvel[9],
                "start_date": stokvel[10],
                "end_date": stokvel[11],
                "payout_frequency_int": stokvel[12],
                "payout_frequency_period": stokvel[13],
                "available_space": max(
                    (stokvel[6] if stokvel[6] is not None else 0)
                    - (stokvel[4] if stokvel[4] is not None else 0),
                    0,
                ),  # Calculate available space
            }
            for stokvel in stokvels
        ]

        return stokvels_list

    except sqlite3.Error as e:
        print(f"Error occurred during insert: {e}")
        raise e

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e


def insert_admin(
    stokvel_id: Optional[str],  # unique constraint here
    stokvel_name: str,
    user_id: Optional[str],
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
    print("user id from inserting admin: ", user_id)

    # Parameter dictionary for executing the query
    parameters = {
        "id": None,
        "stokvel_id": stokvel_id,
        "stokvel_name": stokvel_name,
        "user_id": user_id,
        "total_contributions": total_contributions,
        "total_members": total_members,
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in stokvel_admin insert")
            parameters["id"] = get_next_unique_id(conn, "ADMIN", "id")

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


def update_stokvel_members_count(stokvel_id):
    """
    Updates the stokvel members count
    """

    count_query = "SELECT COUNT(*) FROM STOKVEL_MEMBERS WHERE stokvel_id = :stokvel_id;"
    parameters = {"stokvel_id": stokvel_id}

    try:
        with sqlite_conn.connect() as conn:
            print("Connected to the database for stokvel members update")

            cursor = conn.execute(text(count_query), parameters)
            total_members = cursor.fetchone()[0]

            update_query = "UPDATE STOKVELS SET total_members = :total_members WHERE stokvel_id = :stokvel_id;"

            update_parameters = {
                "stokvel_id": stokvel_id,
                "total_members": total_members,
            }

            conn.execute(text(update_query), update_parameters)
            conn.commit()

            print(
                f"Updated total_members for stokvel_id {stokvel_id} to {total_members}"
            )

    except Exception as e:
        print(f"An error occurred: {e}")


def check_application_pending_approved(user_id, stokvel_id):
    """
    Check if a user already has a pending application in the database.
    """
    query = """SELECT * FROM APPLICATIONS
    WHERE user_id = :user_id
    AND stokvel_id = :stokvel_id
    AND (AppStatus = 'Application Submitted' or AppStatus = 'Approved');"""

    parameters = {"user_id": user_id, "stokvel_id": stokvel_id}

    members_query = "select * from STOKVEL_MEMBERS where user_id = :user_id and stokvel_id = :stokvel_id;"
    members_parameters = {"user_id": user_id, "stokvel_id": stokvel_id}

    try:
        with sqlite_conn.connect() as conn:
            cursor = conn.execute(text(query), parameters)
            result = cursor.fetchone()
            if result is not None:
                print("User has an application in the database")
                return True

            print("No app in db for this user")
            members_cursor = conn.execute(text(members_query), members_parameters)
            members_result = members_cursor.fetchone()
            if members_result is not None:
                print("user is a member in the database")
                return True
            return False
    except Exception as e:
        print(f"An error occurred: {e}")


def check_available_space_in_stokvel(stokvel_id):
    """Checks that there is space available in a stokvel before inserting a user"""

    query = "SELECT total_members, max_number_of_contributors FROM STOKVELS WHERE stokvel_id = :stokvel_id;"
    parameters = {"stokvel_id": stokvel_id}

    print("checking space of : ", str(stokvel_id))

    try:
        with sqlite_conn.connect() as conn:
            cursor = conn.execute(text(query), parameters)
            contributors, max_contributors = cursor.fetchone()
            contributors = 0 if contributors is None else contributors
            # print('contribs = ', contributors, ' max contributors ' + max_contributors)
            return contributors < max_contributors

    except Exception as e:
        print(f"An error occurred: {e}")


def insert_stokvel_join_application(
    stokvel_id: Optional[str],  # unique constraint here
    user_id: Optional[str],
    user_contribution: Optional[float],
    app_status: Optional[str] = None,
    app_date: Optional[str] = None,
):
    """
    docstring
    """

    if app_date is None:
        app_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if app_status is None:
        app_status = "Application Submitted"

    insert_query = """
        INSERT INTO APPLICATIONS (
            id, stokvel_id, user_id, user_contribution, AppStatus, AppDate
        ) VALUES (
            :id, :stokvel_id, :user_id, :user_contribution, :AppStatus, :AppDate
        )
        """

    parameters = {
        "id": None,
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "user_contribution":user_contribution,
        "AppStatus": app_status,
        "AppDate": app_date,
    }

    try:
        with sqlite_conn.connect() as conn:
            if check_available_space_in_stokvel(stokvel_id):
                if stokvel_id is None:
                    current_application_id = get_next_unique_id(
                        conn, "APPLICATIONS", "id"
                    )
                    parameters["id"] = current_application_id

                print("Connected in application insert")
                result = conn.execute(text(insert_query), parameters)
                conn.commit()

                if result.rowcount > 0:
                    print(f"Insert successful, {result.rowcount} row(s) affected.")
                    print("insert application successful")

                else:
                    print("Insert failed.")
            else:
                print("No space in stokvel")

            # return current_application_id

    except sqlite3.Error as e:
        print(f"Error occurred during insert application: {e}")
        raise e

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise e


def update_application_status(app_id: Optional[int], app_status: str):
    """docstring"""
    update_query = """
        UPDATE APPLICATIONS
        SET
            AppStatus = :AppStatus
        WHERE
            id = :id
    """

    parameters = {
        "id": app_id,
        "AppStatus": app_status,
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in application update")
            result = conn.execute(text(update_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
                print("insert application successful")

            else:
                print("Insert failed.")

        # return current_application_id

    except sqlite3.Error as e:
        print(f"Error occurred during insert application: {e}")
        raise e

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a application: {e}")  # Stops execution by raising the error

def add_url_token(userid, stokvel_id, url, token):
    try:
        with sqlite_conn.connect() as conn:
            print("Connected to the database for stokvel members update TOKEN details")
            
            update_query = "UPDATE STOKVEL_MEMBERS SET url = :url, token = :token WHERE stokvel_id = :stokvel_id AND user_id = :user_id;"
            update_parameters = {
                "stokvel_id": stokvel_id,
                "user_id": userid,
                "url":url,
                "token":token
            }
            
            conn.execute(text(update_query), update_parameters)
            conn.commit() 
            
            print(f"Updated token for stokvel_id {stokvel_id} and usser_id {userid} to {token}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
def calculate_number_periods(payout_period, start_date, end_date):
        # Parse the start and end dates as datetime objects using the correct format
    start_date = datetime.strptime(start_date, "%Y-%m-%d")  # Include seconds in the format
    end_date = datetime.strptime(end_date, "%Y-%m-%d")      # Include seconds in the format

    # Calculate the difference based on the payout period
    date_difference = (end_date - start_date).days  # Get the total days difference
    no_periods = 0

    if payout_period == 'Days':
        no_periods = date_difference  # Total days
        period_delta = timedelta(days=1)  # Increment by 1 day
    elif payout_period == 'Weeks':
        no_periods = date_difference // 7  # Total weeks
        period_delta = timedelta(weeks=1)  # Increment by 1 week
    elif payout_period == 'Months':
        diff = relativedelta(end_date, start_date)
        no_periods = diff.years * 12 + diff.months  # Total months
        period_delta = relativedelta(months=1)  # Increment by 1 month
    elif payout_period == 'Years':
        diff = relativedelta(end_date, start_date)
        no_periods = diff.years  # Total years
        period_delta = relativedelta(years=1)  # Increment by 1 year
    elif payout_period == '30 Seconds':
        # Calculate the total number of seconds in the period
        total_seconds = (end_date - start_date).total_seconds()
        print('TOTAL SECONDS ', total_seconds)
        no_periods = int(total_seconds // 30)  # Total number of 30-second periods
        period_delta = timedelta(seconds=30)  # Increment by 30 seconds
    else:
        raise ValueError("Invalid payout period specified.")
    
    return no_periods

def double_number_periods_for_same_daterange(period):
    period_duration =  ""
    number_of_periods_coverted = ""
    if period == 'Years':
        period_duration = "M"
        number_of_periods_coverted = 6
    elif period == "Months":
        period_duration == "w"
        number_of_periods_coverted = 2
    elif period == "Weeks":
        period_duration = "D"
        number_of_periods_coverted = 3
    elif period == "Days":
        period_duration = "H"
        number_of_periods_coverted = "T12"
    elif period == "30 Seconds":
        period_duration = "S"
        number_of_periods_coverted = "T15"
    print(period, ' ',period_duration, ' ', number_of_periods_coverted)
    return period_duration, number_of_periods_coverted

def update_user_active_status(userid, stokvelid, grantaccepted):
    """
    Updates the active status of a user in a stokvel based on whether their grant is accepted or not.
    """
    if grantaccepted:
        # If grant is accepted, set status to 'active'
        query = """
            UPDATE STOKVEL_MEMBERS
            SET active_status = :status
            WHERE user_id = :userid AND stokvel_id = :stokvelid
        """
        params = {
            "status": "active",
            "userid": userid,
            "stokvelid": stokvelid,
        }
    else:
        # If grant is not accepted, set status to 'inactive'
        query = """
            UPDATE STOKVEL_MEMBERS
            SET active_status = :status
            WHERE user_id = :userid AND stokvel_id = :stokvelid
        """
        params = {
            "status": "inactive",
            "userid": userid,
            "stokvelid": stokvelid,
        }

    # Execute the query
    try:
        with sqlite_conn.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()
            print(f"Updated user {userid} status to {params['status']} for stokvel {stokvelid}.")
    except sqlite3.Error as e:
        print(f"Error updating user status: {e}")
        raise e


# First attempt at transaction table

# from .sql_connection import sql_connection
import sqlite3
from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")


def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(text(f"SELECT MAX({id_column}) FROM {table_name}")).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1


def insert_transaction(conn, user_id, stokvel_id, amount, tx_type, tx_date):
    """
    Insert a transaction into the TRANSACTIONS table with success and exception handling.
    """
    try:
        # Insert the transaction into the table
        # Get the next unique id for the transaction
        transaction_id = get_next_unique_id(conn, "TRANSACTIONS", "id")
        conn.execute(
            text(
                """
            INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
            VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)
            """
            ),
            {
                "id": transaction_id,
                "user_id": user_id,
                "stokvel_id": stokvel_id,
                "amount": amount,
                "tx_type": tx_type,
                "tx_date": tx_date,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        )

        conn.commit()  # Commit the transaction to the database

        print(f"Transaction with ID {transaction_id} was successfully added.")

    except Exception as e:
        print(f"Failed to insert transaction. Error: {str(e)}")

def update_max_nr_of_contributors(stokvel_name: str, max_nr_of_contributors: float):
    """
    Update the max number of contributors

    Args:
        stokvel_name
        user_input

    Returns:
        str: Success or failure message.
    """

    # SQL query to update user name
    update_query = """
    UPDATE STOKVELS
    SET max_number_of_contributors = :max_nr_of_contributors
    WHERE stokvel_id = (SELECT stokvel_id FROM STOKVELS WHERE stokvel_name = :stokvel_name);
    """

    with sqlite_conn.connect() as conn:
        conn.execute(
            text(update_query), {"stokvel_name": stokvel_name, "max_nr_of_contributors": max_nr_of_contributors}
        )
        conn.commit()

def update_stokvel_name(stokvel_name: str, new_stokvelname: float):
    """
    Update the max number of contributors

    Args:
        stokvel_name
        user_input

    Returns:
        str: Success or failure message.
    """

    # SQL query to update user name
    update_query = """
    UPDATE STOKVELS
    SET stokvel_name = :new_stokvelname
    WHERE stokvel_id = (SELECT stokvel_id FROM STOKVELS WHERE stokvel_name = :stokvel_name);
    """

    with sqlite_conn.connect() as conn:
            conn.execute(
                text(update_query), {"stokvel_name": stokvel_name, "new_stokvelname": new_stokvelname}
            )
            conn.commit()


def get_stokvel_monthly_interest(stokvel_id: Optional[str]) -> Dict[str, float]:
    """
    Get the accumulated interest for a stokvel in the current savings period.

    :param stokvel_id: The ID of the stokvel to check interest for.
    :return: A dictionary of montlhy interest values keyed by the date.
    """
    engine = sqlite_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # Get most recent payout date from STOKVELS table
            query = text(
                "SELECT MAX(tx_date) FROM TRANSACTIONS WHERE tx_type='PAYOUT' AND stokvel_id = :stokvel_id"
            )
            result = conn.execute(query, {"stokvel_id": stokvel_id})
            prev_payout = result.scalar()

            if not prev_payout:
                query = text(
                    "SELECT created_at FROM STOKVELS WHERE stokvel_id = :stokvel_id"
                )
                result = conn.execute(query, {"stokvel_id": stokvel_id})
                prev_payout = result.scalar()

            # Get all interest values from the INTEREST table where the stokvel_id matches
            # and date is after the previous payout
            interest_query = text(
                """
                SELECT interest_value, date
                FROM INTEREST
                WHERE stokvel_id = :stokvel_id
                AND date > :prev_payout
            """
            )

            interest_result = conn.execute(
                interest_query, {"stokvel_id": stokvel_id, "prev_payout": prev_payout}
            )

            # Store the interest values in a dictionary (keyed by date)
            interest = {row[1]: row[0] for row in interest_result}

            transaction.commit()

            return interest

        except Exception as e:
            transaction.rollback()
            print(f"There was an error retrieving the SQL data: {e}")
            return {}


def get_user_interest(user_id: int, stokvel_id: int) -> float:
    """
    Get the accumulated interest for a user in the current savings period.

    :param user_id: the ID of the user to check interest for.
    :param stokvel_id: The ID of the stokvel to check interest for.
    :return: Total user interest for the savings period.
    """

    stokvel_interest = get_stokvel_monthly_interest(stokvel_id)

    start_date = next(iter(stokvel_interest))

    start_date = start_date[:7]

    # Convert start_date to a datetime object and calculate the date one month before
    start_date_dt = datetime.strptime(start_date, "%Y-%m")
    previous_month_date = (
        (start_date_dt - timedelta(days=1)).replace(day=1).strftime("%Y-%m")
    )

    engine = sqlite_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # SQL query to get monthly sums of users deposits after the start_date
            user_deposit_query = text(
                """
                SELECT
                    strftime('%Y-%m', tx_date) AS month,  -- Get the year-month part of the date
                    SUM(amount) AS total_deposit
                FROM TRANSACTIONS
                WHERE user_id = :user_id
                AND stokvel_id = :stokvel_id
                AND tx_type = 'DEPOSIT'
                AND tx_date > :previous_month_date  -- Start from the month before the interest period
                GROUP BY strftime('%Y-%m', tx_date)  -- Group by year-month
            """
            )

            user_deposit_result = conn.execute(
                user_deposit_query,
                {
                    "user_id": user_id,
                    "stokvel_id": stokvel_id,
                    "previous_month_date": previous_month_date,
                },
            )

            # Store the deposit sums in a dictionary (keyed by year-month)
            user_monthly_deposits = {row[0]: row[1] for row in user_deposit_result}

            # SQL query to get monthly total deposits into stokvel after the start_date
            stokvel_deposits_query = text(
                """
                SELECT strftime('%Y-%m', tx_date) AS month,  -- Get the year-month part of the date
                    SUM(amount) AS total_deposit_stokvel
                FROM TRANSACTIONS
                WHERE stokvel_id = :stokvel_id
                AND tx_type = 'DEPOSIT'
                AND tx_date > :previous_month_date  -- Start from the month before the interest period
                GROUP BY strftime('%Y-%m', tx_date)  -- Group by year-month
            """
            )

            stokvel_deposits_result = conn.execute(
                stokvel_deposits_query,
                {"stokvel_id": stokvel_id, "previous_month_date": previous_month_date},
            )

            # Store stokvel contributions in a dictionary keyed by year-month
            stokvel_monthly_deposits = {
                row[0]: row[1] for row in stokvel_deposits_result
            }

            # Calculate the user's total interest for the savings period
            user_total_interest = 0.00
            user_deposit = 0
            stokvel_deposit = 0
            for month, interest_value in stokvel_interest.items():
                # Calculate the previous month (shift the deposits back by one month)
                previous_month = (
                    (datetime.strptime(month[:7], "%Y-%m") - timedelta(days=1))
                    .replace(day=1)
                    .strftime("%Y-%m")
                )

                # If the previous month's deposits are available
                if (
                    previous_month in user_monthly_deposits
                    and previous_month in stokvel_monthly_deposits
                ):
                    user_deposit += user_monthly_deposits[previous_month]
                    stokvel_deposit += stokvel_monthly_deposits[previous_month]

                    # Calculate the user's share of the interest for the current month
                    user_interest = (user_deposit / stokvel_deposit) * interest_value
                    user_total_interest += user_interest

            user_total_interest = round(user_total_interest, 2)

            transaction.commit()

            return user_total_interest

        except Exception as e:
            transaction.rollback()
            print(f"There was an error retrieving the SQL data: {e}")
            return 0.00


# Contributions function


def contribution_trigger():
    """
    Check if the contribution process should be kicked off based on the NextDate in the database.
    """

    input_date = datetime.now().date()  # Only compare the date part
    tx_date = datetime.now()

    try:
        with sqlite_conn.connect() as conn:
            # Query to check if the NextDate matches the input date
            contribution_triggers = conn.execute(
                text(
                    """
                    SELECT stokvel_id
                    FROM CONTRIBUTIONS
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                {"input_date": input_date},
            ).fetchall()  # Use fetchall() to get all stokvel_ids

            # If results are found, kick off the contribution process
            if contribution_triggers:
                for trigger in contribution_triggers:
                    stokvel_id = trigger[0]

                    all_members = conn.execute(
                        text(
                            """
                            SELECT *
                            FROM STOKVEL_MEMBERS
                            WHERE stokvel_id = :stokvel_id
                            """
                        ),
                        {"stokvel_id": stokvel_id},
                    ).fetchall()  # Fetch all members

                    for member in all_members:
                        try:
                            user_id = member[2]
                            amount = member[5]
                            user_quote_id = member[9]
                            tx_type = "DEPOSIT"
                            tx_date = tx_date
                            manageUrl = member[7]
                            previousToken = member[8]

                            sender_wallet_address = conn.execute(
                                text(
                                    """
                                    SELECT ILP_wallet
                                    FROM USERS
                                    WHERE user_id = :user_id
                                    """
                                ),
                                {"user_id": user_id},
                            ).fetchone()

                            receiving_wallet_address = conn.execute(
                                text(
                                    """
                                    SELECT ILP_wallet
                                    FROM STOKVELS
                                    WHERE stokvel_id = :stokvel_id
                                    """
                                ),
                                {"stokvel_id": stokvel_id},
                            ).fetchone()

                            # Check if a payment is needed based on user_quote_id
                            if user_quote_id is not None:
                                # Create initial payment
                                # create_inital_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, user_quote_id)

                                conn.execute(
                                    text(
                                        """
                                        UPDATE STOKVEL_MEMBERS
                                        SET user_quote_id = NULL
                                        WHERE user_id = :user_id
                                        """
                                    ),
                                    {"user_id": user_id},
                                )

                                insert_transaction(
                                    conn, user_id, stokvel_id, amount, tx_type, tx_date
                                )

                            else:
                                # Create contribution payment
                                # create_contribution_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken)

                                insert_transaction(
                                    conn, user_id, stokvel_id, amount, tx_type, tx_date
                                )

                                print(f"Ran the recurring payment")

                        except Exception as e:
                            print(
                                f"Error attempting to make contribution for user {user_id}: {str(e)}"
                            )
                            return False

            else:
                print("No contributions scheduled for today.")
                return True  # Indicate no contributions found but process is complete

    except Exception as e:
        print(f"Error checking contribution trigger: {str(e)}")
        return False


# Payout  function


def payout_trigger():
    """
    Check if the payout process should be kicked off based on the NextDate in the database.
    """

    input_date = datetime.now().date()  # Only compare the date part
    tx_date = datetime.now()

    try:
        with sqlite_conn.connect() as conn:
            # Query to check if the NextDate matches the input date
            payout_triggers = conn.execute(
                text(
                    """
                    SELECT stokvel_id
                    FROM PAYOUTS
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                {"input_date": input_date},
            ).fetchall()  # Use fetchall() to get all stokvel_ids

            # If results are found, kick off the contribution process
            if payout_triggers:
                for trigger in payout_triggers:
                    stokvel_id = trigger[0]

                    all_members = conn.execute(
                        text(
                            """
                            SELECT *
                            FROM STOKVEL_MEMBERS
                            WHERE stokvel_id = :stokvel_id
                            """
                        ),
                        {"stokvel_id": stokvel_id},
                    ).fetchall()  # Fetch all members

                    for member in all_members:
                        try:

                            user_id = member[2]
                            stokvel_quote_id = member[12]
                            tx_type = "PAYOUT"
                            tx_date = tx_date
                            manageUrl = member[7]
                            previousToken = member[8]

                            # SQL query to sum deposits after the most recent payout
                            deposits = conn.execute(
                                text(
                                    """
                                            SELECT SUM(amount) AS total_deposits
                                            FROM TRANSACTIONS
                                            WHERE user_id = :user_id
                                            AND stokvel_id = :stokvel_id
                                            AND tx_type = 'DEPOSIT'
                                            AND tx_date > COALESCE((
                                                SELECT MAX(tx_date)
                                                FROM TRANSACTIONS
                                                WHERE user_id = :user_id
                                                    AND stokvel_id = :stokvel_id
                                                    AND tx_type = 'PAYOUT'
                                            ), '1900-01-01')
                                            """
                                ),
                                {"user_id": user_id, "stokvel_id": stokvel_id},
                            ).scalar()

                            deposits = float(deposits)

                            interest = get_user_interest(
                                user_id=user_id, stokvel_id=stokvel_id
                            )

                            print(f"Total deposits: {deposits}")
                            print(f"Total interest: {interest}")

                            payout = deposits + interest

                            receiving_wallet_address = conn.execute(
                                text(
                                    """
                                    SELECT ILP_wallet
                                    FROM USERS
                                    WHERE user_id = :user_id
                                    """
                                ),
                                {"user_id": user_id},
                            ).fetchone()

                            sender_wallet_address = conn.execute(
                                text(
                                    """
                                    SELECT ILP_wallet
                                    FROM STOKVELS
                                    WHERE stokvel_id = :stokvel_id
                                    """
                                ),
                                {"stokvel_id": stokvel_id},
                            ).fetchone()

                            # Check if a payment is needed based on user_quote_id
                            if stokvel_quote_id is not None:
                                # Create initial payment
                                # create_inital_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, user_quote_id)

                                conn.execute(
                                    text(
                                        """
                                        UPDATE STOKVEL_MEMBERS
                                        SET stokvel_quote_id = NULL
                                        WHERE user_id = :user_id
                                        """
                                    ),
                                    {"user_id": user_id},
                                )

                                insert_transaction(
                                    conn, user_id, stokvel_id, payout, tx_type, tx_date
                                )

                                print(f"Ran the initial payout")

                            else:
                                # Create contribution payment
                                # create_contribution_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken)

                                insert_transaction(
                                    conn, user_id, stokvel_id, payout, tx_type, tx_date
                                )

                                print(f"Ran the recurring payout")

                        except Exception as e:
                            print(
                                f"Error attempting to make contribution for user {user_id}: {str(e)}"
                            )
                            return False

            else:
                print("No contributions scheduled for today.")
                return True  # Indicate no contributions found but process is complete

    except Exception as e:
        print(f"Error checking contribution trigger: {str(e)}")
        return False


# ------------------------------------------------test functions - to be deleted -----------------------------------------------------------------------------


from datetime import timedelta
from random import choice, randint


def insert_test_data_contributions(num_records: int) -> None:
    """
    Insert test data into the CONTRIBUTIONS table.
    """
    users = [1]  # Sample user IDs
    stokvels = [1]  # Sample stokvel IDs

    start_date = datetime.now() - timedelta(days=7)  # Set start_date to yesterday
    for _ in range(num_records):
        user_id = choice(users)
        stokvel_id = choice(stokvels)
        frequency_days = 7  # Random frequency between 1 and 30 days
        start_date = start_date - timedelta(days=14)  # Random start date within 10 days
        next_date = datetime.now()
        previous_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() + timedelta(days=70)  # End date 60 days after start

        try:
            with sqlite_conn.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO CONTRIBUTIONS (user_id, stokvel_id, frequency_days, StartDate, NextDate, PreviousDate, EndDate)
                    VALUES (:user_id, :stokvel_id, :frequency_days, :StartDate, :NextDate, :PreviousDate, :EndDate)
                    """
                    ),
                    {
                        "user_id": user_id,
                        "stokvel_id": stokvel_id,
                        "frequency_days": frequency_days,
                        "StartDate": start_date,
                        "NextDate": next_date,
                        "PreviousDate": previous_date,
                        "EndDate": end_date,
                    },
                )

                conn.commit()  # Commit the transaction to the database

            print(
                f"Inserted test data for user_id {user_id} and stokvel_id {stokvel_id}."
            )

        except Exception as e:
            print(f"Failed to insert test data. Error: {str(e)}")


def clear_contributions_table() -> None:
    """
    Clear all records from the PAYOUTS table.
    """
    try:
        with sqlite_conn.connect() as conn:
            conn.execute(text("DELETE FROM TRANSACTIONS"))
            conn.commit()  # Commit the transaction to the database
        print("All records have been cleared from the CONTRIBUTIONS table.")
    except Exception as e:
        print(f"Failed to clear CONTRIBUTIONS table. Error: {str(e)}")


def insert_test_user_into_stokvel_members() -> None:
    """
    Insert a test user into the STOKVEL_MEMBERS table with predefined values.
    """
    # Predefined values
    id = 1
    stokvel_id = 1
    user_id = 1
    contribution_amount = 100
    active_status = "active"
    created_at = datetime.now()
    updated_at = datetime.now()
    user_payment_token = "TT"
    user_payment_URI = "TT"
    user_quote_id = "TT"
    stokvel_payment_token = "TT"
    stokvel_payment_URI = "TT"
    stokvel_quote_id = "TT"

    try:
        with sqlite_conn.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO STOKVEL_MEMBERS (id, stokvel_id, user_id, contribution_amount, active_status, created_at, updated_at,
                                              user_payment_token, user_payment_URI, user_quote_id,
                                              stokvel_payment_token, stokvel_payment_URI, stokvel_quote_id)
                VALUES (:id, :stokvel_id, :user_id, :contribution_amount, :active_status, :created_at, :updated_at,
                        :user_payment_token, :user_payment_URI, :user_quote_id,
                        :stokvel_payment_token, :stokvel_payment_URI, :stokvel_quote_id)
                """
                ),
                {
                    "id": id,
                    "stokvel_id": stokvel_id,
                    "user_id": user_id,
                    "contribution_amount": contribution_amount,
                    "active_status": active_status,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "user_payment_token": user_payment_token,
                    "user_payment_URI": user_payment_URI,
                    "user_quote_id": user_quote_id,
                    "stokvel_payment_token": stokvel_payment_token,
                    "stokvel_payment_URI": stokvel_payment_URI,
                    "stokvel_quote_id": stokvel_quote_id,
                },
            )

            conn.commit()  # Commit the transaction to the database

        print(
            f"Inserted test user with stokvel_id {stokvel_id} and user_id {user_id} into STOKVEL_MEMBERS."
        )

    except Exception as e:
        print(f"Failed to insert test user into STOKVEL_MEMBERS. Error: {str(e)}")


def insert_test_user() -> None:
    """
    Insert a test user into the USERS table with predefined values.
    """
    user_id = 1
    user_number = "+123"
    user_name = "John"
    user_surname = "Doe"
    ILP_wallet = "1123dvew"
    MOMO_wallet = "123ABC"
    verified_KYC = 1
    created_at = datetime.now()
    updated_at = datetime.now()

    try:
        with sqlite_conn.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO USERS (user_id, user_number, user_name, user_surname, ILP_wallet, MOMO_wallet, verified_KYC, created_at, updated_at)
                VALUES (:user_id, :user_number, :user_name, :user_surname, :ILP_wallet, :MOMO_wallet, :verified_KYC, :created_at, :updated_at)
                """
                ),
                {
                    "user_id": user_id,
                    "user_number": user_number,
                    "user_name": user_name,
                    "user_surname": user_surname,
                    "ILP_wallet": ILP_wallet,
                    "MOMO_wallet": MOMO_wallet,
                    "verified_KYC": verified_KYC,
                    "created_at": created_at,
                    "updated_at": updated_at,
                },
            )

            conn.commit()  # Commit the transaction to the database

        print(f"Inserted test user with user_id {user_id} into USERS.")

    except Exception as e:
        print(f"Failed to insert test user into USERS. Error: {str(e)}")


def insert_test_stokvel() -> None:
    """
    Insert a test stokvel into the STOKVELS table with predefined values.
    """
    stokvel_id = 1
    stokvel_name = "Test Stokvel"
    ILP_wallet = "1123ILP"
    MOMO_wallet = "456MOMO"
    total_members = 10
    min_contributing_amount = 50.00
    max_number_of_contributors = 100
    total_contributions = 1000.00
    start_date = "2024-01-01"  # Example start date in ISO8601 format
    end_date = "2024-12-31"  # Example end date in ISO8601 format
    payout_frequency_int = 1
    payout_frequency_period = "month"
    created_at = datetime.now() - timedelta(days=123)
    updated_at = datetime.now()

    try:
        with sqlite_conn.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO STOKVELS (stokvel_id, stokvel_name, ILP_wallet, MOMO_wallet, total_members,
                                      min_contributing_amount, max_number_of_contributors, total_contributions,
                                      start_date, end_date, payout_frequency_int, payout_frequency_period,
                                      created_at, updated_at)
                VALUES (:stokvel_id, :stokvel_name, :ILP_wallet, :MOMO_wallet, :total_members,
                        :min_contributing_amount, :max_number_of_contributors, :total_contributions,
                        :start_date, :end_date, :payout_frequency_int, :payout_frequency_period,
                        :created_at, :updated_at)
                """
                ),
                {
                    "stokvel_id": stokvel_id,
                    "stokvel_name": stokvel_name,
                    "ILP_wallet": ILP_wallet,
                    "MOMO_wallet": MOMO_wallet,
                    "total_members": total_members,
                    "min_contributing_amount": min_contributing_amount,
                    "max_number_of_contributors": max_number_of_contributors,
                    "total_contributions": total_contributions,
                    "start_date": start_date,
                    "end_date": end_date,
                    "payout_frequency_int": payout_frequency_int,
                    "payout_frequency_period": payout_frequency_period,
                    "created_at": created_at,
                    "updated_at": updated_at,
                },
            )

            conn.commit()  # Commit the transaction to the database

        print(f"Inserted test stokvel with stokvel_id {stokvel_id} into STOKVELS.")

    except Exception as e:
        print(f"Failed to insert test stokvel into STOKVELS. Error: {str(e)}")


def insert_test_data_payouts(num_records: int) -> None:
    """
    Insert test data into the PAYOUTS table.
    """
    stokvels = [1]  # Sample stokvel IDs

    start_date = datetime.now() - timedelta(days=7)  # Set start_date to yesterday
    for _ in range(num_records):
        stokvel_id = choice(stokvels)
        frequency_days = 7  # Random frequency between 1 and 30 days
        start_date = start_date - timedelta(days=14)  # Random start date within 10 days
        next_date = datetime.now()
        previous_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() + timedelta(days=70)  # End date 60 days after start

        try:
            with sqlite_conn.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO PAYOUTS (stokvel_id, frequency_days, StartDate, NextDate, PreviousDate, EndDate)
                    VALUES ( :stokvel_id, :frequency_days, :StartDate, :NextDate, :PreviousDate, :EndDate)
                    """
                    ),
                    {
                        "stokvel_id": stokvel_id,
                        "frequency_days": frequency_days,
                        "StartDate": start_date,
                        "NextDate": next_date,
                        "PreviousDate": previous_date,
                        "EndDate": end_date,
                    },
                )

                conn.commit()  # Commit the transaction to the database

            print(f"Inserted test data for stokvel_id {stokvel_id}.")

        except Exception as e:
            print(f"Failed to insert test data. Error: {str(e)}")


def insert_test_interest_data() -> None:
    """
    Inserts test data into the INTEREST table, ensuring date is in DATETIME format.
    """
    id = 4
    stokvel_id = 1
    date = "2024-07-30"  # Make sure this is in a valid SQL date format (YYYY-MM-DD)
    interest_value = 15.00

    # Connect to the database and insert the test data
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
                INSERT INTO INTEREST (id, stokvel_id, date, interest_value)
                VALUES (:id, :stokvel_id, :date, :interest_value)
                """
            ),
            {
                "id": id,
                "stokvel_id": stokvel_id,
                "date": date,
                "interest_value": interest_value,
            },
        )
        conn.commit()

def delete_transaction_by_id(transaction_id: int) -> None:
    """
    Delete a transaction from the TRANSACTIONS table based on the given transaction ID.
    
    Parameters:
    transaction_id (int): The ID of the transaction to be deleted.
    """
    delete_query = """
    DELETE FROM TRANSACTIONS
    WHERE id = :transaction_id
    """
    
    try:
        with sqlite_conn.connect() as conn:
            conn.execute(text(delete_query), {"transaction_id": transaction_id})
            conn.commit()
            print(f"Transaction with ID {transaction_id} has been deleted.")
    
    except sqlite3.Error as e:
        print(f"Error occurred while deleting transaction: {e}")


if __name__ == "__main__":
    tx_date = datetime.now() - timedelta(days=90)
    tx_date2 = datetime.now() - timedelta(days=60)
    tx_date3 = datetime.now() - timedelta(days=30)
    num_records = 1
    conn = sqlite_conn.connect()
    # contribution_trigger()
    # payout_trigger()
    #insert_test_data_payouts(num_records)
    #insert_transaction(conn = conn,user_id = 2, stokvel_id = 1, amount = 100 , tx_type = "DEPOSIT", tx_date = tx_date)
    #insert_transaction(conn = conn,user_id = 2, stokvel_id = 1, amount = 100 , tx_type = "DEPOSIT", tx_date = tx_date2)
    #insert_transaction(conn = conn,user_id = 2, stokvel_id = 1, amount = 100 , tx_type = "DEPOSIT", tx_date = tx_date3)
    #insert_transaction(conn = conn,user_id = 1, stokvel_id = 1, amount = 200 , tx_type = "DEPOSIT", tx_date = tx_date)
    #insert_transaction(conn = conn,user_id = 1, stokvel_id = 1, amount = 200 , tx_type = "DEPOSIT", tx_date = tx_date2)
    #insert_transaction(conn = conn,user_id = 1, stokvel_id = 1, amount = 200 , tx_type = "DEPOSIT", tx_date = tx_date3)
    delete_transaction_by_id(7)
    delete_transaction_by_id(8)
    # insert_test_user_into_stokvel_members()
    # insert_test_user()
    #insert_test_data_contributions(num_records)
    #clear_contributions_table()
    # insert_test_stokvel()
    # insert_test_interest_data()
    # print(get_user_interest(user_id=1,stokvel_id=1))
    # print(get_user_interest(user_id=2,stokvel_id=1))
    # print(get_stokvel_monthly_interest(stokvel_id = 1))

def get_stokvel_details(stokvel_id):
    select_query = 'SELECT * FROM STOKVELS WHERE stokvel_id = :stokvel_id'
    parameters = {
        "stokvel_id": stokvel_id
    }
    
    try:
        with sqlite_conn.connect() as conn:
            result = conn.execute(text(select_query), parameters)
            stokvel_details = result.fetchone()  # Fetch one record
            
            if stokvel_details is None:
                print(f"No stokvel found with id: {stokvel_id}")
                return None  # Return None if no record is found
            
            # Convert the result to a dictionary if necessary
            columns = result.keys()  # Extract column names from the result
            stokvel_dict = dict(zip(columns, stokvel_details))  # Create a dictionary from column names and values
            
            print(f"Selected stokvel details: {stokvel_dict}")
            return stokvel_dict  # Return the details

    except sqlite3.Error as e:
        print(f"Error retrieving stokvel details: {e}")
        raise e


def get_stokvel_member_details(stokvel_id, user_id):
    select_query = 'SELECT * FROM STOKVEL_MEMBERS WHERE stokvel_id = :stokvel_id and user_id = :user_id'
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id
    }
    
    try:
        with sqlite_conn.connect() as conn:
            result = conn.execute(text(select_query), parameters)
            stokvel_members_details = result.fetchone()  # Fetch one record
            
            if stokvel_members_details is None:
                print(f"No stokvel found with id: {stokvel_id}")
                return None  # Return None if no record is found
            
            # Convert the result to a dictionary if necessary
            columns = result.keys()  # Extract column names from the result
            stokvel_members_dict = dict(zip(columns, stokvel_members_details))  # Create a dictionary from column names and values
            
            print(f"Selected stokvel details: {stokvel_members_dict}")
            return stokvel_members_dict  # Return the details

    except sqlite3.Error as e:
        print(f"Error retrieving stokvel details: {e}")
        raise e


def update_member_grantaccepted(stokvel_id: int, user_id: int, active_status: str, user_interaction_ref: str):
    update_query = """
    UPDATE STOKVEL_MEMBERS
    SET active_status = :active_status, user_interaction_ref = :user_interaction_ref
    WHERE stokvel_id = :stokvel_id AND user_id = :user_id
    """
    
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "active_status": active_status,
        "user_interaction_ref": user_interaction_ref
    }

    try:
        with sqlite_conn.connect() as conn:
            result =  conn.execute(text(update_query), parameters)
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Successfully updated active_status to '{active_status}' and user_interaction_ref for stokvel_id: {stokvel_id}, user_id: {user_id}")
            else:
                print(f"No records found to update for stokvel_id: {stokvel_id}, user_id: {user_id}")
                
    except sqlite3.Error as e:
        print(f"Error updating stokvel member: {e}")
        raise e
    

def update_stokvel_grantaccepted(stokvel_id: int, user_id: int, stokvel_payout_active_status: str, stokvel_interaction_ref: str):
    update_query = """
    UPDATE STOKVEL_MEMBERS
    SET stokvel_payout_active_status = :stokvel_payout_active_status, stokvel_interaction_ref = :stokvel_interaction_ref
    WHERE stokvel_id = :stokvel_id AND user_id = :user_id
    """
    
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "stokvel_payout_active_status": stokvel_payout_active_status,
        "stokvel_interaction_ref": stokvel_interaction_ref
    }

    try:
        with sqlite_conn.connect() as conn:
            result =  conn.execute(text(update_query), parameters)
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Successfully updated stokvel_payout_active_status to '{stokvel_payout_active_status}' and stokvel_interaction_ref for stokvel_id: {stokvel_id}, user_id: {user_id}")
            else:
                print(f"No records found to update for stokvel_id: {stokvel_id}, user_id: {user_id}")
                
    except sqlite3.Error as e:
        print(f"Error updating stokvel payout: {e}")
        raise e
    

def update_adhoc_contribution_parms(stokvel_id: int, user_id: int, url: str, token: str):
    update_query = """
    UPDATE STOKVEL_MEMBERS
    SET adhoc_contribution_uri = :adhoc_contribution_uri, adhoc_contribution_token = :adhoc_contribution_token
    WHERE stokvel_id = :stokvel_id AND user_id = :user_id
    """
    
    parameters = {
        "stokvel_id": stokvel_id,
        "user_id": user_id,
        "adhoc_contribution_uri": url,
        "adhoc_contribution_token": token
    }

    try:
        with sqlite_conn.connect() as conn:
            result =  conn.execute(text(update_query), parameters)
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Successfully updated adhoc paymnet params for stokvel_id: {stokvel_id}, user_id: {user_id}")
            else:
                print(f"No records found to update for stokvel_id: {stokvel_id}, user_id: {user_id}")
                
    except sqlite3.Error as e:
        print(f"Error updating stokvel payout: {e}")
        raise e
