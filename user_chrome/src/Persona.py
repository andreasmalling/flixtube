class Persona:
    def __init__(self, user, hash, leave=False):
        self.user = user
        self.hash = hash
        self.leave = leave

    def act(self):
        raise NotImplementedError("Persona class is abstract")
