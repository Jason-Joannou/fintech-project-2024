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
    """,
    "valid_actions": ["1", "2", "3", "4"],
    "action_responses": {
        "1": "Please register through our online portal: https://stokvels.com/register",
        "2": "Please register through our online portal: https://stokvels.com/register",
        "3": "Please specify the amount you want to contribute in Rands and the name of the stokvel you would like to contribute to.",
        "4": "Please specify the stokvel you would like to leave.",
    },
    "state": 1,
}


# 25291716
