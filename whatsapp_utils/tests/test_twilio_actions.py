from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import text
from _utils.message_config import GREET_MESSAGE_REGISTERED, GREET_MESSAGE_UNREGISTERED

# Patch MessageBroker at the start before importing the modules that depend on it
mock_broker = MagicMock()
with patch("messageBroker.src.message_broker.MessageBroker", return_value=mock_broker):
    from _utils.cache import Cache
    from _utils.twilio_client import TwilioClient
    from _utils.whatsapp_controller import app

    from database.sqlite_connection import SQLiteConnection


@pytest.fixture
def client():
    """
    docstring
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def twilio_client():
    """
    docstring
    """
    return TwilioClient()


@pytest.fixture
def sqlite_database():
    """
    docstring
    """
    return SQLiteConnection(database="./database/test_db.db")


@pytest.fixture
def sql_server():
    """
    docstring
    """
    return SQLiteConnection(database="./database/test_db.db")


@pytest.fixture
def cache():
    """
    docstring
    """
    return Cache()


@pytest.fixture
def mock_message_broker():
    """
    docstring
    """
    return mock_broker


# Example of grerting test
# When we have a registered user, we should expect the whatsapp endpoint to return the specified greeting message
# This is what the below test checks
def test_greeting_action_call_registered(
    client, cache, mock_message_broker, sqlite_database
):  # pylint: disable=unused-argument
    """
    docstring
    """
    from_number = "+1234567890"
    action_message = "hi"

    # Simulate user in the database
    with sqlite_database.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM USERS WHERE user_number = :from_number"),
            {"from_number": from_number},
        ).fetchone()
        assert len(result) == 5  # should be 5 columns ie 5 items
    cache.set(from_number, result[1])

    # Simulate sending a message to the endpoint
    response = client.post(
        "/whatsapp", data={"From": from_number, "Body": action_message}
    )

    # Assert that the response contains the expected greeting message for registered users
    assert GREET_MESSAGE_REGISTERED["message"] in response.data.decode("utf-8")


def test_greeting_action_call_unregistered(
    client, cache, mock_message_broker, sqlite_database
):  # pylint: disable=unused-argument
    """
    docstring
    """
    from_number = "+1234567891"
    action_message = "hi"

    # Simulate user in the database
    with sqlite_database.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM USERS WHERE user_number = :from_number"),
            {"from_number": from_number},
        ).fetchone()
        assert result is None  # Expect no user to be found

    # Simulate sending a message to the endpoint
    response = client.post(
        "/whatsapp", data={"From": from_number, "Body": action_message}
    )

    # Assert that the response contains the expected greeting message for unregistered users
    assert GREET_MESSAGE_UNREGISTERED["message"] in response.data.decode("utf-8")


# OTHER TESTS TO IMPLEMENT
# What is the expected message when a users sends something other than hi ( registered and unregistered users )
# When they select a specific action
