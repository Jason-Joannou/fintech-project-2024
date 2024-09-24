def extract_whatsapp_number(from_number: str) -> str:
    """
    docstring
    """
    return from_number.split(":")[1]
