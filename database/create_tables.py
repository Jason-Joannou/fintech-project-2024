from .sql_connection import sql_connection
from .sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./test_db.db")
sql_conn = sql_connection()

def create_stokvel_table_sqlite():
    engine = sqlite_conn.get_engine()
    engine.execute("""
        CREATE TABLE IF NOT EXISTS STOKVELS (
            id INTEGER PRIMARY KEY, 
            name TEXT UNIQUE,  -- Add UNIQUE constraint here
            url TEXT, 
            created_at TIMESTAMP, 
            updated_at TIMESTAMP
        );
    """)

def create_stokvel_table_sql_server():
    engine = sql_conn.get_engine()
    engine.execute("""
        CREATE TABLE IF NOT EXISTS STOKVELS (
            id INTEGER PRIMARY KEY, 
            name TEXT UNIQUE,  -- Add UNIQUE constraint here
            url TEXT, 
            created_at DATETIME, 
            updated_at DATETIME
        );
    """)
