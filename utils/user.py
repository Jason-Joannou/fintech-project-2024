class User:
    # Update this to pydantic model
    """
    docstring
    """

    def __init__(self, name, surname, cell_number, id_number, wallet_id):
        """
        The constructor for the User class. It initializes the user's name, surname, cellphone number and ID number.

        Args:
            name (str): The user's name
            surname (str): The user's surname
            cell_number (str): The user's cellphone number
            id_number (str): The user's ID number
            wallet_id (str): The user's wallet ID
        """
        self.name = name
        self.surname = surname
        self.cell_number = cell_number
        self.id_number = id_number
        self.wallet_id = wallet_id

    def __repr__(self):
        """
        Return a string representation of the User object.

        The string representation should include the user's name, surname, cellphone number and ID number.

        Returns:
            str: A string representation of the User object.
        """
        return (
            f"User(name={self.name}, surname={self.surname}, "
            f"cell_number={self.cell_number}, id_number={self.id_number})"
        )
