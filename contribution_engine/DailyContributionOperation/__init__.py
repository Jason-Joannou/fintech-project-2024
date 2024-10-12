import logging
from datetime import datetime, timezone

import requests
from azure.functions import TimerRequest

BASE_READ_ROUTE = "http://127.0.0.1:5000/database/query_db"
BASE_WRITE_ROUTE = "http://127.0.0.1:5000/database/write_db"


def main(DailyContributionOperation: TimerRequest) -> None:
    """
    Main function to trigger daily contributions.
    """

    input_date = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")  # Use UTC
    tx_date = datetime.now(timezone.utc)  # Use UTC

    try:
        # Step 1: Check if the contribution process should be kicked off
        contribution_trigger_date_response = requests.post(
            BASE_READ_ROUTE,
            json={
                "query": (
                    """
                    SELECT stokvel_id
                    FROM CONTRIBUTIONS
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                "parameters": {"input_date": input_date},
            },
            timeout=10,
        )

        # Raise an exception for HTTP error responses
        contribution_trigger_date_response.raise_for_status()

        # Parse the JSON response
        contribution_trigger_date = contribution_trigger_date_response.json()

        logging.info(f"Contribution triggers: {contribution_trigger_date}")

        if not contribution_trigger_date:
            logging.info("No contribution triggers found. Exiting.")
            return

        # Step 2: Trigger the contribution process
        logging.info("Triggering contribution process...")

        for trigger_date in contribution_trigger_date:
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
                try:
                    user_id = member["user_id"]
                    amount = member["contribution_amount"]
                    user_quote_id = member["user_quote_id"]
                    tx_type = "DEPOSIT"
                    manageUrl = member["user_payment_URI"]
                    previousToken = member["user_payment_token"]

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

                    # Step 5: Insert the transaction
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



                    # Step 4: Update STOKVEL_MEMBERS if user_quote_id is not None
                    if user_quote_id is not None:
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

                        # Raise an exception for HTTP error responses
                        update_response.raise_for_status()

                        logging.info(f"Updated user_quote_id for user_id: {user_id}")

                except Exception as e:
                    logging.error(f"Error attempting to make contribution for user {user_id}: {str(e)}")
                    # Depending on your needs, you might want to continue processing other members or halt
                    continue  # Continue with the next member

        logging.info("Contribution process completed successfully.")
        return

    except Exception as e:
        logging.error(f"Error in {main.__name__}: {e}")
        raise


if __name__ == "__main__":
    main(None)
