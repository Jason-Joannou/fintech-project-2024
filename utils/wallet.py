import random


class Wallet:
    # Update to pydantic model
    """
    docstring
    """

    def __init__(self, user_id, user_wallet, user_balance):
        """
        Initialize a Wallet object.

        :param id: Unique identifier for the Wallet object
        :type id: int
        :param user_id: Unique identifier for the user the wallet belongs to
        :type user_id: int
        :param user_wallet: Wallet address of the user
        :type user_wallet: str
        :param user_balance: Balance of the user in the wallet
        :type user_balance: float
        """
        self.id = self.generate_wallet_address()
        self.user_id = user_id
        self.user_wallet = user_wallet
        self.user_balance = user_balance

    def __repr__(self):
        """
        Return a string representation of the Wallet object.

        The string representation should be formatted like this:
        Wallet(id=1, user_id=123, user_wallet='WalletABC', user_balance=100.0)

        :return: A string representation of the Wallet object
        :rtype: str
        """
        return (
            f"Wallet(id={self.id}, user_id={self.user_id}, "
            f"user_wallet='{self.user_wallet}', user_balance={self.user_balance})"
        )

    def generate_wallet_address(self):
        """
        Generates a random 13-digit wallet address.

        Returns:
            str: A string representing the 13-digit wallet address.
        """
        wallet_number = random.randint(10**12, 10**13 - 1)
        wallet_address = str(wallet_number).zfill(13)

        return wallet_address
