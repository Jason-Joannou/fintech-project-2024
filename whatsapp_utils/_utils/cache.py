class Cache:
    """
    A simple in-memory key-value store for caching data.

    This class allows for storing, retrieving, and deleting key-value pairs in a dictionary-based cache.
    """

    def __init__(self):
        """
        Initializes an empty cache.

        The cache is represented as a dictionary where keys are strings, and values are stored as strings.
        """
        self.cache = {}

    def get(self, key: str):
        """
        Retrieves the value associated with the given key from the cache.

        Args:
            key (str): The key whose corresponding value is to be retrieved.

        Returns:
            The value associated with the key if it exists, otherwise None.
        """
        return self.cache.get(key)

    def set(self, key: str, value: str):
        """
        Stores a key-value pair in the cache.

        Args:
            key (str): The key to associate with the value.
            value (str): The value to store in the cache.
        """
        self.cache[key] = value

    def delete(self, key: str):
        """
        Deletes the key-value pair from the cache if the key exists.

        Args:
            key (str): The key to be removed from the cache.
        """
        if key in self.cache:
            del self.cache[key]
