from typing import Dict, List, Optional, Tuple

from database.state_manager.queries import (
    get_state_responses,
    update_current_state,
    update_previous_state,
)
from database.user_queries.queries import (
    check_if_number_exists_sqlite,
    check_if_number_is_admin,
)
from whatsapp_utils._utils.state_config import MESSAGE_STATES
from whatsapp_utils._utils.twilio_messenger import send_conversational_message
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
        self.current_state_tag, self.previous_state_tag = self.get_state_tags()
        self.current_state: StateSchema = (
            MESSAGE_STATES[self.current_state_tag]
            if self.current_state_tag != "stateless"
            else {}
        )
        self.previous_state: StateSchema = (
            MESSAGE_STATES[self.previous_state_tag]
            if self.previous_state_tag != "stateless"
            else {}
        )
        self.state_index = 0

    def check_registration_status(self) -> bool:
        return check_if_number_exists_sqlite(from_number=self.user_number)

    def check_admin_status(self) -> bool:
        return check_if_number_is_admin(from_number=self.user_number)

    def update_registration_status(self) -> None:
        if not self.registration_status:
            self.registration_status = self.check_registration_status()

    def processes_user_request(self, user_action: str) -> str:

        self.update_registration_status()
        # User is not registered
        if not self.registration_status:
            self.set_current_state(tag="unregistered_number")
            if user_action in self.base_greetings:
                return self.get_current_state_message()
            else:
                if user_action not in self.get_current_state_valid_actions():
                    return self.get_unrecognized_state_response()

                return MESSAGE_STATES["unregistered_number"]["action_responses"][
                    user_action
                ]

        # User is registered
        elif self.registration_status:
            if user_action in self.base_greetings:
                if self.check_admin_status():
                    self.set_current_state(tag="registered_number_admin")
                    self.set_previous_state()
                else:
                    self.set_current_state(tag="registered_number")
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
                        MESSAGE_STATES[
                            self.current_state["state_selection"][user_action]
                        ]
                    )

    def get_current_state_message(self):
        msg = self.current_state["message"]
        return send_conversational_message(msg)

    def _get_current_state_message_formatted(self):
        message = self.current_state["message"].split(":")[1]
        return message

    def set_current_state(self, tag: str) -> None:
        # Need to set current state in the db
        update_current_state(from_number=self.user_number, current_state_tag=tag)
        self.update_local_states()

    def set_previous_state(self):
        # Need to set previous state in the db
        update_previous_state(
            from_number=self.user_number, previous_state_tag=self.current_state_tag
        )
        self.update_local_states()

    def get_unrecognized_state_response(self):
        if self.current_state and self.previous_state:
            msg = self.unrecognized_state + self._get_current_state_message_formatted()
            return send_conversational_message(msg)
        else:
            msg = "Sorry, I don't understand. Please activate the service by sending 'Hi' or 'Hello'"
            return send_conversational_message(msg)

    def get_current_state_valid_actions(self) -> List[str]:
        return self.current_state["valid_actions"]

    def get_current_state_action_responses(self) -> Optional[Dict]:
        return self.current_state["action_responses"]

    def get_current_state_action_requests(self) -> Optional[Dict]:
        return self.current_state["action_requests"]

    def get_current_state_state_selections(self) -> Optional[Dict]:
        return self.current_state["state_selection"]

    def get_state_tags(self) -> Tuple:
        return get_state_responses(from_number=self.user_number)

    def return_twilio_formatted_message(self, msg: str) -> str:
        return send_conversational_message(msg)

    def update_local_states(self) -> None:
        self.current_state, self.previous_state = self.get_state_tags()
        self.current_state = (
            MESSAGE_STATES[self.current_state]
            if self.current_state != "stateless"
            else {}
        )
        self.previous_state = (
            MESSAGE_STATES[self.previous_state]
            if self.previous_state != "stateless"
            else {}
        )
