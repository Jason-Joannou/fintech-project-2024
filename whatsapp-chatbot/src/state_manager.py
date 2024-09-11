class StateManager:
    """
    docstring
    """
    def __init__(self):
        self.user_states = {}

    def get_state(self, user_id):
        """
        docstring
        """
        return self.user_states.get(user_id, {})

    def set_state(self, user_id, state):
        """
        docstring
        """
        self.user_states[user_id] = state

    def clear_state(self, user_id):
        """
        docstring
        """
        if user_id in self.user_states:
            del self.user_states[user_id]