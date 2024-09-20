from datetime import datetime, timedelta

from sqlalchemy import text

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

db_conn = SQLiteConnection(database="./database/test_db.db")


def insert_new_user_state(from_number: str) -> None:
    """
    docstring
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = "INSERT INTO STATE_MANAGEMENT (user_number, current_state_tag, previous_state_tag, last_interaction) VALUES (:from_number, 'stateless', 'stateless', :datetime)"
    with db_conn.connect() as conn:
        conn.execute(
            text(query), {"from_number": from_number, "datetime": datetime.now()}
        )


def get_user_state(from_number: str) -> str:
    """
    docstring
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = "SELECT current_state_tag, previous_state_tag, last_interaction FROM STATE_MANAGEMENT WHERE user_number = :from_number"
    with db_conn.connect() as conn:
        cursor = conn.execute(text(query), {"from_number": from_number})
        result = cursor.fetchone()

    current_state_tag, previous_state_tag, last_interaction = result
    return current_state_tag, previous_state_tag, last_interaction


def update_user_state(
    from_number: str, current_state_tag: str, previous_state_tag: str
) -> None:
    """
    docstring
    """

    from_number = extract_whatsapp_number(from_number=from_number)
    query = "UPDATE STATE_MANAGEMENT SET last_interaction = :datetime, current_state_tag = :current_state_tag, previous_state_tag = :previous_state_tag WHERE user_number = :from_number"
    with db_conn.connect() as conn:
        conn.execute(
            text(query),
            {
                "from_number": from_number,
                "datetime": datetime.now(),
                "current_state_tag": current_state_tag,
                "previous_state_tag": previous_state_tag,
            },
        )


def reset_state_if_inactive(from_number: str) -> None:
    """
    docstring
    """
    _, _, last_interaction = get_user_state(from_number=from_number)
    inactive_duration = datetime.now() - datetime.strptime(
        last_interaction, "%Y-%m-%d %H:%M:%S.%f"
    )
    if inactive_duration > timedelta(hours=1):
        update_user_state(
            from_number=from_number,
            current_state_tag="stateless",
            previous_state_tag="stateless",
        )
