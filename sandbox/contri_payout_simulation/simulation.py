from database.contribution_payout_queries import (
    update_next_contributions_dates,
    update_next_payout_dates,
    update_stokvel_token_uri,
    update_user_contribution_token_uri
)

import threading
import time

import threading
import time

# Define the first method

def run_contribution_simulation(stokvel_id:int, user_id_wallets:dict):
    i = 0
    current_next_date = "2024-10-10"
    for userid, wallet in user_id_wallets.items():
        print("add initial payment")
        print("user response containing next token details")
        new_uri = "https://www.example.com" + str(i)
        new_token = "token" + str(i)
        update_user_contribution_token_uri(stokvel_id, userid, new_token, new_uri)
        current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")
        i += 1
    
    time.sleep(30)

    ii = 0
    for j in range(0,5):
        for userid, wallet in user_id_wallets.items():
                print("add recurring payment")
                print("user response containing next token details")

                new_uri = "https://www.example.com" + str(ii)
                new_token = "token" + str(ii)
                update_user_contribution_token_uri(stokvel_id, userid, new_token, new_uri)
                current_next_date = update_next_contributions_dates(current_next_date, stokvel_id, "Months")
                ii += 1
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
    thread2 = threading.Thread(target=run_payout_simulation, args=(stokvel_id, user_id_wallets))


    # Start the threads
    thread1.start()

    time.sleep(30)

    thread2.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

    print("Both methods have completed.")