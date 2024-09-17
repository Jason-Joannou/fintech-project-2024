class Cache:
    """
    docstring
    """

    def __init__(self):
        self.cache = {}

    def get(self, key: str):
        """
        docstring
        """
        return self.cache.get(key)

    def set(self, key: str, value: str):
        """
        docstring
        """
        self.cache[key] = value

    def delete(self, key: str):
        """
        docstring
        """
        if key in self.cache:
            del self.cache[key]
