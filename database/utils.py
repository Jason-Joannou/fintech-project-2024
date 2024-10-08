def extract_whatsapp_number(from_number: str) -> str:
    """
    Extracts the phone number from a string in the format 'prefix:number'.
    """
    # Ensure the string contains a colon and handle cases where it might not
    if ":" in from_number:
        return from_number.split(":", 1)[
            1
        ].strip()  # Get the part after the first colon
    return from_number  # Return the original if no colon is found
