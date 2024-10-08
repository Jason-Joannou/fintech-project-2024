import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

sqlite_conn = SQLiteConnection(database="./database/test_db.db")


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


def get_stokvel_monthly_interest(stokvel_id: int) -> Dict[str, float]:
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
                "SELECT prev_payout FROM STOKVELS WHERE stokvel_id = :stokvel_id"
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
                AND tx_type = 'deposit'
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
                AND tx_type = 'deposit'
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


print(get_stokvel_monthly_interest(stokvel_id=1))
print(get_user_interest(user_id=1, stokvel_id=1))


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

        # print(f"User details: {user_details}")
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
        conn.execute(
            text(update_query), {"new_name": new_name, "user_number": formatted_number}
        )
        conn.commit()


def update_user_surname(phone_number: str, new_surname: str):
    formatted_number = extract_whatsapp_number(from_number=phone_number)

    update_query = """
    UPDATE USERS
    SET user_surname = :new_surname
    WHERE user_number = :user_number;
    """

    try:
        with sqlite_conn.connect() as conn:
            conn.execute(
                text(update_query),
                {"new_surname": new_surname, "user_number": formatted_number},
            )
            conn.commit()

    except Exception as e:
        print(f"Error updating surname: {e}")
