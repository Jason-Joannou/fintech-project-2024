from typing import Dict, List, Optional

from database.user_queries.queries import (
    check_if_number_exists_sqlite,
    check_if_number_is_admin,
)
from whatsapp_utils._utils.state_config import MESSAGE_STATES
from whatsapp_utils.schemas.state_schema import StateSchema


class MessageStateManager:
    """
    docsting
    """

    # We handle registration outside, this is purely for state management
    def __init__(self, user_number: str) -> None:
        self.base_greetings = MESSAGE_STATES["base_state"]
        self.unrecognized_state = MESSAGE_STATES["unrecognized_state"]
        self.user_number = user_number
        self.registration_status = self.check_registration_status()
        self.is_admin = self.check_admin_status()
        self.current_state: StateSchema = {}
        self.previous_state: StateSchema = {}
        self.state_index = 0

    def check_registration_status(self):
        return check_if_number_exists_sqlite(from_number=self.user_number)

    def check_admin_status(self):
        return check_if_number_is_admin(from_number=self.user_number)

    def update_registration_status(self):
        if not self.registration_status:
            self.registration_status = self.check_registration_status()

    def processes_user_request(self, user_action: str):
        # Check if user is admin
        self.update_registration_status()
        if user_action in self.base_greetings and not self.registration_status:
            self.set_current_state(state=MESSAGE_STATES["unregistered_number"])
            self.set_previous_state()
            return self.get_current_state_message()
        elif user_action in self.base_greetings and self.registration_status:
            if self.is_admin:
                self.set_current_state(state=MESSAGE_STATES["registered_number_admin"])
                self.set_previous_state()
            else:
                self.set_current_state(state=MESSAGE_STATES["registered_number"])
                self.set_previous_state()
            return self.get_current_state_message()
        else:  # Handle other actions according to state

            # Check if action is valid for the current state
            if user_action not in self.get_current_state_valid_actions():
                return self.get_unrecognized_state_response()

            # Check if we need to transfer state
            # Back is also a transerable state
            if (
                self.get_current_state_state_selections() is not None
            ):  # We have to transfer state
                self.set_current_state(
                    MESSAGE_STATES[self.current_state.state_selection[user_action]]
                )

    def get_current_state_message(self):
        return self.current_state.message

    def set_current_state(self, state: StateSchema) -> None:
        self.current_state = state

    def set_previous_state(self):
        self.previous_state = self.current_state

    def get_unrecognized_state_response(self):
        if self.current_state:
            return self.unrecognized_state + self.get_current_state_message()
        else:
            return "Sorry, I don't understand. Please activate the service by sending 'Hi' or 'Hello'"

    def get_current_state_valid_actions(self) -> List[str]:
        return self.current_state.valid_actions

    def get_current_state_action_responses(self) -> Optional[Dict]:
        return self.current_state.action_responses

    def get_current_state_action_requests(self) -> Optional[Dict]:
        return self.current_state.action_responses

    def get_current_state_state_selections(self) -> Optional[Dict]:
        return self.current_state.state_selection
