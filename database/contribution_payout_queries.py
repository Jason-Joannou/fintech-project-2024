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
                                          end_date: str, #maybe change this so that there is no inputted end date? instead the users end date is given to them based on the periods that they select?
                                        #   payout_frequency: int,
                                          payout_period: str,
                                          contribution: float):
    
    # Get the difference between the start and enddate
    # Divide the difference by the number of periods
    # loop through the number we got above
    # insert into the table

    start_date += ":00"
    end_date += ":00"

    # Parse the start and end dates as datetime objects using the correct format
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")  # Include seconds in the format
    end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")      # Include seconds in the format

    # Calculate the difference based on the payout period
    date_difference = (end_date - start_date).days  # Get the total days difference
    no_periods = 0

    if payout_period == 'Days':
        no_periods = date_difference  # Total days
        period_delta = timedelta(days=1)  # Increment by 1 day
    elif payout_period == 'Week':
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
        no_periods = int(total_seconds // 30)  # Total number of 30-second periods
        period_delta = timedelta(seconds=30)  # Increment by 30 seconds
    else:
        raise ValueError("Invalid payout period specified.")

    # Prepare insert query
    prepped_insert_query = """
    INSERT INTO MEMBER_CONTRIBUTIONS (
        id, stokvel_id, frequency_days, StartDate, EndDate, contribution
    ) VALUES (
        :id, :stokvel_id, :frequency_days, :StartDate, :EndDate, :contribution
    )
    """
    try:
        with sqlite_conn.connect() as conn:

            debit_date = start_date  # Initialize the first debit date
            for i in range(no_periods):
                next_debit_date = debit_date + period_delta  # Calculate the next debit date

                # Parameter dictionary for executing the query
                parameters = {
                    "id": None,  # Assuming autoincrement for the ID field
                    "stokvel_id": stokvel_id,
                    "frequency_days": (next_debit_date - debit_date).days,
                    "StartDate": debit_date,
                    "EndDate": next_debit_date,
                    "contribution": contribution,
                }

                if stokvel_id is None:
                    stokvel_current_id = get_next_unique_id(conn, 'MEMBER_CONTRIBUTIONS', 'id')
                    parameters['stokvel_id'] = stokvel_current_id

                print("Connected in stokvel insert")
                result = conn.execute(text(prepped_insert_query), parameters)
                conn.commit()

                debit_date = next_debit_date
                        
    except sqlite3.Error as e:
        print(f"Error occurred during insert stokvel: {e}")
        raise Exception(f"SQLiteError occurred during inserting a stokvel: {e}")  # Stops execution by raising the error

    except Exception as e:
        print(f"Error occurred during insert: {e}")
        raise Exception(f"Exception occurred during inserting a stokvel: {e}")  # Stops execution by raising the error



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

    




        