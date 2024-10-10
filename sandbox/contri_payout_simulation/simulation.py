from database.contribution_payout_queries import (
    update_next_contributions_dates,
    update_next_payout_dates,
    update_stokvel_token_uri,
    update_user_contribution_token_uri
)

from database.stokvel_queries.queries import (
     get_stokvel_member_details
)

import threading
import time

import threading
import time

import requests

# Define the first method

node_server_initiate_grant = "http://localhost:3000/incoming-payment-setup"
node_server_initiate_stokvelpayout_grant = "http://localhost:3000/incoming-payment-setup-stokvel-payout"

node_server_create_initial_payment = "http://localhost:3000/create-initial-outgoing-payment"

node_server_recurring_payment = "http://localhost:3000/process-recurring-payment"
node_server_recurring_payment_with_interest = "http://localhost:3000/process-recurring-winterest-payment"

def run_contribution_simulation(stokvel_id:int, user_id_wallets:dict):
    i = 0
    current_next_date = "2024-10-10"
    for userid, wallet in user_id_wallets.items():
        stokvel_members_details = get_stokvel_member_details(stokvel_id, userid)
        print("add initial payment")
        
        payload = {
            "quote_id": stokvel_members_details.get('user_quote_id'),                                    
            "continueUri": stokvel_members_details.get('user_payment_token'),
            "continueAccessToken": stokvel_members_details.get('user_payment_URI'),
            "walletAddressURL": str(wallet)
        }

        response = requests.post(node_server_create_initial_payment, json=payload)

        print("RESPONSE: \n", response.json())
  

        new_token = response.json()['token']
        new_uri = response.json()['manageurl']
        
        update_user_contribution_token_uri(stokvel_id, userid, new_token, new_uri)
        current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")

    time.sleep(30)

    ii = 0
    for j in range(0,5):
        for userid, wallet in user_id_wallets.items():
                stokvel_members_details = get_stokvel_member_details(stokvel_id, userid)

                print("add recurring payment")
                payload = {
                    "sender_wallet_address":"https://ilp.rafiki.money/bob_account",
                    "receiving_wallet_address":"https://ilp.rafiki.money/alices_stokvel",
                    "manageUrl":stokvel_members_details.get('user_payment_URI'),
                    "previousToken":stokvel_members_details.get('user_payment_token'),
                }

                response = requests.post(node_server_create_initial_payment, json=payload)

                print("RESPONSE: \n", response.json())
        

                new_token = response.json()['token']
                new_uri = response.json()['manageurl']
                
                update_user_contribution_token_uri(stokvel_id, userid, new_token, new_uri)
                current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")
        time.sleep(30)


def run_payout_simulation(stokvel_id:int, user_id_wallets:dict): #this will be a dict of all of the users that we need to pay out
    i = 0
    current_next_date = "2024-10-10"

    for userid, wallet in user_id_wallets.items():
        print("add initial payment")
        print("sv response containing next token details")

        new_uri = "https://www.example.com" + str(i)
        new_token = "token" + str(i)
        update_stokvel_token_uri(stokvel_id, userid, new_token, new_uri)
        current_next_date = update_next_payout_dates(current_next_date, stokvel_id, "Years")
        i += 1
    
    time.sleep(30)

    ii = 0
    for j in range(0,5):
        for userid, wallet in user_id_wallets.items():
                print("add recurring payment")
                print("sv response containing next token details")

                new_uri = "https://www.example.com" + str(ii)
                new_token = "token" + str(ii)
                update_stokvel_token_uri(stokvel_id, userid, new_token, new_uri)
                current_next_date = update_next_payout_dates(current_next_date, stokvel_id, "Years")
                ii += 1
        time.sleep(30)

if __name__ == "__main__":


    #arguments
    stokvel_id = 12
    user_id_wallets = {
        "980618": "https://ilp.rafiki.money/bob_account",
    }

    # thread1 = threading.Thread(target=run_contribution_simulation(stokvel_id=stokvel_id, user_id_wallets=user_id_wallets))
    # thread2 = threading.Thread(target=run_payout_simulation(stokvel_id=stokvel_id, user_id_wallets=user_id_wallets))

    thread1 = threading.Thread(target=run_contribution_simulation, args=(stokvel_id, user_id_wallets))
    # thread2 = threading.Thread(target=run_payout_simulation, args=(stokvel_id, user_id_wallets))


    # Start the threads
    thread1.start()

    time.sleep(30)

    # thread2.start()

    # Wait for both threads to complete
    thread1.join()
    # thread2.join()

    print("Both methods have completed.")