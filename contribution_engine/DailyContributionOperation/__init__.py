import logging
from datetime import datetime, timezone

import requests
from azure.functions import TimerRequest

BASE_READ_ROUTE = "http://127.0.0.1:5000/database/query_db"
BASE_WRITE_ROUTE = "http://127.0.0.1:5000/database/write_db"


def main(DailyContributionOperation: TimerRequest) -> None:
    """
    docstring
    """

    input_date = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")  # Use UTC
    tx_date = datetime.now(timezone.utc)  # Use UTC

    try:
        # Step 1: Check if the contribution process should be kicked off
        contribution_trigger_date = requests.post(
            BASE_READ_ROUTE,
            json={
                "query": (
                    """
                    SELECT stokvel_id
                    FROM CONTRIBUTIONS
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                "parameter": {"input_date": input_date},
            },
            timeout=10,
        )

        contribution_trigger_date.raise_for_status()
        contribution_trigger_date = contribution_trigger_date.json()

        if not contribution_trigger_date:
            logging.info("No contribution triggers found. Exiting.")
            return

        # Step 2: Trigger the contribution process
        logging.info("Triggering contribution process...")

        for trigger_date in contribution_trigger_date:
            stokvel_id = trigger_date["stokvel_id"]

            stokvel_members = requests.post(
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
            )  # Fetch all members

            stokvel_members.raise_for_status()
            stokvel_members = stokvel_members.json()

            if not stokvel_members:
                logging.info("No members found. Exiting.")
                return

            for member in stokvel_members:
                user_id = member["user_id"]
                amount = member["amount"]
                user_quote_id = member["user_quote_id"]
                tx_type = "DEPOSIT"
                tx_date = tx_date
                manageUrl = member["manageUrl"]
                previousToken = member["previousToken"]

                if user_quote_id is not None:
                    # Create initial payment (ILP API)
                    # create_inital_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, user_quote_id)
                    response = requests.post(
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
                    response.raise_for_status()

                    response = requests.post(
                        BASE_WRITE_ROUTE,
                        json={
                            "query": """
                            INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
                            VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)""",
                            "parameters": {
                                "user_id": user_id,
                                "stokvel_id": stokvel_id,
                                "amount": amount,
                                "tx_type": tx_type,
                                "tx_date": tx_date,
                                "created_at": datetime.now(),
                                "updated_at": datetime.now(),
                            },
                        },
                        timeout=10,
                    )
                    response.raise_for_status()

                else:

                    # Create contribution payment (ILP API)
                    # create_contribution_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken)

                    response = requests.post(
                        BASE_WRITE_ROUTE,
                        json={
                            "query": """
                                INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
                                VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)""",
                            "parameters": {
                                "user_id": user_id,
                                "stokvel_id": stokvel_id,
                                "amount": amount,
                                "tx_type": tx_type,
                                "tx_date": tx_date,
                                "created_at": datetime.now(),
                                "updated_at": datetime.now(),
                            },
                        },
                        timeout=10,
                    )
                    response.raise_for_status()
        logging.info("Contribution process triggered.")
        return
    except Exception as e:
        print(f"Error in {main.__name__}: {e}")
        raise


if __name__ == "__main__":
    main(None)
