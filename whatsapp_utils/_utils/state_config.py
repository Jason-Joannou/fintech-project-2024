from whatsapp_utils._utils.message_config import (
    ADMIN_SERVICES,
    COMMUNITY_SERVICES,
    FINANCIAL_REPORTS,
    REGISTERED_NUMBER,
    REGISTERED_NUMBER_ADMIN,
    STOKVEL_SERVICES,
    UNREGISTERED_NUMBER,
)

# Need to add messages states as we go
MESSAGE_STATES = {
    "base_state": ["Hi", "Hello", "hi", "hello"],
    "unrecognized_state": "Sorry, I don't understand that action. The following actions are allowed in this state:\n",
    REGISTERED_NUMBER["tag"]: REGISTERED_NUMBER,
    REGISTERED_NUMBER["tag"]: REGISTERED_NUMBER_ADMIN,
    UNREGISTERED_NUMBER["tag"]: UNREGISTERED_NUMBER,
    ADMIN_SERVICES["tag"]: ADMIN_SERVICES,
    COMMUNITY_SERVICES["tag"]: COMMUNITY_SERVICES,
    FINANCIAL_REPORTS["tag"]: FINANCIAL_REPORTS,
    STOKVEL_SERVICES["tag"]: STOKVEL_SERVICES,
}
