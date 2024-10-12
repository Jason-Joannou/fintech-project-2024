import logging
from datetime import datetime, timezone, timedelta
import requests

from azure.functions import TimerRequest


BASE_READ_ROUTE = "http://127.0.0.1:5000/database/query_db"
BASE_WRITE_ROUTE = "http://127.0.0.1:5000/database/write_db"


def main(DailyPayoutOperation: TimerRequest) -> None:
    """
    Main function to trigger daily payouts.
    """

    input_date = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")  # Use UTC
    tx_date = datetime.now(timezone.utc)  # Use UTC

    try:
        # Step 1: Check if the payout process should be kicked off
        payout_trigger_date_response = requests.post(
            BASE_READ_ROUTE,
            json={
                "query": (
                    """
                    SELECT stokvel_id
                    FROM PAYOUTS
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                "parameters": {"input_date": input_date},
            },
            timeout=10,
        )

        # Raise an exception for HTTP error responses
        payout_trigger_date_response.raise_for_status()

        # Parse the JSON response
        payout_trigger_date = payout_trigger_date_response.json()

        logging.info(f"payout triggers: {payout_trigger_date}")

        if not payout_trigger_date:
            logging.info("No payout triggers found. Exiting.")
            return

        # Step 2: Trigger the payout process
        logging.info("Triggering payout process...")

        for trigger_date in payout_trigger_date:
            stokvel_id = trigger_date["stokvel_id"]
            logging.info(f"Processing stokvel_id: {stokvel_id}")

            # Fetch all members of the stokvel
            stokvel_members_response = requests.post(
                BASE_READ_ROUTE,
                json={
                    "query": (
                        """
                        SELECT *
                        FROM STOKVEL_MEMBERS
                        WHERE stokvel_id = :stokvel_id
                        """
                    ),
                    "parameters": {"stokvel_id": stokvel_id},
                },
                timeout=10,
            )

            # Raise an exception for HTTP error responses
            stokvel_members_response.raise_for_status()

            # Parse the JSON response
            stokvel_members = stokvel_members_response.json()

            logging.info(f"Members for stokvel_id {stokvel_id}: {stokvel_members}")

            if not stokvel_members:
                logging.info(f"No members found for stokvel_id {stokvel_id}. Continuing to next stokvel.")
                continue  # Continue with the next stokvel_id

            for member in stokvel_members:
                
                user_id = member["user_id"]
                stokvel_quote_id = member["stokvel_quote_id"]
                tx_type = "PAYOUT"
                manageUrl = member["stokvel_payment_URI"]
                previousToken = member["stokvel_payment_token"]

                # SQL query to sum deposits after the most recent payout

                deposits_response = requests.post(
                    BASE_READ_ROUTE,
                    json={
                        "query": (
                            """
                            SELECT SUM(amount) AS total_deposits
                            FROM TRANSACTIONS
                            WHERE user_id = :user_id
                            AND stokvel_id = :stokvel_id
                            AND tx_type = 'DEPOSIT'
                            AND tx_date >= COALESCE((
                                SELECT MAX(tx_date)
                                FROM TRANSACTIONS
                                WHERE user_id = :user_id
                                    AND stokvel_id = :stokvel_id
                                    AND tx_type = 'PAYOUT'
                            ), '1900-01-01')
                            """
                        ),
                        "parameters": {"user_id": user_id, "stokvel_id": stokvel_id},
                    },
                    timeout=10,
                )

                # Raise an exception for HTTP error responses
                deposits_response.raise_for_status()

                # Parse the JSON response to extract the data
                deposits_data = deposits_response.json()

                # Log or print the total deposits
                if deposits_data and isinstance(deposits_data, list) and len(deposits_data) > 0:
                    total_deposits = deposits_data[0].get('total_deposits', 0)
                    print(f"Total deposits to payout: {total_deposits}")
                else:
                    print("No deposits found or error in the query response.")

                ###################################################################################
                # Step 3: Calculate accumulated interest for the stokvel after the most recent payout
                interest_response = requests.post(
                    BASE_READ_ROUTE,
                    json={
                        "query": (
                            """
                            SELECT interest_value, date
                            FROM INTEREST
                            WHERE stokvel_id = :stokvel_id
                            AND date > COALESCE((
                                SELECT MAX(tx_date)
                                FROM TRANSACTIONS
                                WHERE stokvel_id = :stokvel_id and user_id = :user_id
                                AND tx_type = 'PAYOUT'
                            ), '1900-01-01')
                            ORDER BY date ASC  -- Sort by date in ascending order
                            """
                        ),
                        "parameters": {"stokvel_id": stokvel_id, "user_id": user_id},
                    },
                    timeout=10,
                )

                interest_response.raise_for_status()
                interest_data = interest_response.json()
                print("Interest table")
                print(interest_data)

                stokvel_interest = {row["date"]: row["interest_value"] for row in interest_data}
                if stokvel_interest:
                    start_date = next(iter(stokvel_interest))[:7]
                else:
                    start_date = datetime.now().strftime("%Y-%m")

                previous_month_date = (
                    (datetime.strptime(start_date, "%Y-%m") - timedelta(days=1))
                    .replace(day=1)
                    .strftime("%Y-%m")
                )

                # Step 4: Calculate the user's share of the interest
                user_interest_response = requests.post(
                    BASE_READ_ROUTE,
                    json={
                        "query": (
                            """
                            SELECT strftime('%Y-%m', tx_date) AS month, SUM(amount) AS total_deposit
                            FROM TRANSACTIONS
                            WHERE user_id = :user_id
                            AND stokvel_id = :stokvel_id
                            AND tx_type = 'DEPOSIT'
                            AND tx_date > :previous_month_date
                            GROUP BY strftime('%Y-%m', tx_date)
                            """
                        ),
                        "parameters": {"user_id": user_id, "stokvel_id": stokvel_id, "previous_month_date": previous_month_date},
                    },
                    timeout=10,
                )

                user_interest_response.raise_for_status()
                user_monthly_deposits = {row["month"]: row["total_deposit"] for row in user_interest_response.json()}
                user_interest_response_data = user_interest_response.json()
                print("User Monthly deposits")
                print(user_interest_response_data)
                print(user_monthly_deposits)

                stokvel_deposit_response = requests.post(
                    BASE_READ_ROUTE,
                    json={
                        "query": (
                            """
                            SELECT strftime('%Y-%m', tx_date) AS month, SUM(amount) AS total_deposit
                            FROM TRANSACTIONS
                            WHERE stokvel_id = :stokvel_id
                            AND tx_type = 'DEPOSIT'
                            AND tx_date > :previous_month_date
                            GROUP BY strftime('%Y-%m', tx_date)
                            """
                        ),
                        "parameters": {"stokvel_id": stokvel_id, "previous_month_date": previous_month_date},
                    },
                    timeout=10,
                )

                stokvel_deposit_response.raise_for_status()
                stokvel_monthly_deposits = {row["month"]: row["total_deposit"] for row in stokvel_deposit_response.json()}

                user_total_interest = 0.0
                for month, interest_value in stokvel_interest.items():
                    previous_month = (
                        (datetime.strptime(month[:7], "%Y-%m") - timedelta(days=1))
                        .replace(day=1)
                        .strftime("%Y-%m")
                    )

                    if previous_month in user_monthly_deposits and previous_month in stokvel_monthly_deposits:
                        user_deposit = user_monthly_deposits[previous_month]
                        stokvel_deposit = stokvel_monthly_deposits[previous_month]

                        user_share = (user_deposit / stokvel_deposit) * interest_value/100 * stokvel_deposit
                        user_total_interest += user_share

                user_total_interest = round(user_total_interest, 2)

                # Insert interest calculation function in here

                # add interest to total_deposits to reach the correct value for amount variable
                amount = total_deposits + user_total_interest

            

                logging.info(f"Processing member: user_id={user_id}, amount={amount}, tx_type={tx_type}")
                print(f"Processing member: user_id={user_id}, amount={amount}, tx_type={tx_type}")
                # Step 3: Get the next unique transaction ID
                table_name = 'TRANSACTIONS'
                id_column = 'id'

                max_id_response = requests.post(
                    BASE_READ_ROUTE,
                    json={
                        "query": f"SELECT MAX({id_column}) AS max_id FROM {table_name}"
                    },
                    timeout=10,
                )

                # Raise an exception for HTTP error responses
                max_id_response.raise_for_status()

                # Parse the JSON response
                max_id_result = max_id_response.json()

                logging.info(f"Max ID result: {max_id_result}")
                print(f"Max ID result: {max_id_result}")

                if max_id_result and isinstance(max_id_result, list):
                    max_id = max_id_result[0].get('max_id', 0)
                    id = (max_id or 0) + 1
                else:
                    id = 1

                logging.info(f"Calculated transaction ID: {id}")

                # Step 4: Insert the transaction

                #Inser 

                insert_response = requests.post(
                    BASE_WRITE_ROUTE,
                    json={
                        "query": """
                        INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
                        VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)
                        """,
                        "parameters": {
                            "id": id,
                            "user_id": user_id,
                            "stokvel_id": stokvel_id,
                            "amount": amount,
                            "tx_type": tx_type,
                            "tx_date": tx_date.strftime('%Y-%m-%d %H:%M:%S'),  # Ensure string format
                            "created_at": tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "updated_at": tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                        },
                    },
                    timeout=10,
                )

                # Raise an exception for HTTP error responses
                insert_response.raise_for_status()

                logging.info(f"Inserted transaction ID {id} for user_id {user_id} and stokvel_id {stokvel_id}.")
                logging.info(f"Insert response status: {insert_response.status_code}, response text: {insert_response.text}")
                print(f"Insert response status: {insert_response.status_code}, response text: {insert_response.text}")

                parameters = {
                    "id": id,
                    "user_id": user_id,
                    "stokvel_id": stokvel_id,
                    "amount": amount,
                    "tx_type": tx_type,
                    "tx_date": tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "created_at": tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "updated_at": tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                }

                print(f"Inserting transaction with parameters: {(parameters)}")



                # Step 5: Update STOKVEL_MEMBERS if user_quote_id is not None
                if stokvel_quote_id is not None:
                    # Update user_quote_id to NULL
                    update_response = requests.post(
                        BASE_WRITE_ROUTE,
                        json={
                            "query": (
                                """
                                UPDATE STOKVEL_MEMBERS
                                SET user_quote_id = NULL
                                WHERE user_id = :user_id
                                """
                            ),
                            "parameters": {"user_id": user_id},
                        },
                        timeout=10,
                    )

                    #ILP Payment function for initial payment
                
                    # Raise an exception for HTTP error responses
                    update_response.raise_for_status()

                    logging.info(f"Updated user_quote_id for user_id: {user_id}")

                else: 

                    #ILP Payment function for recurring payments

                    logging.info("payout process completed successfully.")
        return

    except Exception as e:
        logging.error(f"Error in {main.__name__}: {e}")
        raise


if __name__ == "__main__":
    main(None)
