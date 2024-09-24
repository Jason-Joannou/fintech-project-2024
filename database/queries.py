# from .sql_connection import sql_connection
from sqlalchemy import text, exc

from datetime import datetime

from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()

def get_next_unique_id(conn, table_name, id_column):
    """
    Get the next unique id for the given table and id column.
    """
    result = conn.execute(
        text(f"SELECT MAX({id_column}) FROM {table_name}")
    ).fetchone()
    # If no result exists (table is empty), return 1, otherwise increment the max id
    return (result[0] or 0) + 1

def create_wallet(conn, entity_id, wallet_type, entity_type):
    """
    Create a wallet for a user or stokvel in the user_wallet or stokvel_wallet table.
    
    Args:
        conn: SQLite connection object.
        entity_id: The ID of the user or stokvel.
        wallet_type: Type of wallet ('ILP' or 'MOMO'). Default is 'ILP'.
        entity_type: Type of entity ('user' or 'stokvel'). Default is 'user'.
    
    Returns:
        bool: True if wallet is successfully created, False otherwise.
    """
    try:
        # Determine the wallet table based on entity type
        wallet_table = 'user_wallet' if entity_type == 'user' else 'stokvel_wallet'
        
        # Generate unique wallet ID
        wallet_id = get_next_unique_id(conn, wallet_table, 'id')
        
        # Generate wallet name based on entity type and wallet type
        wallet_name = f"{wallet_type}_{entity_type}_{entity_id}_wallet"
        
        # Prepare wallet entry data
        wallet_entry = {
            'id': wallet_id,
            'user_id': entity_id,  # Can refer to user_id or stokvel_id depending on entity type
            'user_wallet': wallet_name,
            'UserBalance': 500.0  # Default balance of 500
        }
        
        # SQL query to insert wallet data into the appropriate table
        insert_wallet_query = f"""
            INSERT INTO {wallet_table} (id, user_id, user_wallet, UserBalance)
            VALUES (:id, :user_id, :user_wallet, :UserBalance)
        """
        
        # Execute the insert query
        conn.execute(text(insert_wallet_query), wallet_entry)
        conn.commit()
        
        print(f"Success: {wallet_type} wallet '{wallet_name}' added to {wallet_table}.")
        return True
    
    except exc.IntegrityError as e:
        print(f"Failure: Could not add {wallet_type} wallet for {entity_type} ID {entity_id}. Error: {e}")
        return False

# Usage example
# create_wallet(conn, entity_id=1, wallet_type='ILP', entity_type='user')

   
def create_user(user_number, user_name, user_surname):
    try:
        with sqlite_conn.connect() as conn:
            # Get unique user_id
            user_id = get_next_unique_id(conn, 'USERS', 'user_id')

            # Insert user data into USERS table
            new_user = {
                'user_id': user_id,
                'user_number': user_number,
                'user_name': user_name,
                'user_surname': user_surname,
                'ILP_wallet': f"ILP_{user_id}_wallet",  # Placeholder for wallet name
                'MOMO_wallet': f"MOMO_{user_id}_wallet",  # Placeholder for wallet name
                'verified_KYC': 1,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            insert_user_query = """
                INSERT INTO USERS (user_id, user_number, user_name, user_surname, ILP_wallet, MOMO_wallet,
                                   verified_KYC, created_at, updated_at)
                VALUES (:user_id, :user_number, :user_name, :user_surname, :ILP_wallet, :MOMO_wallet,
                        :verified_KYC, :created_at, :updated_at)
            """
            conn.execute(text(insert_user_query), new_user)
            conn.commit()
            print(f"Success: New user '{user_name} {user_surname}' added to USERS table.")

            # Create ILP and MOMO wallets for the user
            create_wallet(conn, user_id, wallet_type='ILP', entity_type='user')
            create_wallet(conn, user_id, wallet_type='MOMO', entity_type='user')

    except Exception as e:
        print(f"An error occurred: {e}")



def create_stokvel(stokvel_name, total_members, min_contributing_amount, max_number_of_contributors, Total_contributions):
    try:
        with sqlite_conn.connect() as conn:
            # Get unique stokvel_id
            stokvel_id = get_next_unique_id(conn, 'STOKVELS', 'stokvel_id')

            # Insert stokvel data into STOKVELS table
            new_stokvel = {
                'stokvel_id': stokvel_id,
                'stokvel_name': stokvel_name,
                'ILP_wallet': f"ILP_{stokvel_id}_wallet",  # Placeholder for wallet name
                'MOMO_wallet': f"MOMO_{stokvel_id}_wallet",  # Placeholder for wallet name
                'total_members': total_members,
                'min_contributing_amount': min_contributing_amount,
                'max_number_of_contributors': max_number_of_contributors,
                'Total_contributions': Total_contributions,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            insert_stokvel_query = """
                INSERT INTO STOKVELS (stokvel_id, stokvel_name, ILP_wallet, MOMO_wallet, total_members, 
                                      min_contributing_amount, max_number_of_contributors, Total_contributions, 
                                      created_at, updated_at)
                VALUES (:stokvel_id, :stokvel_name, :ILP_wallet, :MOMO_wallet, :total_members, 
                        :min_contributing_amount, :max_number_of_contributors, :Total_contributions, 
                        :created_at, :updated_at)
            """
            conn.execute(text(insert_stokvel_query), new_stokvel)
            conn.commit()
            print(f"Success: New stokvel '{stokvel_name}' added to STOKVELS table.")

            # Create ILP and MOMO wallets for the stokvel
            create_wallet(conn, stokvel_id, wallet_type='ILP', entity_type='stokvel')
            create_wallet(conn, stokvel_id, wallet_type='MOMO', entity_type='stokvel')

    except Exception as e:
        print(f"An error occurred: {e}")

# Next functions to write are: 
# Customize stokvel create function to assign an admin to the admin table
# Allow users to apply to join a stokvel



# Example usage


def check_if_number_exists_sqlite(from_number):
    """
    docstring
    """

    query = "SELECT * FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()
        if result:
            return True

        return False
 



if __name__ == "__main__":
    #create_user('+1234567', 'John', 'Doe')
    create_stokvel('My Stokvel', 10, 100.0, 15, 1000.0)