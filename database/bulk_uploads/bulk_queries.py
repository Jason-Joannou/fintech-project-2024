import sqlite3
from typing import List, Tuple

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection

sqlite_conn = SQLiteConnection(database="./database/test_db.db")


def bulk_upload_transaction(table_rows: List[Tuple]):

    sql_query = """
                INSERT INTO TRANSACTIONS (id, user_id, stokvel_id, amount, tx_type, tx_date, created_at, updated_at)
                VALUES (:id, :user_id, :stokvel_id, :amount, :tx_type, :tx_date, :created_at, :updated_at)
                """

    with sqlite_conn.connect() as conn:
        try:
            conn.executemany(text(sql_query), table_rows)
            conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            conn.rollback()
