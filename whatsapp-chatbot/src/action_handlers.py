from messageBroker.src.message_broker import MessageBroker
from .twilio_client import TwilioClient
from .state_manager import StateManager


twilio_client = TwilioClient()
message_broker = MessageBroker()
state_manager = StateManager()

def handle_action(from_number, action):
    state = state_manager.get_state(from_number)
    if action == "1" and not state:
        state_manager.set_state(from_number, {'action': 'join_stokvel', 'step': 1})
        # Need to get a list of all available stockvels
        message_broker.publish(queue_name="action_queue", message=f"{from_number}:join_stokvel")
    elif action == "2":
        message_broker.publish(queue_name="action_queue", message=f"{from_number}:leave_stokvel")
    else:
        twilio_client.send_mesage(to=from_number, body="Invalid action. Please try again.")

def process_action(ch, method, properties, body):
    # This will be our callback method in the borker queue
    message = body.decode()
    from_number, action = message.split(':')

    pass