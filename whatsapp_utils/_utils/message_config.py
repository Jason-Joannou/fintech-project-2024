UNREGISTERED_NUMBER = {
    "tag": "unregistered_number",
    "message": """
    Hi there! We noticed this number is not registered with us. Registering your number is needed to start contributing to Stokvels.
    Please select one of the following options to proceed:
    1. Register using Rafiki money
    2. Register using MTN Mobile Money
    """,
    "valid_actions": ["1", "2"],
    "action_responses": {
        "1": "Please register through our online portal: http://stokveldigital.uksouth.azurecontainer.io/onboard",
        "2": "Please register through our online portal: https://stokvels.com/register",
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
<<<<<<< HEAD
=======
    },
    "state": 0,
}

REGISTERED_NUMBER_ADMIN = {
    "tag": "registered_number_admin",
    "message": """
    Hi there, welcome back! Please select one of the following options to proceed:
    1. Stokvel Services
    2. Community Services
    3. Financial Reports
    4. Admin Services
    """,
    "valid_actions": ["1", "2", "3", "4"],
    "state_selection": {
        "1": "stokvel_services",
        "2": "community_services",
        "3": "financial_reports",
        "4": "admin_services",
>>>>>>> 9b015a5 (Changes to message config and data queries)
    },
    "state": 0,
}

STOKVEL_SERVICES = {
    "tag": "stokvel_services",
    "message": """
    Please select one of the following options to proceed:
<<<<<<< HEAD
    1. Join a stokvel
    2. Create a stokvel
    3. My stokvels
=======
    1. Join a stokvel 
    2. Create a stokvel 
    3. My stokvels
    4. Back
    """,
    "valid_actions": ["1", "2", "3", "4"],
    "action_responses": {
        "1": "Please register through our online portal: https://stokvels.com/register",
        "2": "Please register through our online portal: https://stokvels.com/register"},
    "action_requests": {
        "3": "stokvels/my_stokvels"},
    "state_selection": {
        "4": "back_state"},
    "state": 1,
}

COMMUNITY_SERVICES = {
    "tag": "community_services",
    "message": """
    Welcome to our community services! Please select one of the following options to proceed:
    1. Total Number of Stokvels
    2. Total Number of Members
    3. Total Number of Contributions
    4. Total Number of Members grouped by Stokvel
    5. Total Contributions grouped by Stokvel
    6. Back
    """,
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {  # Maybe we specify the endpoint per action
        "1": "/stokvels/total_stokvels",
        "2": "/users/total_users",
        "3": "/accounting/total_contributions",
        "4": "/users/users_by_stokvel",
        "5": "/accounting/contributions_by_stokvel",
    },
    "state_selection": {"6": "back_state"},
    "state": 1,
}

FINANCIAL_REPORTS = {
    "tag": "financial_reports",
    "message": """
    Welcome to your finacial reports services! Please select one of the following options to proceed:
    1. Your total contributions
    2. Your total stokvel payouts
    3. Audit a stokvel
>>>>>>> 9b015a5 (Changes to message config and data queries)
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
    2. Change my contribution amount
    3. View stokvel constitution
    4. Make a contribution
    5. Leave stokvel
    6. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "/stokvel/stokvel_summary",
        "2": "/stokvel/change_contribution",
        "3": "/stokvel/view_constitution",
        "4": "/stokvel/make_contribution",
    },
    "state_selection": {"5": "leave_stokvel", "6": "back_state"},
    "input_request_states": {
        "2": {
            "tag": "stokvel_actions_user:input_request_states:2",
            "message": "Please enter the new recurring contribution amount for your stokvel in Rands.",
            "valid_type": float,
            "invalid_message": "Please make sure you specify a number value. Returning to previous menu.",
            "action": "2",
        },
        "4": {
            "tag": "stokvel_actions_user:input_request_states:4",
            "message": "Please enter the contribution amount for your stokvel in Rands.",
            "valid_type": float,
            "invalid_message": "Please make sure you specify a number value. Returning to previous menu.",
            "action": "4",
        },
    },
    "state": 1,
}


STOKVEL_ACTIONS_ADMIN = {
    "tag": "stokvel_actions_admin",
    "message": """
    Welcome to stokvel actions page! Please select one of the following options to proceed:
    1. View stokvel summary
    2. Change my contribution amount
    3. View stokvel constitution
    4. Make a contribution
    5. Leave stokvel
    6. Administrative actions
    7. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6", "7"],
    "action_requests": {
        "1": "/stokvel/stokvel_summary",
        "2": "/stokvel/change_contribution",
        "3": "/stokvel/view_constitution",
        "4": "/stokvel/make_contribution",
    },
    "state_selection": {"5": "leave_stokvel", "6": "admin_services", "7": "back_state"},
    "input_request_states": {
        "2": {
            "tag": "stokvel_actions_admin:input_request_states:2",
            "message": "Please enter the new recurring contribution amount for your stokvel in Rands.",
            "valid_type": float,
            "invalid_message": "Please make sure you specify a number value. Returning to previous menu.",
            "action": "2",
        },
        "4": {
            "tag": "stokvel_actions_admin:input_request_states:4",
            "message": "Please enter the contribution amount for your stokvel in Rands.",
            "valid_type": float,
            "invalid_message": "Please make sure you specify a number value. Returning to previous menu.",
            "action": "4",
        },
    },
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
    "action_requests": {"1": "admin/leave_stokvel"},
    "state_selection": {"2": "back_state"},
    "state": 1,
}

STOKVEL_ADMIN_SERVICES = {
    "tag": "admin_services",
    "message": """
<<<<<<< HEAD
Welcome to stokvel administration! Please select one of the following options to proceed:
1. Change stokvel name
2. Change maximum member number
3. Change minimum contributing amount
4. Change payout date
5. View pending applications
6. Back
""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {  # Maybe we specify the endpoint per action
        "1": "/stokvel/admin/change_stokvel_name",  # We need to specify the type of endpoint, ie endpoing:Method(post)
        "2": "/stokvel/admin/change_member_number",
        "3": "/stokvel/admin/change_contributing_amt",
        "4": "/stokvel/admin/change_payout_date",
=======
    Welcome to your admin page! Please select one of the following options to proceed:
    1. View stokvel applications
    2. Change stokvel name
    3. Change maximum member number 
    4. Change minimum contributing amount
    5. Change payout date 
    6. Back
    """,
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "admin/admin_stokvels",
        "2": "admin/admin_stokvel_members",
>>>>>>> 9b015a5 (Changes to message config and data queries)
    },
    "state_selection": {"6": "back_state"},
    "action_responses": {
        "5": "View pending applications here: http://stokveldigital.uksouth.azurecontainer.io/stokvel/approvals",
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
        "3": {
            "tag": "admin_services:input_request_states:3",
            "message": "Please specify the minimum contributing for your stokvel.",
            "valid_type": float,
            "invalid_message": "Please make sure the amount is numeric and greater than 0. Returning you to the previous menu.",
            "action": "3",
        },
        "4": {
            "tag": "admin_services:input_request_states:4",
            "message": "Please specify the new payout date for your stokvel in the format dd/mm/yyy.",
            "valid_type": str,
            "invalid_message": "Please make sure you provide the new payout date in the format dd/mm/yyyy. Returning you to the previous menu.",
            "action": "4",
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
    1. View user name
    2. View user surname
    3. View wallet my address
    4. View my wallet balance
    5. My transactions
    6. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "/stokvel/view_username",
        "2": "/stokvel/view_usersurname",
        "3": "/stokvel/view_wallet_address",
        "4": "/stokvel/view_wallet_balances",
        "5": "/stokvel/view_transactions",
    },
    "state_selection": {"6": "back_state"},
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
        "1": "/admin/update_username",
        "2": "/admin/update_usersurname",
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
            "action": "1",
        },
    },
    "state": 1,
}

# Will be removed once the dynamic state is created
MY_STOKVELS = {
    "tag": "my_stokvels",
    "message": """ <insert message here> """,
    "valid_actions": ["1", "2", "3", "4"],
    "state_selection": {
        "1": "stokvel_actions_user",
        "2": "stokvel_actions_user",
        "3": "stokvel_actions_admin",
        "5": "back_state"},
}

STOKVEL_ACTIONS_USER = {
    "tag": "stokvel_actions_user",
    "message": """
    Welcome to stokvel actions page! Please select one of the following options to proceed:
    1. View stokvel summary
    2. Change my contribution amount
    3. View stokvel constitution
    4. Make a contribution
    5. Leave stokvel
    6. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6"],
    "action_requests": {
        "1": "admin/stokvel_summary",
        "2": "admin/change_contribution",
        "3": "admin/view_constitution",
        "4": "admin/make_contribution",
        "5": "admin/leave_stokvel",
    },
    "state_selection": {"6": "back_state"},
    "input_request_states": {
        "2": {
            "tag": "stokvel_actions_user:input_request_states:2",
            "message": "Please provide contribution amount for to your stokvel.",
            "valid_type": float, 
            "invalid_message": "Please make ensure your new name is at least one character long. Returning to previous menu.",
            "action": "2",
        },
    },
    "state": 1,
}


STOKVEL_ACTIONS_ADMIN = {
    "tag": "stokvel_actions_admin",
    "message": """
    Welcome to stokvel actions page! Please select one of the following options to proceed:
    1. View stokvel summary
    2. Change my contribution amount
    3. View stokvel constitution
    4. Make a contribution
    5. Leave stokvel
    6. Administrative actions
    7. Back""",
    "valid_actions": ["1", "2", "3", "4", "5", "6","7"],
    "action_requests": {
        "1": "admin/stokvel_summary",
        "2": "admin/change_contribution",
        "3": "admin/view_constitution",
        "4": "admin/make_contribution",
        "5": "admin/leave_stokvel",
    },
    "state_selection": {
        "6": "admin_services",
        "7": "back_state"},
    "input_request_states": {
        "2": {
            "tag": "stokvel_actions_user:input_request_states:2",
            "message": "Please provide contribution amount for to your stokvel.",
            "valid_type": float, 
            "invalid_message": "Please make ensure your new name is at least one character long. Returning to previous menu.",
            "action": "2",
        },
    },
    "state": 1,
}

STOKVEL_ADMIN_SERVICES = {
    "tag": "admin_services",
    "message": """
    Welcome to stokvel administration! Please select one of the following options to proceed:
    1. Change stokvel name
    2. Change maximum member number 
    3. Change minimum contributing amount
    4. Change payout date 
    5. View pending applications
    6. Back
    """,
    "valid_actions": ["1", "2", "3", "4", "5"],
    "action_requests": {  # Maybe we specify the endpoint per action
        "1": "/stokvels/change_stokvel_name",  # We need to specify the type of endpoint, ie endpoing:Method(post)
        "2": "/users/change_member_number",
        "3": "/accounting/change_contributing_amt",
        "4": "/users/change_payout_date",
    },
    "state_selection": {"6": "back_state"},
    "action_responses": {
        "5": "View pending applications here: https://stokvels.com/register",
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
        "3": {
            "tag": "admin_services:input_request_states:3",
            "message": "Please specify the minimum contributing for your stokvel.",
            "valid_type": float,
            "invalid_message": "Please make sure the amount is numeric and greater than 0. Returning you to the previous menu.",
            "action": "3",
        },
        "4": {
            "tag": "admin_services:input_request_states:4",
            "message": "Please specify the new payout date for your stokvel in the format dd/mm/yyy.",
            "valid_type": str,
            "invalid_message": "Please make sure you provide the new payout date in the format dd/mm/yyyy. Returning you to the previous menu.",
            "action": "4",
        }
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
    "state_selection": {
        "1": "view_profile",
        "2": "update_profile",
        "3": "back_state"},
    "state": 1,
}

VIEW_PROFILE = {
    "tag": "view_profile",
    "message": """
    Please select what you would view to see on your profile:
    1. View user name
    2. View user surname
    3. View wallet my addresses
    4. View my wallet balances
    5. My transactions
    6. Back""",
    "valid_actions": ["1", "2", "3","4","5","6"],
    "action_requests": {
        "1": "admin/view_username",
        "2": "admin/view_usersurname",
        "3": "admin/view_wallet_address",
        "4": "admin/view_wallet_balances",
        "5": "admin/view_transactions",
    },
    "state_selection": {
        "6": "back_state"},
    "state": 2,
}


UPDATE_PROFILE = {
    "tag": "update_profile",
    "message": """
    Please select what you would like to update:
    1. Update user name
    2. Update user surname
    3. Update wallet my addresses
    4. Update my cellphone number
    5. Back""",
    "valid_actions": ["1", "2", "3","4","5"],
    "action_requests": {
        "1": "admin/update_username",
        "2": "admin/update_usersurname",
        "3": "admin/update_wallet_address",
        "4": "admin/update_cellnumber",
    },
    "state_selection": {
        "5": "back_state"},
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
            "action": "1",
        },
        "3": {
            "tag": "update_profile:input_request_states:3",
            "message": "Please enter your new wallet address.",
            "valid_type": str,
            "invalid_message": "Please make sure the new wallet address is at least one character long. Returning you to the previous menu.",
            "action": "3",
        },
        "4": {
            "tag": "update_profile:input_request_states:4",
            "message": "Please enter your new wallet new cell phone number.",
            "valid_type": str,
            "invalid_message": "Please make sure your new cell phone number is at least one character long. Returning you to the previous menu.",
            "action": "4",
        }
    },
    "state": 1,
}


# 25291716
