import pytest
from unittest.mock import patch, MagicMock
from src.message_config import GREET_MESSAGE_REGISTERED, GREET_MESSAGE_UNREGISTERED
from sqlalchemy import text

# Patch MessageBroker at the start before importing the modules that depend on it
mock_broker = MagicMock()
with patch('messageBroker.src.message_broker.MessageBroker', return_value=mock_broker):
    from src.twilio_client import TwilioClient
    from src.cache import Cache
    from database.sqlite_connection import SQLiteConnection
    from src.whatsapp_controller import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def twilio_client():
    return TwilioClient()

@pytest.fixture
def sqlite_database():
    return SQLiteConnection(database="./database/test_db.db")

@pytest.fixture
def sql_server():
    return SQLiteConnection(database="./database/test_db.db")

@pytest.fixture
def cache():
    return Cache()

@pytest.fixture
def mock_message_broker():
    return mock_broker

# Example of grerting test
    # When we have a registered user, we should expect the whatsapp endpoint to return the specified greeting message
    # This is what the below test checks
def test_greeting_action_call_registered(client, cache, mock_message_broker, sqlite_database):
    from_number = '+1234567890'
    action_message = 'hi'

    # Simulate user in the database
    with sqlite_database.connect() as conn:
        result = conn.execute(text("SELECT * FROM USERS WHERE user_number = :from_number"), {'from_number': from_number}).fetchone()
        assert len(result) == 5 # should be 5 columns ie 5 items
    cache.set(from_number, result[1])

    # Simulate sending a message to the endpoint
    response = client.post('/whatsapp', data={'From': from_number, 'Body': action_message})

    # Assert that the response contains the expected greeting message for registered users
    assert GREET_MESSAGE_REGISTERED["message"] in response.data.decode('utf-8')

def test_greeting_action_call_unregistered(client, cache, mock_message_broker, sqlite_database):
    from_number = '+1234567891'
    action_message = 'hi'

    # Simulate user in the database
    with sqlite_database.connect() as conn:
        result = conn.execute(text("SELECT * FROM USERS WHERE user_number = :from_number"), {'from_number': from_number}).fetchone()
        assert result is None  # Expect no user to be found

    # Simulate sending a message to the endpoint
    response = client.post('/whatsapp', data={'From': from_number, 'Body': action_message})

    # Assert that the response contains the expected greeting message for unregistered users
    assert GREET_MESSAGE_UNREGISTERED["message"] in response.data.decode('utf-8')

