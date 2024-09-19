from typing import Dict, Optional

from pydantic import BaseModel, Field


class StateSchema(BaseModel):
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
