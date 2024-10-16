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

from datetime import datetime

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
    contributions = {}
    current_next_date = datetime.now()
    for j in range(1,12):
        print(f"Month: {j}")
        for userid, wallet in user_id_wallets.items():
                
                if userid not in contributions:
                    contributions[userid] = 0
                
                stokvel_members_details = get_stokvel_member_details(stokvel_id, userid)
                print("add recurring payment")
                payload = {
                    "sender_wallet_address":wallet,
                    "receiving_wallet_address":"https://ilp.rafiki.money/alices_stokvel",
                    "manageUrl":stokvel_members_details.get('user_payment_URI'),
                    "previousToken":stokvel_members_details.get('user_payment_token'),
                    "contributionValue": stokvel_members_details.get('contribution_amount')
                }

                response = requests.post(node_server_recurring_payment, json=payload)

                print("RESPONSE: \n", response.json())
        

                new_token = response.json()['token']
                new_uri = response.json()['manageurl']
                
                update_user_contribution_token_uri(stokvel_id, userid, new_token, new_uri)
                
                contributions[userid] += stokvel_members_details.get('contribution_amount')
                # current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")
        time.sleep(30)


def run_payout_simulation(stokvel_id:int, user_id_wallets:dict): #this will be a dict of all of the users that we need to pay out
    current_next_date = "2024-10-10"
    for j in range(0,5):
        for userid, wallet in user_id_wallets.items():
                stokvel_members_details = get_stokvel_member_details(stokvel_id, userid)

                print("add recurring payment")
                payload = {
                    "sender_wallet_address":"https://ilp.rafiki.money/alices_stokvel",
                    "receiving_wallet_address":wallet,
                    "manageUrl":stokvel_members_details.get('stokvel_payment_URI'),
                    "previousToken":stokvel_members_details.get('stokvel_payment_token'),
                    "payout_value": str(1589+j)
                }

                response = requests.post(node_server_recurring_payment_with_interest, json=payload)

                print("RESPONSE: \n", response.json())
        
                new_token = response.json()['token']
                new_uri = response.json()['manageurl']
                
                update_stokvel_token_uri(stokvel_id, userid, new_token, new_uri)
                current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")
        time.sleep(30)

if __name__ == "__main__":


    #arguments
    stokvel_id = 1
    user_id_wallets = {
        "980618": "https://ilp.rafiki.money/bob_account",
        "880618": "https://ilp.rafiki.money/joe_account"
    }

    run_contribution_simulation(stokvel_id, user_id_wallets)

    time.sleep(30)


    print("Both methods have completed.")