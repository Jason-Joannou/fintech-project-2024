import sqlite3
from typing import List, Tuple

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")


def bulk_upload_transaction(table_rows: List[Tuple]):
    """
    This function takes in a list of tuples representing a table row,
    and then uploads it to the TRANSACTIONS table in the SQLite database.
    The row should contain the following columns in order: id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at
    If there is an operational error during the bulk upload, the function will print the error and rollback the changes
    """
    sql_query = """
                INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
                VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)
                """

    with sqlite_conn.connect() as conn:
        try:
            conn.execute(text(sql_query), table_rows)
            conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            conn.rollback()


def bulk_upload_interest_table(table_rows: List[Tuple]):

    sql_query = """
                INSERT INTO INTEREST (stokvel_id, date, interest_value)
                VALUES (:stokvel_id, :date, :interest_value)"""
    with sqlite_conn.connect() as conn:
        try:
            conn.execute(text(sql_query), table_rows)
            conn.commit()
        except Exception as e:
            print(f"Error in bulk upload for interest table: {e}")
            conn.rollback()
