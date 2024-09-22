from typing import Dict, Optional

import requests

BASE_URL = "http://127.0.0.1:5000"


def query_endpoint(endpoint_suffix: str, payload: Optional[Dict] = None) -> str:

    full_url = f"{BASE_URL}{endpoint_suffix}"

    try:
        if payload is not None:  # Post request
            response = requests.post(full_url, json=payload)
        else:  # Get request
            response = requests.get(full_url)

        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Other error occurred: {err}"
