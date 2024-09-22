# from .sql_connection import sql_connection
from sqlalchemy import text

from .sqlite_connection import SQLiteConnection
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from datetime import datetime

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()



def check_if_number_exists_sqlite(from_number):

    """
    docstring
    """

    query = "SELECT * FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()
        print(result)
        if result:
            return True

        return False

def insert_user(user_id, user_number, user_name, user_surname, ILP_wallet, MOMO_wallet = 'test', verified_KYC = 1, created_at=None, updated_at=None):

        """
        Inserts a new user into the USERS table.

        Args:
            user_id (int): The user's ID.
            user_number (str): The user's number.
            user_name (str): The user's name.
            user_surname (str): The user's surname.
            ILP_wallet (str): The user's ILP wallet.
            MOMO_wallet (str): The user's MOMO wallet.
            verified_KYC (int): KYC verification status (0 or 1).
            created_at (str, optional): The timestamp when the user was created. Defaults to current time if not provided.
            updated_at (str, optional): The timestamp when the user was last updated. Defaults to current time if not provided.
        """
        if created_at is None:
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if updated_at is None:
            updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        insert_query = """
        INSERT INTO USERS (
            user_id, user_number, user_name, user_surname, ILP_wallet, 
            MOMO_wallet, verified_KYC, created_at, updated_at
        ) VALUES (
            :user_id, :user_number, :user_name, :user_surname, :ILP_wallet, 
            :MOMO_wallet, :verified_KYC, :created_at, :updated_at
        )
        """

        parameters = {
            'user_id': user_id,
            'user_number': user_number,
            'user_name': user_name,
            'user_surname': user_surname,
            'ILP_wallet': ILP_wallet,
            'MOMO_wallet': MOMO_wallet,
            'verified_KYC': verified_KYC,
            'created_at': created_at,
            'updated_at': updated_at
        }

        try:
            with sqlite_conn.connect() as conn:
                print("Connected in user insert")
                result = conn.execute(text(insert_query), parameters)
                conn.commit()
                
                if result.rowcount > 0:
                    print(f"Insert successful, {result.rowcount} row(s) affected.")
                else:
                    print("Insert failed.")
        except Exception as e:
            print(f"Error occurred during insert: {e}")

def insert_wallet(user_id, user_wallet, userbalance):
    """
        Inserts a new user wallet into the USER_WALLET table.

        Args:
            user_id (int): The user's ID.
            user_wallet (str): The user's wallet address.
            userbalance (float): The user's balance in the wallet.
    """

    insert_query = """
    INSERT INTO USER_WALLET (
        user_id, user_wallet, UserBalance
    ) VALUES (
        :user_id, :user_wallet, :UserBalance
    )
    """

    parameters = {
        'user_id': user_id,
        'user_wallet': user_wallet,
        'UserBalance': userbalance
    }

    try:
        with sqlite_conn.connect() as conn:
            print("Connected in wallet insert")
            result = conn.execute(text(insert_query), parameters)
            conn.commit()

            if result.rowcount > 0:
                print(f"Insert successful, {result.rowcount} row(s) affected.")
            else:
                print("Insert failed.")
    except Exception as e:
        print(f"Error occurred during insert: {e}")
    

def add_user_wallet_to_db(user, wallet):
    """
    Onboards a new user by inserting them into the USERS table, and a corresponding entry in the USER_WALLET table.

    Args:
        user (utils.user.User): The user to be onboarded.
        wallet (utils.wallet.Wallet): The wallet to be associated with the user.
    """
    sql = text("""
    INSERT INTO USERS (user_id, user_number, user_name, user_surname, ILP_wallet) 
    VALUES (:user_id, :user_number, :user_name, :user_surname, :ILP_wallet);
    
    INSERT INTO USER_WALLET (user_id, user_wallet, userbalance) 
    VALUES (:user_id, :user_wallet, :userbalance);
    """)

    try:
        with sqlite_conn.connect() as conn:

            conn.execute(sql, {
                'user_id': user.id_number,
                'user_number': user.cell_number,
                'user_name': user.name,
                'user_surname': user.surname,
                'ILP_wallet': user.wallet_id,
                'user_wallet': wallet.id,
                'userbalance': wallet.user_balance
            })
            conn.commit()

    except IntegrityError as ie:
        print(f"IntegrityError occurred: {ie}")
        raise

    except SQLAlchemyError as se:
        print(f"SQLAlchemyError occurred: {se}")
        raise

    except Exception as e:
        print(f"General Error occurred: {e}")
        raise