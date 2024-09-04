from .sql_connection import sql_connection
from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./test_db.db")
sql_conn = sql_connection()

# URL refers to the openAPI address of the stokvel

def create_stokvel_table_sqlite():
    with sqlite_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS STOKVELS (
                id INTEGER PRIMARY KEY, 
                name TEXT UNIQUE,  -- Add UNIQUE constraint here
                url TEXT, 
                stokvel_type TEXT,
                min_contributing_amount INTEGER,
                max_number_of_contributors INTEGER,
                payout_day INTEGER,
                created_at TIMESTAMP, 
                updated_at TIMESTAMP
            );
        """)

def create_stokvel_table_sql_server():
    with sql_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS STOKVELS (
                id INTEGER PRIMARY KEY, 
                name TEXT UNIQUE,  -- Add UNIQUE constraint here
                url TEXT,
                stokvel_type TEXT,
                min_contributing_amount INTEGER,
                max_number_of_contributors INTEGER,
                payout_day INTEGER,
                created_at DATETIME, 
                updated_at DATETIME
            );
        """)

def create_user_table_sqlite():
    with sqlite_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                created_at TIMESTAMP, 
                updated_at TIMESTAMP
            );
        """)

def create_user_table_sql_server():
    with sql_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                created_at DATETIME, 
                updated_at DATETIME
            )
    """)

def create_transaction_table_sqlite():
    with sqlite_conn.connect() as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER, 
            stokvel_id INTEGER, 
            amount INTEGER, 
            created_at TIMESTAMP, 
            updated_at TIMESTAMP
        );
    """)

def create_transaction_table_sql_server():

    with sql_conn.connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER, 
            stokvel_id INTEGER, 
            amount INTEGER, 
            created_at DATETIME, 
            updated_at DATETIME
        );
    """)

def create_resource_table_sqlite():
    with sqlite_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS RESOURCES (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                url TEXT, 
                created_at TIMESTAMP, 
                updated_at TIMESTAMP
            );
        """)

def create_resource_table_sql_server():
    engine = sql_conn.get_engine()
    engine.execute(
        """
        CREATE TABLE IF NOT EXISTS RESOURCES (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            url TEXT, 
            created_at DATETIME, 
            updated_at DATETIME
        );
        """
    )
    with sql_conn.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS RESOURCES (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                url TEXT, 
                created_at DATETIME, 
                updated_at DATETIME
            );
        """)
