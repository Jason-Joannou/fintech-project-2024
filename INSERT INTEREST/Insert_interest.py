import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from typing import Optional

def insert_stokvel_interest(
    stokvel_id: Optional[str], 
    contribution_month: str,  # The specified contribution month in format yyyy-mm-dd
    ) -> bool:
    """
    Insert a new interest value for a stokvel into the INTEREST table.

    :param stokvel_id: The ID of the stokvel to insert interest for.
    :param contribution_month: The first/last day of the month when contributions were made (format: yyyy-mm-dd).
    :return: True if insertion was successful, False otherwise.
    """

    engine = sqlite_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # Get most recent payout date from STOKVELS table
            query = text(
                "SELECT MAX(tx_date) FROM TRANSACTIONS WHERE tx_type='payout' AND stokvel_id = :stokvel_id"
            )
            result = conn.execute(query, {"stokvel_id": stokvel_id})
            prev_payout = result.scalar()

            if not prev_payout:
                query = text(
                    "SELECT created_at FROM STOKVELS WHERE stokvel_id = :stokvel_id"
                )
                result = conn.execute(query, {"stokvel_id": stokvel_id})
                prev_payout = result.scalar()

            previous_payout_full = datetime.strptime(previous_payout_full, "%Y-%m-%d")
            previous_payout = previous_payout_full.strftime("%Y-%m")

            # Convert contribution_month to yyyy-mm format
            contribution_date = datetime.strptime(contribution_month, "%Y-%m-%d")
            contribution_year_month = contribution_date.strftime("%Y-%m")

            # Fetch all deposits between the previous payout date and the specified contribution month
            stokvel_deposits_query = text(
                """
                SELECT SUM(amount) AS total_deposit_stokvel
                FROM TRANSACTIONS
                WHERE stokvel_id = :stokvel_id
                AND tx_type = 'deposit'
                AND strftime('%Y-%m', tx_date) > :previous_payout
                AND strftime('%Y-%m', tx_date) <= :contribution_year_month
                """
            )

            stokvel_deposits_result = conn.execute(
                stokvel_deposits_query,
                {
                    "stokvel_id": stokvel_id,
                    "previous_payout": previous_payout,
                    "contribution_year_month": contribution_year_month,
                }
            )

            total_contributions = stokvel_deposits_result["total_deposit_stokvel"]

            if total_contributions is None:
                print("No contributions found between the last payout and the specified month.")
                return False

            # Calculate the interest date (last day of the month after contribution month)
            next_month = contribution_date + relativedelta(months=1)
            interest_date = (next_month + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
            interest_date_str = interest_date.strftime("%Y-%m-%d")

            # Generate a random multiplier (monthly interest rate) between 0% and 1.2%
            random_multiplier = random.uniform(0.00, 0.012)

            # Calculate interest value based on total contributions
            interest_value = total_contributions * random_multiplier

            # Insert the new interest entry into the INTEREST table
            insert_query = text(
                """
                INSERT INTO INTEREST (stokvel_id, date, interest_value)
                VALUES (:stokvel_id, :interest_date, :interest_value)
                """
            )

            conn.execute(insert_query, {
                "stokvel_id": stokvel_id,
                "interest_date": interest_date_str,
                "interest_value": interest_value
            })

           
            transaction.commit()
            return True

        except Exception as e:
            transaction.rollback()
            print(f"There was an error inserting the SQL data: {e}")
            return False
        
