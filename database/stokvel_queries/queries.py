# from .sql_connection import sql_connection
import sqlite3
from datetime import datetime
from typing import List, Optional

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()


def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(text(f"SELECT MAX({id_column}) FROM {table_name}")).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1


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
            stokvel_payment_token, stokvel_payment_URI, stokvel_quote_id, created_at, updated_at
        ) VALUES (
            :stokvel_id, :user_id, :contribution_amount, :user_payment_token, :user_payment_URI, :user_quote_id, 
            :stokvel_payment_token, :stokvel_payment_URI, :stokvel_quote_id, :created_at, :updated_at
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
    period_duration, number_of_periods_coverted, = ""
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



