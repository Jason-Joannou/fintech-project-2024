from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

db_conn = SQLiteConnection(database="./database/test_db.db")


def insert_new_user_state(from_number: str) -> None:
    """
    Insert new user state if no state is found.
    """
    engine = db_conn.get_engine()
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    INSERT INTO STATE_MANAGEMENT
    (user_number, current_state_tag, previous_state_tag, last_interaction)
    VALUES
    (:from_number, 'stateless', 'stateless', :datetime)
    """
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(
                text(query), {"from_number": from_number, "datetime": datetime.now()}
            )
            transaction.commit()
        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error inserting the state:", e)


def get_user_state(from_number: str) -> Tuple[str, str, str]:
    """
    Retrieve the current and previous state tags and last interaction timestamp.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    SELECT current_state_tag, previous_state_tag, last_interaction
    FROM STATE_MANAGEMENT
    WHERE user_number = :from_number
    """
    with db_conn.connect() as conn:
        result = conn.execute(text(query), {"from_number": from_number}).fetchone()

    current_state_tag, previous_state_tag, last_interaction = result
    return current_state_tag, previous_state_tag, last_interaction


def update_current_state(from_number: str, current_state_tag: str) -> None:
    """
    Update user state with new state tags and last interaction timestamp.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    UPDATE STATE_MANAGEMENT
    SET last_interaction = :datetime,
        current_state_tag = :current_state_tag
    WHERE user_number = :from_number
    """
    engine = db_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(
                text(query),
                {
                    "from_number": from_number,
                    "datetime": datetime.now(),
                    "current_state_tag": current_state_tag,
                },
            )
            transaction.commit()
        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error updating the state:", e)


def update_previous_state(from_number: str, previous_state_tag: str) -> None:
    """
    Update user state with new state tags and last interaction timestamp.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    UPDATE STATE_MANAGEMENT
    SET last_interaction = :datetime,
        previous_state_tag = :previous_state_tag
    WHERE user_number = :from_number
    """
    engine = db_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(
                text(query),
                {
                    "from_number": from_number,
                    "datetime": datetime.now(),
                    "previous_state_tag": previous_state_tag,
                },
            )
            transaction.commit()
        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error updating the state:", e)


def reset_state_if_inactive(from_number: str) -> None:
    """
    Reset user state to 'stateless' if the user has been inactive for more than an hour.
    """
    result = get_user_state(from_number=from_number)
    if result is not None:
        _, _, last_interaction = result
        inactive_duration = datetime.now() - datetime.strptime(
            last_interaction, "%Y-%m-%d %H:%M:%S.%f"
        )
        if inactive_duration > timedelta(hours=1):
            update_current_state(from_number=from_number, current_state_tag="stateless")
            update_previous_state(
                from_number=from_number, previous_state_tag="stateless"
            )


def check_if_user_has_state(from_number: str) -> bool:
    """
    Check if the user has an existing state in the database.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = "SELECT 1 FROM STATE_MANAGEMENT WHERE user_number = :from_number"
    with db_conn.connect() as conn:
        result = conn.execute(text(query), {"from_number": from_number}).fetchone()
    return result is not None


def get_state_responses(from_number: str) -> Tuple[str, str]:
    """
    Retrieve the current and previous state tags for the user, handling all database interactions in a single transaction.
    """
    engine = db_conn.get_engine()

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            if not check_if_user_has_state(from_number):
                insert_new_user_state(from_number)

            reset_state_if_inactive(from_number)

            current_state_tag, previous_state_tag, _ = get_user_state(from_number)
            transaction.commit()
            return current_state_tag, previous_state_tag

        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error getting the state responses:", e)
            return "stateless", "stateless"
