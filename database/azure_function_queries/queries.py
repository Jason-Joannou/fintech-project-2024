from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection

db_conn = SQLiteConnection(database="./database/test_db.db")


def dynamic_read_operation(query: str, params: Dict) -> List[Dict]:
    """
    Executes a dynamic SQL query with provided parameters.

    Args:
        query (str): The SQL query to execute.
        params (Dict): A dictionary of parameters to bind to the query.

    Returns:
        List[Dict]: A list of dictionaries representing the rows.
    """
    try:
        with db_conn.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            # Convert each row to a dictionary using column names
            data = [dict(row._mapping) for row in rows]
            return data
    except SQLAlchemyError as e:
        print(f"An error occurred during database query execution: {e}")
        return []


def dynamic_write_operation(query: str, params: Dict) -> None:
    """
    Executes a dynamic SQL write operation with the provided parameters.

    This function executes a SQL query for operations like INSERT, UPDATE, or DELETE.
    It does not return any data.

    Args:
        query (str): The SQL query to execute. This should be a write operation such as
                     an INSERT, UPDATE, or DELETE statement.
        params (Dict): A dictionary of parameters to bind to the query, where the keys
                       correspond to parameter names in the SQL query.

    Raises:
        SQLAlchemyError: If an error occurs during the execution of the query, the
                         exception is caught and re-raised after logging the error.
    """
    try:
        with db_conn.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()
    except SQLAlchemyError as e:
        print(f"An error occurred during database query execution: {e}")
        conn.rollback()
        raise e
