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
        "1": "Please register through our online portal: https://stokvels.com/register",
        "2": "Please register through our online portal: https://stokvels.com/register",
    },
    "state": -1,
}

REGISTERED_NUMBER = {
    "tag": "registered_number",
    "message": """
    Hi there, welcome back! Please select one of the following options to proceed:
    1. Stokvel Services
    2. Comunity Services
    3. Financial Reports
    """,
    "valid_actions": ["1", "2", "3"],
    "state_selection": {
        "1": "stokvel_services",
        "2": "community_services",
        "3": "financial_reports",
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
    },
    "state": 0,
}

STOKVEL_SERVICES = {
    "tag": "stokvel_services",
    "message": """
    Please select one of the following options to proceed:
    1. Create a stokvel
    2. Join a stokvel
    3. Contribute to a stockvel
    4. Leave a stockvel
    5. Back
    """,
    "valid_actions": ["1", "2", "3", "4", "5"],
    "action_responses": {
        "1": "Please register through our online portal: https://stokvels.com/register",
        "2": "Please register through our online portal: https://stokvels.com/register",
        "3": "Please specify the amount you want to contribute in Rands and the name of the stokvel you would like to contribute to.",
        "4": "Please specify the stokvel you would like to leave.",
    },
    "state_selection": {"5": "back_state"},
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
    4. Back
    """,
    "valid_actions": ["1", "2", "3", "4"],
    "action_requests": {
        "1": "accounting/total_user_contributions",
        "2": "accounting/total_user_payouts",
        "3": "accoutning/audit_stokvel",
    },
    "state_selection": {"4": "back_state"},
    "state": 1,
}

ADMIN_SERVICES = {
    "tag": "admin_services",
    "message": """
    Welcome to your admin page! Please select one of the following options to proceed:
    1. View your stokvels
    2. View your stokvel members
    3. Edit stokvel constitution
    4. Back""",
    "valid_actions": ["1", "2", "3", "4"],
    "action_requests": {
        "1": "admin/admin_stokvels",
        "2": "admin/admin_stokvel_members",
    },
    "action_responses": {
        "3": "You can edit your stokvel constitutions through our online portal: stokvels.com"
    },
    "state_selection": {"5": "back_state"},
    "state": 1,
}


# 25291716
