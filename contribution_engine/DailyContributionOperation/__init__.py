import logging
from datetime import datetime, timezone
import requests

from azure.functions import TimerRequest

BASE_ROUTE = 'http://127.0.0.1:5000/database/query_db'

def main(DailyContributionOperation: TimerRequest) -> None:
    # Logic for azure function
    query = 'select * from USERS where user_id = :user_id'
    parameters = {'user_id': 1}
    results = requests.post(BASE_ROUTE, json={'query': query, 'parameters': parameters}).json()
    print(results) 

def contribution_trigger():
    """
    Check if the contribution process should be kicked off based on the NextDate in the database.
    """

    input_date = datetime.now().date().strftime('%Y-%m-%d')  # Only compare the date part
    tx_date = datetime.now()

    try:
        # Query to check if the NextDate matches the input date
            contribution_triggers = requests.post(BASE_ROUTE,
                json={'query':(
                    """
                    SELECT stokvel_id 
                    FROM CONTRIBUTIONS 
                    WHERE DATE(NextDate) = :input_date  -- Compare only the date part
                    """
                ),
                'parameter':{'input_date': input_date}
            }).json() # Use fetchall() to get all stokvel_ids

            # If results are found, kick off the contribution process
            if contribution_triggers:
                for trigger in contribution_triggers:
                    stokvel_id = trigger[0]

                    all_members = requests.post(BASE_ROUTE,
                        json={'query':("""
                            SELECT * 
                            FROM STOKVEL_MEMBERS 
                            WHERE stokvel_id = :stokvel_id
                            """)
                        ,
                        'parameters':{'stokvel_id': stokvel_id}
                    }).json()  # Fetch all members

                    for member in all_members:
                        try:
                            user_id = member[2]
                            amount = member[5]
                            user_quote_id = member[9]
                            tx_type = "DEPOSIT"
                            tx_date = tx_date
                            manageUrl = member[7]
                            previousToken = member[8]

                            sender_wallet_address = requests.post(BASE_ROUTE,
                                json={'query':(
                                    """
                                    SELECT ILP_wallet
                                    FROM USERS 
                                    WHERE user_id = :user_id
                                    """
                                ),
                                'parameters':{'user_id': user_id}
                            }).json()

                            receiving_wallet_address = requests.post(BASE_ROUTE,
                                json={'query':(
                                    """
                                    SELECT ILP_wallet
                                    FROM STOKVELS 
                                    WHERE stokvel_id = :stokvel_id
                                    """
                                ),
                                'parameters':{'stokvel_id': stokvel_id}
                            }).json()


                            # Check if a payment is needed based on user_quote_id
                            if user_quote_id is not None:
                                # Create initial payment
                                # create_inital_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken, user_quote_id)

                                requests.post(BASE_ROUTE,
                                    json={'query':(
                                        """
                                        UPDATE STOKVEL_MEMBERS
                                        SET user_quote_id = NULL
                                        WHERE user_id = :user_id
                                        """
                                    ),
                                    'parameters':{'user_id': user_id}
                                }).json

                                insert_transaction(conn,user_id, stokvel_id, amount, tx_type, tx_date)

                            else: 
                                # Create contribution payment
                                # create_contribution_payment(sender_wallet_address, receiving_wallet_address, manageUrl, previousToken)

                                insert_transaction(conn,user_id, stokvel_id, amount, tx_type, tx_date) 
                                
                                print(f"Ran the recurring payment")                     

                        except Exception as e:
                            print(f"Error attempting to make contribution for user {user_id}: {str(e)}")
                            return False

            else:
                print("No contributions scheduled for today.")
                return True  # Indicate no contributions found but process is complete

    except Exception as e:
        print(f"Error checking contribution trigger: {str(e)}")
        return False

if __name__ == "__main__":
    contribution_trigger()
