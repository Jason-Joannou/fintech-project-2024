import json
from typing import Dict, List, Optional, Tuple, Union, cast

from database.state_manager.queries import (
    check_if_unregistered_state_exists,
    get_current_stokvel_selection,
    get_state_responses,
    pop_previous_state,
    set_current_stokvel_selection,
    update_current_state,
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
        self.current_state_tag: Optional[str] = None
        self.current_state: Union[Dict, StateSchema] = {}
        self.update_local_states()

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

    def update_registration_status(self):
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
            if user_action in self.base_greetings:
                self.set_current_state(tag="unregistered_number")
                return self.get_current_state_message()

            if user_action not in self.get_current_state_valid_actions():
                return self.get_unrecognized_state_response()

            # Do action response method
            return self.return_twilio_formatted_message(
                msg=MESSAGE_STATES["unregistered_number"]["action_responses"][
                    user_action
                ]
            )

        # User is registered

        # Unrecognized state will remain in the state manager when a user registers for the first time
        # But will not be part of the state when the user interacts after some time
        check_if_unregistered_state_exists(from_number=self.user_number)
        self.update_local_states()
        if user_action in self.base_greetings:
            self.set_current_state(tag="registered_number")
            return self.get_current_state_message()

        if (
            self.current_state_tag is None
            and user_action not in self.get_current_state_valid_actions()
        ):
            return self.get_unrecognized_state_response()
        # Check if action is valid for the current state
        if (
            self.current_state_tag is not None
            and "input_request" not in self.current_state_tag
            and user_action not in self.get_current_state_valid_actions()
        ):
            return self.get_unrecognized_state_response()

        # Validation for input state
        if (
            isinstance(self.current_state_tag, str)
            and "input_request" in self.current_state_tag
        ):
            flag, user_input = self.handle_input_state_validation(
                user_input=user_action
            )
            if not flag:
                # If false we want execution to stop, if true we want execution to carry on
                msg = self.current_state["invalid_message"]
                self.set_previous_state()  # Need to move back to state before
                return self.return_twilio_formatted_message(msg=msg)

        # Check if we need to transfer state
        # Back is also a transerable state
        if self.get_current_state_state_selections():  # We have to transfer state

            # Check if selection is a back state selection
            if user_action in self.current_state["state_selection"].keys():
                if self.current_state["state_selection"][user_action] == "back_state":
                    self.set_previous_state()
                    return self.get_current_state_message()

                if self.get_current_stokvels_in_state():
                    stokvels = self.get_current_stokvels_in_state()
                    stokvel_selection = stokvels[int(user_action) - 1]
                    self.set_current_stokvels_in_state(
                        stokvel_selection=stokvel_selection
                    )

                self.set_current_state(
                    tag=self.current_state["state_selection"][user_action]
                )
                return self.get_current_state_message()

        # If not transferable state check if it is an action response

        if self.get_current_state_action_responses():
            action_responses = self.get_current_state_action_responses()
            if user_action in list(action_responses.keys()):
                msg = action_responses[user_action]
                return self.return_twilio_formatted_message(msg=msg)

        # If not action reponse, check if action request
        if self.get_current_state_action_requests():
            action_requests = self.get_current_state_action_requests()
            if user_action in list(action_requests.keys()):
                # Need to check if the action request has an input_state
                input_action_states = self.get_current_state_input_action_states()
                if user_action in list(input_action_states.keys()):
                    input_action_states = input_action_states[user_action]
                    self.set_current_state(tag=input_action_states["tag"])
                    msg = input_action_states["message"]
                    return self.return_twilio_formatted_message(msg=msg)

                # Need to check for dynamic state
                if action_requests[user_action] == "/stokvel/my_stokvels":

                    self.set_current_state(tag="my_stokvels")
                    return self.get_current_state_message()

                endpoint = action_requests[user_action]
                msg = self.execute_action_request(
                    endpoint=endpoint,
                    payload={
                        "user_number": self.user_number,
                        "stokvel_selection": self.get_current_stokvel_selection(),
                    },
                )
                return self.return_twilio_formatted_message(msg=msg)

        if (
            isinstance(self.current_state_tag, str)
            and "input_request" in self.current_state_tag
        ):
            endpoint_action = self.current_state["action"]
            self.set_previous_state()
            action_requests = self.get_current_state_action_requests()
            endpoint = action_requests[endpoint_action]
            msg = self.execute_action_request(
                endpoint=endpoint,
                payload={
                    "user_input": user_input,
                    "user_number": self.user_number,
                    "stokvel_selection": self.get_current_stokvel_selection(),
                },
            )
            return self.return_twilio_formatted_message(msg=msg)

    def execute_action_request(
        self, endpoint: str, payload: Optional[Dict] = None
    ) -> Union[str, Dict]:
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

    def get_current_stokvels_in_state(self):
        """
        Retrieves the current stokvels in the dynamic state.

        Returns:
        list: The list of current stokvels.
        """

        return self.current_state.get("current_stokvels", [])

    def get_current_stokvel_selection(self):
        """
        Retrieves the current stokvel selection from the DB.

        Returns:
        str: The current stokvel selection.
        """

        return get_current_stokvel_selection(from_number=self.user_number)

    def set_current_stokvels_in_state(self, stokvel_selection: str):
        """
        Sets the current stokvels in the dynamic state.

        Parameters:
        stokvel_selection (str): The list of current stokvels.
        """
        set_current_stokvel_selection(
            from_number=self.user_number, stokvel_selection=stokvel_selection
        )

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
        Pops the previous state from the stack and sets it as the current state.
        """
        pop_previous_state(from_number=self.user_number)
        self.update_local_states()

    def get_unrecognized_state_response(self):
        """
        Returns the response for an unrecognized action, either from the current
        state or a default message.

        Returns:
        str: The formatted unrecognized state message.
        """
        if self.current_state:
            msg = self.unrecognized_state + self._get_current_state_message_formatted()
            return send_conversational_message(msg)

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

    def get_current_state_input_action_states(self) -> Optional[Dict]:
        """
        Retrieves the input action states for the current state.

        Returns:
        Optional[Dict]: A dictionary mapping actions to input states for the current state.
        """
        return self.current_state.get("input_request_states", {})

    def get_current_state_state_selections(self) -> Optional[Dict]:
        """
        Retrieves the state selections for the current state, allowing the user
        to transition between different states.

        Returns:
        Optional[Dict]: A dictionary mapping user actions to new state tags.
        """
        return self.current_state.get("state_selection", {})

    def get_state_tags(self) -> Optional[str]:
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
        the state tags from the database and navigating to the most nested sub-state.
        """
        self.current_state_tag = self.get_state_tags()

        # Need to account for dynamic state - Dynamic state will be set within the state manager
        if self.current_state_tag != "my_stokvels":
            # Initialize to an empty dictionary in case no state is found
            retrieved_state = {}  # type: ignore

            if self.current_state_tag is not None and ":" in self.current_state_tag:
                sub_state_split = self.current_state_tag.split(":")
                inital_state = MESSAGE_STATES  # Start with the base state dictionary

                # Traverse through each sub-state to reach the most nested one
                for state_tag in sub_state_split:
                    retrieved_state = inital_state.get(state_tag, {})  # type: ignore
                    if not retrieved_state:
                        break  # Exit if a sub-state doesn't exist
                    inital_state = retrieved_state  # Move deeper into the state
            else:
                # Handle the case where there are no sub-states
                retrieved_state = MESSAGE_STATES.get(self.current_state_tag, {})  # type: ignore

            # Set the current state based on whether the retrieval was successful
            self.current_state = (
                cast(StateSchema, retrieved_state) if retrieved_state else {}
            )
        else:
            retrieved_state = self.execute_action_request(  # type: ignore
                endpoint="/stokvel/my_stokvels",
                payload={"user_number": self.user_number},
            )
            self.current_state = json.loads(retrieved_state) if retrieved_state else {}  # type: ignore

    def handle_input_state_validation(
        self, user_input: str
    ) -> Tuple[bool, Union[Optional[float], Optional[int], Optional[str]]]:
        """
        Validates the user input based on the current state's valid_type.

        Args:
            user_input (str): The input provided by the user.

        Returns:
            Tuple[bool, Union[Optional[float], Optional[int], Optional[str]]]:
            A tuple where the first element is a boolean indicating if the input is valid,
            and the second element is the validated input converted to the appropriate type,
            or None if the validation fails.
        """
        valid_type = self.current_state.get("valid_type")
        try:
            if valid_type == float:
                converted_input = float(user_input)
            elif valid_type == int:
                converted_input = int(user_input)
            elif valid_type == str:
                converted_input = str(user_input)  # type: ignore
            else:
                raise ValueError("Unsupported input type.")
            return True, converted_input
        except ValueError:
            return False, None
