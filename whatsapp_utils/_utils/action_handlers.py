from .state_manager import StateManager
from .twilio_client import TwilioClient

twilio_client = TwilioClient()
state_manager = StateManager()


def handle_action(from_number, action):
    """
    docstring
    """
    state = state_manager.get_state(from_number)
    if action == "1" and not state:
        state_manager.set_state(from_number, {"action": "join_stokvel", "step": 1})
        # Need to get a list of all available stockvels
    elif action == "2":
        pass
    else:
        pass
