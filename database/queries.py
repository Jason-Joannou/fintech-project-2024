from .sqlite_connection import SQLiteConnection
from .sql_connection import sql_connection
from sqlalchemy import text

sqlite_conn = SQLiteConnection(database="./database/test_db.db")
# sql_conn = sql_connection()

def check_if_number_exists_sqlite(from_number):

    query = f"SELECT * FROM USERS WHERE user_number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(text(query), {'from_number': from_number})
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
