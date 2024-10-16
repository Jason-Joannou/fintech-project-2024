import logging
from datetime import datetime, timedelta, timezone

import requests
from azure.functions import TimerRequest
from dateutil.relativedelta import relativedelta

BASE_READ_ROUTE = "http://127.0.0.1:5000/database/query_db"
BASE_WRITE_ROUTE = "http://127.0.0.1:5000/database/write_db"

node_server_create_initial_payment = (
    "http://localhost:3001/payments/initial_outgoing_payment"
)

node_server_recurring_payment = (
    "http://localhost:3001/payments/process_recurring_payments"
)
node_server_recurring_payment_with_interest = (
    "http://localhost:3001/payments/process_recurring_winterest_payment"
)


def main(DailyContributionOperation: TimerRequest) -> None:
    """
    Main function to trigger daily contributions.
    """

    input_date = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")  # Use UTC
    tx_date = datetime.now(timezone.utc)  # Use UTC

    print(input_date)

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
        print(contribution_trigger_date)

        if not contribution_trigger_date:
            logging.info("No contribution triggers found. Exiting.")
            print("No contribution triggers found. Exiting.")
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
            print(f"Members for stokvel_id {stokvel_id}: {stokvel_members}")

            if not stokvel_members:
                logging.info(
                    f"No members found for stokvel_id {stokvel_id}. Continuing to next stokvel."
                )
                continue  # Continue with the next stokvel_id

            for member in stokvel_members:

                user_id = member["user_id"]
                amount = member["contribution_amount"]
                user_quote_id = member["user_quote_id"]
                tx_type = "DEPOSIT"
                manageUrl = member["user_payment_URI"]
                previousToken = member["user_payment_token"]

                logging.info(
                    f"Processing member: user_id={user_id}, amount={amount}, tx_type={tx_type}"
                )
                print(
                    f"Processing member: user_id={user_id}, amount={amount}, tx_type={tx_type}"
                )
                # Step 3: Get the next unique transaction ID
                table_name = "TRANSACTIONS"
                id_column = "id"

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
                    max_id = max_id_result[0].get("max_id", 0)
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
                            "tx_date": tx_date.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),  # Ensure string format
                            "created_at": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "updated_at": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                        },
                    },
                    timeout=10,
                )

                # Raise an exception for HTTP error responses
                insert_response.raise_for_status()

                logging.info(
                    f"Inserted transaction ID {id} for user_id {user_id} and stokvel_id {stokvel_id}."
                )
                logging.info(
                    f"Insert response status: {insert_response.status_code}, response text: {insert_response.text}"
                )
                print(
                    f"Insert response status: {insert_response.status_code}, response text: {insert_response.text}"
                )

                parameters = {
                    "id": id,
                    "user_id": user_id,
                    "stokvel_id": stokvel_id,
                    "amount": amount,
                    "tx_type": tx_type,
                    "tx_date": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "created_at": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                }

                print(f"Inserting transaction with parameters: {(parameters)}")

                # Step 4: Update STOKVEL_MEMBERS if user_quote_id is not None
                if user_quote_id is not None:
                    # Update user_quote_id to NULL
                    # region ILP INITIAL PAYMENT

                    current_next_date = input_date
                    query = """
                        SELECT STOKVEL_MEMBERS.*,
                        USERS.ILP_Wallet,
                            STOKVELS.payout_frequency_duration,
                            STOKVELS.contribution_period
                            FROM STOKVEL_MEMBERS

                            JOIN USERS ON STOKVEL_MEMBERS.user_id = USERS.user_id
                            JOIN STOKVELS ON STOKVEL_MEMBERS.stokvel_id = STOKVELS.stokvel_id WHERE STOKVEL_MEMBERS.stokvel_id = :stokvel_id
                            AND STOKVEL_MEMBERS.user_id = :user_id
                        """
                    parameters = {"stokvel_id": stokvel_id, "user_id": user_id}

                    # Send the POST request to the API
                    stokvel_members_details_response = requests.post(
                        BASE_READ_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": query,
                            "parameters": parameters,
                        },
                        timeout=10,
                    )

                    # Check for HTTP errors
                    stokvel_members_details_response.raise_for_status()

                    # Parse the JSON response
                    stokvel_members_result = stokvel_members_details_response.json()

                    # If result is found, return it
                    stokvel_members_details = stokvel_members_result[
                        0
                    ]  # Assuming it's the first record

                    payload = {
                        "quote_id": stokvel_members_details["user_quote_id"],
                        "continueUri": stokvel_members_details["user_payment_URI"],
                        "continueAccessToken": stokvel_members_details[
                            "user_payment_token"
                        ],
                        "walletAddressURL": stokvel_members_details["ILP_wallet"],
                        "interact_ref": str(
                            stokvel_members_details["user_interaction_ref"]
                        ),
                    }

                    print("PAYLOAD: \n", payload)

                    initial_payment_response = requests.post(
                        node_server_create_initial_payment, json=payload, timeout=10
                    )

                    print("RESPONSE: \n", initial_payment_response.json())

                    new_token = initial_payment_response.json()["token"]
                    new_uri = initial_payment_response.json()["manageurl"]

                    print("NEW DETAILS")
                    print(new_token)
                    print(new_uri)

                    # update_stokvel_token_uri(stokvel_id, user_id, new_token, new_uri)

                    update_token_url_query = """
                            UPDATE STOKVEL_MEMBERS
                            SET user_payment_token = :new_token,
                                user_payment_URI = :new_uri,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE stokvel_id = :stokvel_id and user_id = :user_id
                        """

                    update_token_url_parameters = {
                        "new_token": new_token,
                        "new_uri": new_uri,
                        "stokvel_id": stokvel_id,
                        "user_id": user_id,
                    }

                    # Send the POST request to the API
                    stokvel_members_token_url_update_response = requests.post(
                        BASE_WRITE_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": update_token_url_query,
                            "parameters": update_token_url_parameters,
                        },
                        timeout=10,
                    )
                    # Check for HTTP errors
                    stokvel_members_token_url_update_response.raise_for_status()

                    # update to the next contribution date

                    if stokvel_members_details["contribution_period"] == "Days":
                        period_delta = timedelta(days=1)  # Increment by 1 day
                    elif stokvel_members_details["contribution_period"] == "Week":
                        period_delta = timedelta(weeks=1)  # Increment by 1 week
                    elif stokvel_members_details["contribution_period"] == "Months":
                        period_delta = relativedelta(months=1)  # Increment by 1 month
                    elif stokvel_members_details["contribution_period"] == "Years":
                        period_delta = relativedelta(years=1)  # Increment by 1 year
                    else:
                        raise ValueError("Invalid contribution period specified.")

                    # Calculate the next contribution date
                    current_next_date_dt = datetime.strptime(
                        current_next_date, "%Y-%m-%d"
                    )
                    next_date = (current_next_date_dt + period_delta).strftime(
                        "%Y-%m-%d"
                    )

                    update_next_contribution_query = """
                            UPDATE CONTRIBUTIONS
                            SET PreviousDate = :PreviousDate, NextDate = :NextDate
                            WHERE stokvel_id = :stokvel_id
                        """

                    date_update_parameters = {
                        "PreviousDate": current_next_date,  # Set the current NextDate as PreviousDate
                        "NextDate": next_date,  # Set the new calculated NextDate
                        "stokvel_id": stokvel_id,
                    }

                    # Send the POST request to the API
                    member_contributions_update_response = requests.post(
                        BASE_WRITE_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": update_next_contribution_query,
                            "parameters": date_update_parameters,
                        },
                        timeout=10,
                    )
                    # Check for HTTP errors
                    member_contributions_update_response.raise_for_status()

                    # endregion

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

                else:
                    # region ILP RECURRING CONTRIBUTION PAYMENT
                    current_next_date = input_date
                    query = """
                        SELECT STOKVEL_MEMBERS.*,
                        USERS.ILP_Wallet,
                            STOKVELS.payout_frequency_duration,
                            STOKVELS.contribution_period
                            FROM STOKVEL_MEMBERS

                            JOIN USERS ON STOKVEL_MEMBERS.user_id = USERS.user_id
                            JOIN STOKVELS ON STOKVEL_MEMBERS.stokvel_id = STOKVELS.stokvel_id WHERE STOKVEL_MEMBERS.stokvel_id = :stokvel_id
                            AND STOKVEL_MEMBERS.user_id = :user_id
                        """
                    parameters = {"stokvel_id": stokvel_id, "user_id": user_id}

                    # Send the POST request to the API
                    stokvel_members_details_response = requests.post(
                        BASE_READ_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": query,
                            "parameters": parameters,
                        },
                        timeout=10,
                    )

                    # Check for HTTP errors
                    stokvel_members_details_response.raise_for_status()

                    # Parse the JSON response
                    stokvel_members_result = stokvel_members_details_response.json()

                    # If result is found, return it
                    stokvel_members_details = stokvel_members_result[
                        0
                    ]  # Assuming it's the first record

                    print("add recurring payment")
                    payload = {
                        "sender_wallet_address": stokvel_members_details["ILP_wallet"],
                        "receiving_wallet_address": "$ilp.rafiki.money/masterstokveladdress",
                        "manageUrl": stokvel_members_details["user_payment_URI"],
                        "previousToken": stokvel_members_details["user_payment_token"],
                    }

                    print("PAYLOAD: \n", payload)

                    recurring_payment_response = requests.post(
                        node_server_recurring_payment, json=payload, timeout=10
                    )
                    print("RESPONSE: \n", recurring_payment_response.json())

                    recurring_payment_response.raise_for_status()  # raise error making payment with node server

                    new_token = recurring_payment_response.json()["token"]
                    new_uri = recurring_payment_response.json()["manageurl"]

                    print("NEW DETAILS")
                    print(new_token)
                    print(new_uri)

                    # update_stokvel_token_uri(stokvel_id, user_id, new_token, new_uri)

                    update_token_url_query = """
                            UPDATE STOKVEL_MEMBERS
                            SET user_payment_token = :new_token,
                                user_payment_URI = :new_uri,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE stokvel_id = :stokvel_id and user_id = :user_id
                        """

                    update_token_url_parameters = {
                        "new_token": new_token,
                        "new_uri": new_uri,
                        "stokvel_id": stokvel_id,
                        "user_id": user_id,
                    }

                    # Send the POST request to the API
                    stokvel_members_token_url_update_response = requests.post(
                        BASE_WRITE_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": update_token_url_query,
                            "parameters": update_token_url_parameters,
                        },
                        timeout=10,
                    )
                    # Check for HTTP errors
                    stokvel_members_token_url_update_response.raise_for_status()

                    # update to the next contribution date

                    if stokvel_members_details["contribution_period"] == "Days":
                        period_delta = timedelta(days=1)  # Increment by 1 day
                    elif stokvel_members_details["contribution_period"] == "Week":
                        period_delta = timedelta(weeks=1)  # Increment by 1 week
                    elif stokvel_members_details["contribution_period"] == "Months":
                        period_delta = relativedelta(months=1)  # Increment by 1 month
                    elif stokvel_members_details["contribution_period"] == "Years":
                        period_delta = relativedelta(years=1)  # Increment by 1 year
                    else:
                        raise ValueError("Invalid contribution period specified.")

                    # Calculate the next contribution date
                    next_date = current_next_date + period_delta

                    update_next_contribution_query = """
                            UPDATE CONTRIBUTIONS
                            SET PreviousDate = :PreviousDate, NextDate = :NextDate
                            WHERE stokvel_id = :stokvel_id
                        """

                    date_update_parameters = {
                        "PreviousDate": current_next_date,  # Set the current NextDate as PreviousDate
                        "NextDate": next_date,  # Set the new calculated NextDate
                        "stokvel_id": stokvel_id,
                    }

                    # Send the POST request to the API
                    member_contributions_update_response = requests.post(
                        BASE_WRITE_ROUTE,  # Assuming you're using a different route for reads
                        json={
                            "query": update_next_contribution_query,
                            "parameters": date_update_parameters,
                        },
                        timeout=10,
                    )
                    # Check for HTTP errors
                    member_contributions_update_response.raise_for_status()

                    # endregion

        logging.info("Contribution process completed successfully.")
        return

    except Exception as e:
        logging.error(f"Error in {main.__name__}: {e}")
        raise


if __name__ == "__main__":
    main(None)
