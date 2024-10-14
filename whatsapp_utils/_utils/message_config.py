UNREGISTERED_NUMBER = {
    "tag": "unregistered_number",
    "message": """
    Hi there! We noticed this number is not registered with us. Registering your number is needed to start contributing to Stokvels.
    Please select one of the following options to proceed:
    1. Register using Rafiki money
    """,
    "valid_actions": ["1"],
    "action_responses": {
        "1": "Please register through our online portal: http://stokveldigital.uksouth.azurecontainer.io/onboard",
    },
    "state": -1,
}

REGISTERED_NUMBER = {
    "tag": "registered_number",
    "message": """
    Hi there, welcome back! Please select one of the following options to proceed:
        1. Stokvel services
        2. My profile
    """,
    "valid_actions": ["1", "2"],
    "state_selection": {
        "1": "stokvel_services",
        "2": "my_profile",
    },
    "state": 0,
}

STOKVEL_SERVICES = {
    "tag": "stokvel_services",
    "message": """
    Please select one of the following options to proceed:
    1. Join a stokvel
    2. Create a stokvel
    3. My stokvels
    4. Back
    """,
    "valid_actions": ["1", "2", "3", "4"],
    "action_responses": {
        "1": "Please join a stokvel through our online portal: http://stokveldigital.uksouth.azurecontainer.io/stokvel/join_stokvel",
        "2": "Please create a new stokvel through our online portal: http://stokveldigital.uksouth.azurecontainer.io/stokvel/create_stokvel",
    },
    "action_requests": {"3": "/stokvel/my_stokvels"},
    "state_selection": {"4": "back_state"},
    "state": 1,
}

STOKVEL_ACTIONS_USER = {
    "tag": "stokvel_actions_user",
    "message": """
    Welcome to stokvel actions page! Please select one of the following options to proceed:
    1. View stokvel summary
    2. View stokvel constitution
    3. View your interest
    4. View stokvel interest
    5. Leave stokvel
    6. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "/stokvel/stokvel_summary",
        "2": "/stokvel/view_constitution",
        "3": "/stokvel/user_total_interest",
        "4": "/stokvel/stokvel_total_interest",
    },
    "state_selection": {"5": "leave_stokvel", "6": "back_state"},
    "state": 1,
}


STOKVEL_ACTIONS_ADMIN = {
    "tag": "stokvel_actions_admin",
    "message": """
    Welcome to stokvel actions page! Please select one of the following options to proceed:
    1. View stokvel summary
    2. View stokvel constitution
    3. View stokvel interest
    4. Leave stokvel
    5. Administrative actions
    6. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "/stokvel/stokvel_summary",
        "2": "/stokvel/view_constitution",
        "3": "/stokvel/stokvel_total_interest",
    },
    "state_selection": {"4": "leave_stokvel", "5": "admin_services", "6": "back_state"},
    "state": 1,
}

LEAVE_STOKVEL = {
    "tag": "leave_stokvel",
    "message": """
    Are you are sure you want to leave this stokvel? You will lose your interest earned on your contributions:
    1. Leave stokvel
    2. Back
    """,
    "valid_actions": ["1", "2"],
    "action_requests": {"1": "stokvels/admin/leave_stokvel"},
    "state_selection": {"2": "back_state"},
    "state": 1,
}

STOKVEL_ADMIN_SERVICES = {
    "tag": "admin_services",
    "message": """
Welcome to stokvel administration! Please select one of the following options to proceed:
1. Change stokvel name
2. Change maximum member number
3. View pending applications
4. Back
""",
    "valid_actions": ["1", "2", "3", "4"],
    "action_requests": {  # Maybe we specify the endpoint per action
        "1": "/stokvel/admin/change_stokvel_name",  # We need to specify the type of endpoint, ie endpoing:Method(post)
        "2": "/stokvel/admin/change_member_number",
    },
    "state_selection": {"4": "back_state"},
    "action_responses": {
        "3": "View pending applications here: http://stokveldigital.uksouth.azurecontainer.io/stokvel/approvals",
    },
    "input_request_states": {
        "1": {
            "tag": "admin_services:input_request_states:1",
            "message": "Please provide the new name of your stokvel. A minimum of one character is required.",
            "valid_type": str,
            "invalid_message": "Please make ensure your new name is at least one character long. Returning to previous menu.",
            "action": "1",
        },
        "2": {
            "tag": "admin_services:input_request_states:2",
            "message": "Please specify new maximum amount of members in your stokvel.",
            "valid_type": float,
            "invalid_message": "Please make sure the number of members is numeric and greater than 0. Returning you to the previous menu.",
            "action": "2",
        },
    },
    "state": 1,
}

MY_PROFILE = {
    "tag": "my_profile",
    "message": """
    Please select one of the following actions to proceed:
    1. View my profile
    2. Update my profile
    3. Back""",
    "valid_actions": ["1", "2", "3"],
    "state_selection": {"1": "view_profile", "2": "update_profile", "3": "back_state"},
    "state": 1,
}

VIEW_PROFILE = {
    "tag": "view_profile",
    "message": """
    Please select what you would view to see on your profile:
    1. View Account Details
    2. Back""",
    "valid_actions": ["1", "2"],
    "action_requests": {
        "1": "/users/view_account_details",
    },
    "state_selection": {"2": "back_state"},
    "state": 2,
}

UPDATE_PROFILE = {
    "tag": "update_profile",
    "message": """
    Please select what you would like to update:
    1. Update user name
    2. Update user surname
    3. Back""",
    "valid_actions": ["1", "2", "3"],
    "action_requests": {
        "1": "/users/admin/update_username",
        "2": "/users/admin/update_usersurname",
    },
    "state_selection": {"3": "back_state"},
    "input_request_states": {
        "1": {
            "tag": "update_profile:input_request_states:1",
            "message": "Please update your updated name. A minimum of one character is required.",
            "valid_type": str,
            "invalid_message": "Please make ensure your new name is at least one character long. Returning to previous menu.",
            "action": "1",
        },
        "2": {
            "tag": "update_profile:input_request_states:2",
            "message": "Please update your updated surname. A minimum of one character is required.",
            "valid_type": str,
            "invalid_message": "Please make ensure your new surnamename is at least one character long. Returning to previous menu.",
            "action": "2",
        },
    },
    "state": 1,
}


# 25291716
