from typing import Dict, List, Union

from whatsapp_utils._utils.message_config import (
    ADMIN_SERVICES,
    COMMUNITY_SERVICES,
    FINANCIAL_REPORTS,
    REGISTERED_NUMBER,
    REGISTERED_NUMBER_ADMIN,
    STOKVEL_SERVICES,
    UNREGISTERED_NUMBER,
)
from whatsapp_utils.schemas.state_schema import StateSchema

# Need to add messages states as we go
MESSAGE_STATES: Dict[str, Union[StateSchema, List[str], str]] = {
    "base_state": ["Hi", "Hello", "hi", "hello"],
    "unrecognized_state": "Sorry, I don't understand that action. The following actions are allowed in this state:\n",
    REGISTERED_NUMBER["tag"]: StateSchema(**REGISTERED_NUMBER),
    REGISTERED_NUMBER_ADMIN["tag"]: StateSchema(**REGISTERED_NUMBER_ADMIN),
    UNREGISTERED_NUMBER["tag"]: StateSchema(**UNREGISTERED_NUMBER),
    ADMIN_SERVICES["tag"]: StateSchema(**ADMIN_SERVICES),
    COMMUNITY_SERVICES["tag"]: StateSchema(**COMMUNITY_SERVICES),
    FINANCIAL_REPORTS["tag"]: StateSchema(**FINANCIAL_REPORTS),
    STOKVEL_SERVICES["tag"]: StateSchema(**STOKVEL_SERVICES),
}
