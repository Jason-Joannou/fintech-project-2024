from flask import Flask, request
from messageBroker.pythonBroker.src.message_broker import MessageBroker
from action_handlers import handle_action
from twilio.twiml.messaging_response import MessagingResponse
from database.queries import check_if_number_exists_sql, check_if_number_exists_sqlite
from message_config import GREET_MESSAGE_REGISTERED, GREET_MESSAGE_UNREGISTERED
from .cache import Cache

app = Flask(__name__)
cache = Cache()

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    from_number = request.values.get('From', '')
    twiml = MessagingResponse()

    user = cache.get(from_number)
    if user is None:
        user = check_if_number_exists_sqlite(from_number=from_number)
        if user is not None:
            cache.set(from_number, user)
    
    if user is not None:
        if incoming_msg in ['hi', 'hello']:
            twiml.message(GREET_MESSAGE_REGISTERED["message"])
        else:
            handle_action(from_number=from_number, action=incoming_msg)

    else:
        if incoming_msg in ['hi', 'hello']:
            twiml.message(GREET_MESSAGE_UNREGISTERED["message"])
        else:
            print("Invalid message, please activate the service by sending 'Hi' or 'Hello'")
