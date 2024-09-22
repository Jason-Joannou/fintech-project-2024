from typing import Dict, Optional

from pydantic import BaseModel, Field


class StateSchema(BaseModel):
    """
    A schema representing the state of a user in the message system.

    This model defines various attributes of the user's state, such as
    the current tag, message, valid actions, and potential responses or requests
    based on user input.

    Attributes:
        tag (str): A label for the current state of the user, used to identify the state.
        message (str): A message that corresponds to the current state, typically displayed to the user.
        valid_actions (list[str]): A list of valid actions the user can take in the current state.
        state (int): A numeric value representing the current state of the user.
        action_responses (Optional[Dict]): A dictionary mapping user actions to predefined responses for those actions.
        action_requests (Optional[Dict]): A dictionary mapping user actions to API endpoints for dynamic requests.
        state_selection (Optional[Dict]): A dictionary mapping user actions to state transitions.
    """

    tag: str = Field(..., example="community_services")
    message: str = Field(..., example="Welcome to our community services!")
    valid_actions: list[str] = Field(..., example=["1", "2", "3"])
    state: int = Field(..., example=1)
    action_responses: Optional[Dict] = Field(
        None,
        example="Please register through our online portal: https://stokvels.com/register",
    )
    action_requests: Optional[Dict] = Field(
        None, examples={"1": "/stokvels/total_stokvels"}
    )
    state_selection: Optional[Dict] = Field(None, examples={"1": "community_services"})
