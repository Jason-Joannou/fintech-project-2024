# from .sql_connection import sql_connection
from sqlalchemy import text

from datetime import datetime

from .sqlite_connection import SQLiteConnection

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
        if result:
            return True

        return False


# Call the function update a user name. We have to create a lot more of these functions! 

def update_user_name(user_id, new_name):
    """
    Update the user_name of a user identified by user_id.
    """
    try:
        with sqlite_conn.connect() as conn:
            update_query = text("""
                UPDATE USERS
                SET user_name = :new_name, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id
            """)
            
            conn.execute(update_query, {'new_name': new_name, 'user_id': user_id})
            print(f"Success: user_name updated for user_id {user_id}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
update_user_name(1, 'John')


if __name__ == "__main__":
#    update_user_name(1, 'John')