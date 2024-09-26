class Storage:
    def __init__(self):
        self.data_store = {}

    def add_data(self, key, data):
        """
        Adds or updates the data for the given key.

        Args:
            key (str): The key to identify the stored data.
            data: The data to store.
        """
        self.data_store[key] = data

    def get_data(self, key):
        """
        Retrieves the latest data associated with the given key.

        Args:
            key (str): The key to identify the stored data.

        Returns:
            The latest data associated with the key, or None if the key is not found.
        """
        return self.data_store.get(key)