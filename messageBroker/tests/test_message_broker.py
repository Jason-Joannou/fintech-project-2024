import pytest
from src.message_broker import MessageBroker


@pytest.fixture
def broker():
    broker = MessageBroker()
    yield broker
    broker.close()

def test_publish_and_consume(broker):
    test_queue = 'test_queue'
    test_message = 'Hello, RabbitMQ!'

    def callback(ch, method, properties, body):
        assert body.decode() == test_message
        print(f"Received: {body.decode()}")

    broker.publish(test_queue, test_message)
    broker.consume_one(test_queue, callback)