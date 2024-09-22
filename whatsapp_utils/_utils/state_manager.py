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
from whatsapp_utils._utils.api_requests import query_endpoint
from whatsapp_utils._utils.state_config import MESSAGE_STATES
from whatsapp_utils._utils.twilio_messenger import send_conversational_message
from whatsapp_utils.schemas.state_schema import StateSchema


class MessageStateManager:
    """
    Manages the state of user interactions via WhatsApp messages, allowing for
    state-based conversational responses and actions. Handles user registration,
    admin status, and message routing based on the current and previous states.

    Attributes:
    user_number (str): The phone number of the user interacting with the system.
    registration_status (bool): Indicates if the user is registered.
    is_admin (bool): Indicates if the user has admin privileges.
    current_state_tag (str): The current state of the user interaction.
    previous_state_tag (str): The previous state of the user interaction.
    current_state (StateSchema): The schema defining the current state's behavior.
    previous_state (StateSchema): The schema defining the previous state's behavior.
    state_index (int): Index for managing state transitions.
    """

    # We handle registration outside, this is purely for state management
    def __init__(self, user_number: str) -> None:
        """
        Initializes the state manager with the user's phone number and retrieves
        the user's registration status, admin status, and current and previous
        states from the database.

        Parameters:
        user_number (str): The phone number of the user interacting with the system.
        """
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
        """
        Checks if the user's phone number is registered in the database.

        Returns:
        bool: True if the user is registered, False otherwise.
        """
        return check_if_number_exists_sqlite(from_number=self.user_number)

    def check_admin_status(self) -> bool:
        """
        Checks if the user's phone number belongs to an admin.

        Returns:
        bool: True if the user is an admin, False otherwise.
        """
        return check_if_number_is_admin(from_number=self.user_number)

    def update_registration_status(self) -> None:
        """
        Updates the user's registration status by checking the database again.
        If the status has changed, the internal registration_status attribute
        is updated.
        """
        if not self.registration_status:
            self.registration_status = self.check_registration_status()

    def processes_user_request(self, user_action: str) -> str:
        """
        Processes the user's action based on their current state and registration status.
        Handles transitions between states, returns appropriate responses, and
        triggers any associated actions.

        Parameters:
        user_action (str): The action or message sent by the user.

        Returns:
        str: The response message based on the user's current state and action.
        """

        self.update_registration_status()
        # User is not registered
        if not self.registration_status:
            self.set_current_state(tag="unregistered_number")
            if user_action in self.base_greetings:
                return self.get_current_state_message()
            else:
                if user_action not in self.get_current_state_valid_actions():
                    return self.get_unrecognized_state_response()

                # Do action response method
                return self.return_twilio_formatted_message(
                    msg=MESSAGE_STATES["unregistered_number"]["action_responses"][
                        user_action
                    ]
                )

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

                    # Check if selection is a back state selection
                    if user_action in self.current_state["state_selection"].keys():
                        if (
                            self.current_state["state_selection"][user_action]
                            == "back_state"
                        ):
                            self.set_current_state(tag=self.previous_state["tag"])
                            self.set_previous_state()
                            return self.get_current_state_message()

                        self.set_previous_state()
                        self.set_current_state(
                            tag=self.current_state["state_selection"][user_action]
                        )
                        return self.get_current_state_message()

                # If not transferable state check if it is an action response

                if self.get_current_state_action_responses() is not None:
                    action_responses = self.get_current_state_action_responses().keys()
                    if user_action in action_responses:
                        msg = self.get_current_state_action_responses()[user_action]
                        return self.return_twilio_formatted_message(msg=msg)

                # If not action reponse, check if action request

                if self.get_current_state_action_requests() is not None:
                    action_requests = self.get_current_state_action_requests().keys()
                    if user_action in action_requests:
                        endpoint = self.get_current_state_action_requests()[user_action]
                        msg = self.execute_action_request(endpoint=endpoint)
                        return self.return_twilio_formatted_message(msg=msg)

    def execute_action_request(
        self, endpoint: str, payload: Optional[Dict] = None
    ) -> str:
        """
        Executes an external action request to a specified endpoint and returns the response.

        Parameters:
        endpoint (str): The API endpoint suffix to send the request to.
        payload (Optional[Dict]): Optional payload for the request.

        Returns:
        str: The response message from the API request.
        """
        msg = query_endpoint(endpoint_suffix=endpoint, payload=payload)
        return msg

    def get_current_state_message(self):
        """
        Retrieves the message associated with the current state and formats it
        for Twilio.

        Returns:
        str: The formatted message for the current state.
        """
        msg = self.current_state["message"]
        return send_conversational_message(msg)

    def _get_current_state_message_formatted(self):
        """
        Extracts and formats the message from the current state's schema.

        Returns:
        str: The formatted message for display.
        """
        message = self.current_state["message"].split(":")[1]
        return message

    def set_current_state(self, tag: str) -> None:
        """
        Sets the current state of the user interaction in the database and
        updates the local state attributes.

        Parameters:
        tag (str): The tag representing the new current state.
        """
        # Need to set current state in the db
        update_current_state(from_number=self.user_number, current_state_tag=tag)
        self.update_local_states()

    def set_previous_state(self):
        """
        Sets the previous state of the user interaction in the database and
        updates the local state attributes.
        """
        # Need to set previous state in the db
        update_previous_state(
            from_number=self.user_number, previous_state_tag=self.current_state_tag
        )
        self.update_local_states()

    def get_unrecognized_state_response(self):
        """
        Returns the response for an unrecognized action, either from the current
        state or a default message.

        Returns:
        str: The formatted unrecognized state message.
        """
        if self.current_state and self.previous_state:
            msg = self.unrecognized_state + self._get_current_state_message_formatted()
            return send_conversational_message(msg)
        else:
            msg = "Sorry, I don't understand. Please activate the service by sending 'Hi' or 'Hello'"
            return send_conversational_message(msg)

    def get_current_state_valid_actions(self) -> List[str]:
        """
        Retrieves the valid actions for the current state.

        Returns:
        List[str]: A list of valid actions for the current state.
        """
        return self.current_state.get("valid_actions", [])

    def get_current_state_action_responses(self) -> Optional[Dict]:
        """
        Retrieves the action responses for the current state.

        Returns:
        Optional[Dict]: A dictionary mapping actions to responses for the current state.
        """
        return self.current_state.get("action_responses", {})

    def get_current_state_action_requests(self) -> Optional[Dict]:
        """
        Retrieves the action requests for the current state, which may trigger
        external API calls.

        Returns:
        Optional[Dict]: A dictionary mapping actions to API endpoints for the current state.
        """
        return self.current_state.get("action_requests", {})

    def get_current_state_state_selections(self) -> Optional[Dict]:
        """
        Retrieves the state selections for the current state, allowing the user
        to transition between different states.

        Returns:
        Optional[Dict]: A dictionary mapping user actions to new state tags.
        """
        return self.current_state.get("state_selection", {})

    def get_state_tags(self) -> Tuple:
        """
        Retrieves the current and previous state tags from the database.

        Returns:
        Tuple: A tuple containing the current state tag and the previous state tag.
        """
        return get_state_responses(from_number=self.user_number)

    def return_twilio_formatted_message(self, msg: str) -> str:
        """
        Formats a given message using Twilio's conversational messaging format.

        Parameters:
        msg (str): The message to format.

        Returns:
        str: The formatted message for Twilio.
        """
        return send_conversational_message(msg)

    def update_local_states(self) -> None:
        """
        Updates the local current and previous state attributes by retrieving
        the state tags from the database.
        """
        self.current_state_tag, self.previous_state_tag = self.get_state_tags()
        self.current_state = (
            MESSAGE_STATES[self.current_state_tag]
            if self.current_state_tag != "stateless"
            else {}
        )
        self.previous_state = (
            MESSAGE_STATES[self.previous_state_tag]
            if self.previous_state_tag != "stateless"
            else {}
        )
