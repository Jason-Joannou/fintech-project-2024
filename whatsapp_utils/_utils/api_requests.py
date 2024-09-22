from typing import Dict, Optional

import requests

BASE_URL = "http://127.0.0.1:5000"


def query_endpoint(endpoint_suffix: str, payload: Optional[Dict] = None) -> str:
    """
    Sends an HTTP request to a specified API endpoint and returns the response as a string.

    This method constructs a full URL by appending the `endpoint_suffix` to the base URL,
    then sends either a GET or POST request based on whether a payload is provided.

    Args:
        endpoint_suffix (str): The suffix to append to the base URL to form the complete endpoint.
        payload (Optional[Dict], optional): A dictionary containing the data to send with
                                            a POST request. If not provided, a GET request is made.
                                            Defaults to None.

    Returns:
        str: The text response from the server if the request is successful.
             If an error occurs, a string describing the error is returned.

    Raises:
        requests.exceptions.HTTPError: If an HTTP error occurs during the request.
        Exception: For any other exceptions during the request.
    """

    full_url = f"{BASE_URL}{endpoint_suffix}"

    try:
        if payload is not None:  # Post request
            response = requests.post(full_url, json=payload, timeout=5)
        else:  # Get request
            response = requests.get(full_url, timeout=5)

        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Other error occurred: {err}"
