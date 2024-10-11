from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection

db_conn = SQLiteConnection(database="./database/test_db.db")


def dynamic_query(query: str, params: Dict) -> List[Dict]:
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
