# from .sql_connection import sql_connection
from sqlalchemy import text

from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()

# URL refers to the openAPI address of the stokvel


def create_stokvel_members_table_sqlite():
    """
    docstring
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS STOKVEL_MEMBERS (
                id INTEGER PRIMARY KEY,
                stokvel_id INTEGER,
                stokvel_name TEXT,
                user_id INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """
            )
        )


def create_stokvel_table_sqlite():
    """
    docstring
    """

    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS STOKVELS (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,  -- Add UNIQUE constraint here
                stokvel_wallet TEXT,
                stokvel_type TEXT,
                min_contributing_amount INTEGER,
                max_number_of_contributors INTEGER,
                payout_day INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """
            )
        )


def create_user_table_sqlite():
    """
    docstring
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS USERS (
                user_id INTEGER PRIMARY KEY,
                user_number TEXT,
                wallet_address TEXT,
                created_at TIMESTAMP, 
                updated_at TIMESTAMP
            );
        """
            )
        )


def create_transaction_table_sqlite():
    """
    docstring
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS TRANSACTIONS (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                stokvel_id INTEGER,
                stokvel_name TEXT,
                stokvel_type TEXT,
                amount INTEGER,
                created_at TIMESTAMP, 
                updated_at TIMESTAMP
        );
    """
            )
        )


def create_resource_table_sqlite():
    """
    docstring
    """
    with sqlite_conn.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS RESOURCES (
                id INTEGER PRIMARY KEY,
                name TEXT,
                url TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """
            )
        )


if __name__ == "__main__":
    create_user_table_sqlite()
