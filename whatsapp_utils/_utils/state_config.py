from whatsapp_utils._utils.message_config import (
    ADMIN_SERVICES,
    LEAVE_STOKVEL,
    MY_PROFILE,
    MY_STOKVELS,
    REGISTERED_NUMBER,
    STOKVEL_ACTIONS_ADMIN,
    STOKVEL_ACTIONS_USER,
    STOKVEL_ADMIN_SERVICES,
    STOKVEL_SERVICES,
    UNREGISTERED_NUMBER,
    UPDATE_PROFILE,
    VIEW_PROFILE,
)

# Need to add messages states as we go
MESSAGE_STATES = {
    "base_state": ["Hi", "Hello", "hi", "hello"],
    "unrecognized_state": "Sorry, I don't understand that action. The following actions are allowed in this state:\n",
    REGISTERED_NUMBER["tag"]: REGISTERED_NUMBER,
    ADMIN_SERVICES["tag"]: ADMIN_SERVICES,
    STOKVEL_SERVICES["tag"]: STOKVEL_SERVICES,
    STOKVEL_ACTIONS_ADMIN["tag"]: STOKVEL_ACTIONS_ADMIN,
    STOKVEL_ACTIONS_USER["tag"]: STOKVEL_ACTIONS_USER,
    LEAVE_STOKVEL["tag"]: LEAVE_STOKVEL,
    STOKVEL_ADMIN_SERVICES["tag"]: STOKVEL_ADMIN_SERVICES,
    MY_PROFILE["tag"]: MY_PROFILE,
    MY_STOKVELS["tag"]: MY_STOKVELS,
    VIEW_PROFILE["tag"]: VIEW_PROFILE,
    UPDATE_PROFILE["tag"]: UPDATE_PROFILE,
    UNREGISTERED_NUMBER["tag"]: UNREGISTERED_NUMBER,
}
