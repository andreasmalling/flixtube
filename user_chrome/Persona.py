class Persona:
    def __init__(self, user, hash):
        self.user = user
        self.hash = hash

    def act(self):
        raise NotImplementedError("Persona class is abstract")
