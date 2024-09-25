import json
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.sqlite_connection import SQLiteConnection
from database.utils import extract_whatsapp_number

db_conn = SQLiteConnection(database="./database/test_db.db")


def pop_previous_state(from_number: str) -> None:
    """
    Pops the current state from the stack and returns the previous state tag or None if the stack is empty.

    Parameters:
    from_number (str): The user's phone number.

    Returns:
    str: The new current state after popping, or None if the stack is empty.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    stack_query = (
        "SELECT stack_state FROM STATE_MANAGEMENT WHERE user_number = :from_number"
    )
    update_query = """
    UPDATE STATE_MANAGEMENT
    SET stack_state = :stack_state
    WHERE user_number = :from_number
    """
    engine = db_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:

            result = conn.execute(
                text(stack_query), {"from_number": from_number}
            ).fetchone()
            stack_state = json.loads(result[0]) if result and result[0] else []

            if len(stack_state) > 1:
                # Pop the current state (top of the stack)
                stack_state.pop()
                # Set the new current state to the new top of the stack
                conn.execute(
                    text(update_query),
                    {
                        "from_number": from_number,
                        "stack_state": json.dumps(stack_state),
                    },
                )
                transaction.commit()
            else:
                # If there's only one state or none, we can't pop further
                print("State stack is empty or has only one state.")
        except SQLAlchemyError as e:
            print("There was an error popping the previous state:", e)


def insert_new_user_state(from_number: str) -> None:
    """
    Insert new user state if no state is found.
    """
    engine = db_conn.get_engine()
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    INSERT INTO STATE_MANAGEMENT
    (user_number, last_interaction, stack_state)
    VALUES
    (:from_number, :datetime, :stack_state)
    """
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(
                text(query),
                {
                    "from_number": from_number,
                    "datetime": datetime.now(),
                    "stack_state": json.dumps([]),
                },
            )
            transaction.commit()
        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error inserting the state:", e)


def get_user_state(from_number: str) -> Tuple[List[str], str]:
    """
    Retrieve the current and previous state tags and last interaction timestamp.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    SELECT stack_state, last_interaction
    FROM STATE_MANAGEMENT
    WHERE user_number = :from_number
    """
    with db_conn.connect() as conn:
        result = conn.execute(text(query), {"from_number": from_number}).fetchone()

    stack_state, last_interaction = (json.loads(result[0])), (result[1])
    return stack_state, last_interaction


def update_current_state(from_number: str, current_state_tag: Optional[str]) -> None:
    """
    Update user state with new state tags and last interaction timestamp.
    """

    from_number = extract_whatsapp_number(from_number=from_number)
    query = """
    UPDATE STATE_MANAGEMENT
    SET last_interaction = :datetime,
    stack_state = :stack_state
    WHERE user_number = :from_number
    """
    stack_query = (
        "SELECT stack_state FROM STATE_MANAGEMENT WHERE user_number = :from_number"
    )
    engine = db_conn.get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            if current_state_tag is not None:
                result = conn.execute(
                    text(stack_query), {"from_number": from_number}
                ).fetchone()
                stack_state = json.loads(result[0]) if result and result[0] else []
                stack_state.append(current_state_tag)
            else:
                stack_state = []

            conn.execute(
                text(query),
                {
                    "from_number": from_number,
                    "datetime": datetime.now(),
                    "stack_state": json.dumps(stack_state),
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
        _, last_interaction = result
        inactive_duration = datetime.now() - datetime.strptime(
            last_interaction, "%Y-%m-%d %H:%M:%S.%f"
        )
        if inactive_duration > timedelta(hours=1):
            update_current_state(from_number=from_number, current_state_tag=None)


def check_if_user_has_state(from_number: str) -> bool:
    """
    Check if the user has an existing state in the database.
    """
    from_number = extract_whatsapp_number(from_number=from_number)
    query = "SELECT 1 FROM STATE_MANAGEMENT WHERE user_number = :from_number"
    with db_conn.connect() as conn:
        result = conn.execute(text(query), {"from_number": from_number}).fetchone()
    return result is not None


def get_state_responses(from_number: str) -> Optional[str]:
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

            stack_state, _ = get_user_state(from_number)
            current_state_tag = stack_state[-1] if stack_state else None
            transaction.commit()

        except SQLAlchemyError as e:
            transaction.rollback()
            print("There was an error getting the state responses:", e)
            current_state_tag = None

    return current_state_tag
