# from .sql_connection import sql_connection
import sqlite3
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from .sqlite_connection import SQLiteConnection
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

# from queries import get_next_unique_id


sqlite_conn = SQLiteConnection(database="./database/test_db.db")

def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(
        text(f"SELECT MAX({id_column}) FROM {table_name}")
    ).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1

def insert_member_contribution_parameters(stokvel_id: int, 
                                          start_date: str, 
                                          payout_period: str):
    """
    Function to insert the first contribution into the 'CONTRIBUTIONS' table with the 
    next contribution date equal to the start date, and prepare for future contributions.
    
    Args:
    - stokvel_id (int): ID of the stokvel (group).
    - start_date (str): The starting date in 'YYYY-MM-DD' format.
    - payout_period (str): The payout period, e.g., 'Days', 'Week', 'Months', etc.
    """
    # Append time to start date if not already present
    start_date += "T00:00:00"  # Add time if not specified
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")  # Convert to datetime object

    # For the first contribution, NextDate is the same as StartDate
    next_date = start_date
    frequency_days = 0  # Since it's the same day, the difference is 0 days

    # Prepare insert query for CONTRIBUTIONS table
    prepped_insert_query = """
    INSERT INTO CONTRIBUTIONS (
        stokvel_id, frequency_days, StartDate, NextDate, PreviousDate
    ) VALUES (
        :stokvel_id, :frequency_days, :StartDate, :NextDate, :PreviousDate
    )
    """

    # Execute the insert query
    try:
        with sqlite_conn.connect() as conn:
            parameters = {
                "stokvel_id": stokvel_id,
                "frequency_days": frequency_days,  # 0 because NextDate = StartDate
                "StartDate": start_date,
                "NextDate": next_date,  # Next contribution date is the same as the start date
                "PreviousDate": None  # No previous date for the first contribution
            }

            # Insert the new contribution data
            conn.execute(text(prepped_insert_query), parameters)
            conn.commit()

            print("First contribution parameters inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error occurred during insert stokvel: {e}")
        raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a stokvel: {e}")

def insert_stokvel_payouts_parameters(stokvel_id: int, 
                                          start_date: str, 
                                          payout_period: str):
    """
    Function to calculate the next contribution date based on the payout period
    and insert the result into the 'CONTRIBUTIONS' table.
    
    Args:
    - stokvel_id (int): ID of the stokvel (group).
    - start_date (str): The starting date in 'YYYY-MM-DDTHH:MM:SS' format.
    - payout_period (str): The payout period, e.g., 'Days', 'Week', 'Months', etc.
    """
    # Parse the start date as a datetime object using the correct format
    start_date += "T00:00:00"  # Add time if not specified
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")  # Convert to datetime object

    # Calculate the next contribution date
    next_date = calculate_next_date(payout_period, start_date)
    frequency_days = 0  # Get the frequency in days

    # Prepare insert query for CONTRIBUTIONS table
    prepped_insert_query = """
    INSERT INTO PAYOUTS (
        stokvel_id, frequency_days, StartDate, NextDate, PreviousDate
    ) VALUES (
        :stokvel_id, :frequency_days, :StartDate, :NextDate, :PreviousDate
    )
    """

    # Execute the insert query
    try:
        with sqlite_conn.connect() as conn:
            parameters = {
                "stokvel_id": stokvel_id,
                "frequency_days": frequency_days,  # Days between start and next date
                "StartDate": start_date,
                "NextDate": next_date,
                "PreviousDate": start_date  # First contribution, so no previous date
            }

            # Insert the new contribution data
            result = conn.execute(text(prepped_insert_query), parameters)
            conn.commit()
            
            print("Contribution parameters inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error occurred during insert stokvel: {e}")
        raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

def calculate_next_date(contribution_or_payout_period, current_date):

    # example usage:
    # pevious_date = next_date --> update in DB
    # new next_date = update_next_date()
    current_date = str(current_date)
    if ":" in current_date and "T" not in current_date:
        current_date = current_date.split(" ")[0]
        current_date += "T00:00:00"  # Add the time component if not present


    if "T" not in current_date:  # Check if the time component is already present
        current_date += "T00:00:00"  # Add the time component if not present
    
    current_date = datetime.strptime(current_date, "%Y-%m-%dT%H:%M:%S")  # Convert to datetime object
    # Determine the next contribution date based on the payout period
    if contribution_or_payout_period == 'Days':
        period_delta = timedelta(days=1)  # Increment by 1 day
    elif contribution_or_payout_period == 'Week':
        period_delta = timedelta(weeks=1)  # Increment by 1 week
    elif contribution_or_payout_period == 'Months':
        period_delta = relativedelta(months=1)  # Increment by 1 month
    elif contribution_or_payout_period == 'Years':
        period_delta = relativedelta(years=1)  # Increment by 1 year
    else:
        raise ValueError("Invalid payout period specified.")

    # Calculate the next contribution date
    next_date = current_date + period_delta
    return next_date.strftime("%Y-%m-%dT%H:%M:%S")  # Return with time


def update_next_contributions_dates(current_next_date, stokvel_id, contribution_or_payout_period):
        update_query = """
            UPDATE CONTRIBUTIONS
            SET PreviousDate = :PreviousDate, NextDate = :NextDate
            WHERE stokvel_id = :stokvel_id
        """
        # Execute the update query

        try:
            with sqlite_conn.connect() as conn:
                parameters = {
                    "PreviousDate": current_next_date,  # Set the current NextDate as PreviousDate
                    "NextDate": calculate_next_date(contribution_or_payout_period, current_next_date),# Set the new calculated NextDate
                    "stokvel_id": stokvel_id
                }
                result = conn.execute(text(update_query), parameters)
                conn.commit()
                print(f"Contribution parameters inserted successfully.: \n{current_next_date} \n {calculate_next_date(contribution_or_payout_period, current_next_date)}")

            return calculate_next_date(contribution_or_payout_period, current_next_date)
            

        except sqlite3.Error as e:
            print(f"Error occurred during insert stokvel: {e}")
            raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

        except Exception as e:
            print(f"Error occurred during insert: {e}")
            raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

def update_next_payout_dates(current_next_date, stokvel_id, contribution_or_payout_period):
        update_query = """
            UPDATE PAYOUTS
            SET PreviousDate = :PreviousDate, NextDate = :NextDate
            WHERE stokvel_id = :stokvel_id
        """
        # Execute the update query

        try:
            with sqlite_conn.connect() as conn:
                parameters = {
                    "PreviousDate": current_next_date,  # Set the current NextDate as PreviousDate
                    "NextDate": calculate_next_date(contribution_or_payout_period, current_next_date),# Set the new calculated NextDate
                    "stokvel_id": stokvel_id
                }
                result = conn.execute(text(update_query), parameters)
                conn.commit()
            
            print("Contribution parameters inserted successfully.")
            return calculate_next_date(contribution_or_payout_period, current_next_date)

        except sqlite3.Error as e:
            print(f"Error occurred during insert stokvel: {e}")
            raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

        except Exception as e:
            print(f"Error occurred during insert: {e}")
            raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error


def update_user_contribution_token_uri(stokvel_id, user_id, new_token, new_uri):
    try:
        with sqlite_conn.connect() as conn:
            # Update query to modify user_payment_token and user_payment_URI
            update_query = """
            UPDATE STOKVEL_MEMBERS
            SET user_payment_token = :new_token, 
                user_payment_URI = :new_uri, 
                updated_at = CURRENT_TIMESTAMP
            WHERE stokvel_id = :stokvel_id AND user_id = :user_id
            """

            # Execute the update query with the provided parameters
            conn.execute(text(update_query), {
                "new_token": new_token,
                "new_uri": new_uri,
                "stokvel_id": stokvel_id,
                "user_id": user_id
            })

            # Commit the transaction
            conn.commit()

            print(f"User payment token and URI updated successfully for user_id {user_id} in stokvel_id {stokvel_id}")

    except sqlite3.Error as e:
        print(f"SQLite error during update: {e}")
        raise Exception(f"SQLiteError occurred during token/URI update: {e}")

    except Exception as e:
        print(f"Error during token/URI update: {e}")
        raise Exception(f"Exception occurred during token/URI update: {e}")

def update_stokvel_token_uri(stokvel_id, user_id, new_token, new_uri):
    try:
        with sqlite_conn.connect() as conn:
            # Update query to modify stokvel_payment_token and stokvel_payment_URI
            update_query = """
            UPDATE STOKVEL_MEMBERS
            SET stokvel_payment_token = :new_token, 
                stokvel_payment_URI = :new_uri, 
                updated_at = CURRENT_TIMESTAMP
            WHERE stokvel_id = :stokvel_id and user_id = :user_id
            """

            # Execute the update query with the provided parameters
            conn.execute(text(update_query), {
                "new_token": new_token,
                "new_uri": new_uri,
                "stokvel_id": stokvel_id,
                "user_id": user_id
            })

            # Commit the transaction
            conn.commit()

            print(f"Stokvel payment token and URI updated successfully for stokvel_id {stokvel_id}")

    except sqlite3.Error as e:
        print(f"SQLite error during update: {e}")
        raise Exception(f"SQLiteError occurred during stokvel token/URI update: {e}")

    except Exception as e:
        print(f"Error during stokvel token/URI update: {e}")
        raise Exception(f"Exception occurred during stokvel token/URI update: {e}")

# def insert_member_contribution_parameters(stokvel_id: int, 
#                                           start_date: str,
#                                           end_date: str, #maybe change this so that there is no inputted end date? instead the users end date is given to them based on the periods that they select?
#                                         #   payout_frequency: int,
#                                           payout_period: str):    
#     # Get the difference between the start and enddate
#     # Divide the difference by the number of periods
#     # loop through the number we got above
#     # insert into the table

#     start_date += ":00"
#     end_date += ":00"

#     # Parse the start and end dates as datetime objects using the correct format
#     start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")  # Include seconds in the format
#     end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")      # Include seconds in the format

#     # Calculate the difference based on the payout period
#     date_difference = (end_date - start_date).days  # Get the total days difference
#     no_periods = 0

#     if payout_period == 'Days':
#         no_periods = date_difference  # Total days
#         period_delta = timedelta(days=1)  # Increment by 1 day
#     elif payout_period == 'Week':
#         no_periods = date_difference // 7  # Total weeks
#         period_delta = timedelta(weeks=1)  # Increment by 1 week
#     elif payout_period == 'Months':
#         diff = relativedelta(end_date, start_date)
#         no_periods = diff.years * 12 + diff.months  # Total months
#         period_delta = relativedelta(months=1)  # Increment by 1 month
#     elif payout_period == 'Years':
#         diff = relativedelta(end_date, start_date)
#         no_periods = diff.years  # Total years
#         period_delta = relativedelta(years=1)  # Increment by 1 year
#     elif payout_period == '30 Seconds':
#         # Calculate the total number of seconds in the period
#         total_seconds = (end_date - start_date).total_seconds()
#         no_periods = int(total_seconds // 30)  # Total number of 30-second periods
#         period_delta = timedelta(seconds=30)  # Increment by 30 seconds
#     else:
#         raise ValueError("Invalid payout period specified.")

#     # Prepare insert query
#     prepped_insert_query = """
#     INSERT INTO MEMBER_CONTRIBUTIONS (
#         id, stokvel_id, frequency_days, StartDate, EndDate
#     ) VALUES (
#         :id, :stokvel_id, :frequency_days, :StartDate, :EndDate
#     )
#     """
#     try:
#         with sqlite_conn.connect() as conn:

#             debit_date = start_date  # Initialize the first debit date
#             for i in range(no_periods):
#                 next_debit_date = debit_date + period_delta  # Calculate the next debit date

#                 # Parameter dictionary for executing the query
#                 parameters = {
#                     "id": None,  # Assuming autoincrement for the ID field
#                     "stokvel_id": stokvel_id,
#                     "frequency_days": (next_debit_date - debit_date).days,
#                     "StartDate": debit_date,
#                     "EndDate": next_debit_date,
#                 }

#                 if stokvel_id is None:
#                     stokvel_current_id = get_next_unique_id(conn, 'MEMBER_CONTRIBUTIONS', 'id')
#                     parameters['stokvel_id'] = stokvel_current_id

#                 print("Connected in stokvel insert")
#                 result = conn.execute(text(prepped_insert_query), parameters)
#                 conn.commit()

#                 debit_date = next_debit_date
                        
#     except sqlite3.Error as e:
#         print(f"Error occurred during insert stokvel: {e}")
#         raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

#     except Exception as e:
#         print(f"Error occurred during insert: {e}")
#         raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error
    

# def insert_stokvel_payout_parameters(stokvel_id: int, 
#                                           start_date: str,
#                                           end_date: str, #maybe change this so that there is no inputted end date? instead the users end date is given to them based on the periods that they select?
#                                         #   payout_frequency: int,
#                                           payout_period: str):    
#     # Get the difference between the start and enddate
#     # Divide the difference by the number of periods
#     # loop through the number we got above
#     # insert into the table

#     start_date += ":00"
#     end_date += ":00"

#     # Parse the start and end dates as datetime objects using the correct format
#     start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")  # Include seconds in the format
#     end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")      # Include seconds in the format

#     # Calculate the difference based on the payout period
#     date_difference = (end_date - start_date).days  # Get the total days difference
#     no_periods = 0

#     if payout_period == 'Days':
#         no_periods = date_difference  # Total days
#         period_delta = timedelta(days=1)  # Increment by 1 day
#     elif payout_period == 'Week':
#         no_periods = date_difference // 7  # Total weeks
#         period_delta = timedelta(weeks=1)  # Increment by 1 week
#     elif payout_period == 'Months':
#         diff = relativedelta(end_date, start_date)
#         no_periods = diff.years * 12 + diff.months  # Total months
#         period_delta = relativedelta(months=1)  # Increment by 1 month
#     elif payout_period == 'Years':
#         diff = relativedelta(end_date, start_date)
#         no_periods = diff.years  # Total years
#         period_delta = relativedelta(years=1)  # Increment by 1 year
#     elif payout_period == '30 Seconds':
#         # Calculate the total number of seconds in the period
#         total_seconds = (end_date - start_date).total_seconds()
#         no_periods = int(total_seconds // 30)  # Total number of 30-second periods
#         period_delta = timedelta(seconds=30)  # Increment by 30 seconds
#     else:
#         raise ValueError("Invalid payout period specified.")

#     # Prepare insert query
#     prepped_insert_query = """
#     INSERT INTO MEMBER_CONTRIBUTIONS (
#         id, stokvel_id, frequency_days, StartDate, EndDate
#     ) VALUES (
#         :id, :stokvel_id, :frequency_days, :StartDate, :EndDate
#     )
#     """
#     try:
#         with sqlite_conn.connect() as conn:

#             debit_date = start_date  # Initialize the first debit date
#             for i in range(no_periods):
#                 next_debit_date = debit_date + period_delta  # Calculate the next debit date

#                 # Parameter dictionary for executing the query
#                 parameters = {
#                     "id": None,  # Assuming autoincrement for the ID field
#                     "stokvel_id": stokvel_id,
#                     "frequency_days": (next_debit_date - debit_date).days,
#                     "StartDate": debit_date,
#                     "EndDate": next_debit_date
#                 }

#                 if stokvel_id is None:
#                     stokvel_current_id = get_next_unique_id(conn, 'MEMBER_CONTRIBUTIONS', 'id')
#                     parameters['stokvel_id'] = stokvel_current_id

#                 print("Connected in stokvel insert")
#                 result = conn.execute(text(prepped_insert_query), parameters)
#                 conn.commit()

#                 debit_date = next_debit_date
                        
#     except sqlite3.Error as e:
#         print(f"Error occurred during insert stokvel: {e}")
#         raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

#     except Exception as e:
#         print(f"Error occurred during insert: {e}")
#         raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error



# Example usage
if __name__ == "__main__":
    stokvel_id = 1
    result = insert_member_contribution_parameters(
        stokvel_id=stokvel_id, 
        start_date="2022-01-01", 
        end_date="2022-12-31", 
        payout_period="Months", 
        contribution=100.00,
    )
    print(result)


# def insert_stokvel_payout_parameters():
#     pass

# if __name__ == "__main__":
#     # sqlite_conn = SQLiteConnection(database="./database/test_db.db")
#     print(insert_member_contribution_parameters( 1, "2024-01-01", "2025-01-01", "Years"))

    




        