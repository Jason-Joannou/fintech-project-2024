class Cache:
    """
    docstring
    """

    def __init__(self):
        self.cache = {}

    def get(self, key):
        """
        docstring
        """
        return self.cache.get(key)

    def set(self, key, value):
        """
        docstring
        """
        self.cache[key] = value

    def delete(self, key):
        """
        docstring
        """
        if key in self.cache:
            del self.cache[key]
