from .sqlite_connection import SQLiteConnection
from .sql_connection import sql_connection

sqlite_conn = SQLiteConnection(database="./test_db.db")
sql_conn = sql_connection()

def check_if_number_exists_sqlite(from_number):

    query = f"SELECT * FROM numbers WHERE number = :from_number"
    with sqlite_conn.connect() as conn:
        cursor = conn.execute(query, {'from_number': from_number})
        result = cursor.fetchone()
        if result:
            return result
        else:
            return None
        
def check_if_number_exists_sql(from_number):

    query = f"SELECT * FROM numbers WHERE number = :from_number"
    with sql_conn.connect() as conn:
        cursor = conn.execute(query, {'from_number': from_number})
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
