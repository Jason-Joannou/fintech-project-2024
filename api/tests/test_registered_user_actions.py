import pytest
from flask import Flask

from api.routes.whatsapp_controller import whatsapp_bp
from whatsapp_utils._utils.message_config import GREET_MESSAGE_REGISTERED


# Create a test app
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(whatsapp_bp)
    app.config["TESTING"] = True
    client = app.test_client()
    yield client


@pytest.fixture
def registered_user():
    registered_number = "+1234567890"
    return registered_number


@pytest.fixture
def unregistered_user():
    unregistered_number = "+1234567891"
    return unregistered_number


# Test case: Registered user sends "hi"
def test_whatsapp_registered_user_hi(client, registered_user):
    # Simulate sending 'hi' from a registered number
    data = {"Body": "hi", "From": registered_user}
    response = client.post("/whatsapp", data=data)

    # Check if the correct message is sent for a registered user
    assert response.status_code == 200
    assert GREET_MESSAGE_REGISTERED["message"] in response.data.decode(
        "utf-8"
    )  # Replace with your actual registered user greeting


def test_whatsapp_registered_user_hello(client, registered_user):
    # Simulate sending 'hello' from a registered number
    data = {"Body": "hello", "From": registered_user}
    response = client.post("/whatsapp", data=data)

    # Check if the correct message is sent for a registered user
    assert response.status_code == 200
    assert GREET_MESSAGE_REGISTERED["message"] in response.data.decode(
        "utf-8"
    )  # Replace with your actual registered user greeting


# What happens if User sends invalid message
# What actions do we take if we receive the join stokvel action
# What actions do we take if a user wants to create a stokvel
# etc
