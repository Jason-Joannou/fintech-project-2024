from sqlalchemy import text
from datetime import datetime
from sqlalchemy import exc, select, func
from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")

def drop_tables():
    """
    Drop all the tables in the database if they exist.
    """
    try:
        with sqlite_conn.connect() as conn:
            # Drop tables if they exist
            tables = [
                "USERS", "STOKVELS", "STOKVEL_MEMBERS", "TRANSACTIONS", "RESOURCES",
                "ADMIN", "CONTRIBUTIONS", "USER_WALLET", "STOKVEL_WALLET", "APPLICATIONS"
            ]
            
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
                print(f"Success: {table} table dropped.")
                
    except Exception as e:
        print(f"An error occurred while dropping tables: {e}")

# Run the drop tables function
drop_tables()
