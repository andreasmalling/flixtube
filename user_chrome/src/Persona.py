from time import sleep


class Persona:
    def __init__(self, user, hash, leave=False):
        self.user = user
        self.hash = hash
        self.leave = leave

    def act(self):
        raise NotImplementedError("Persona class is abstract")

    def leave_website(self):
        self.user.browser.quit()
        if not self.leave:
            while True:
                print("sleep")
                sleep(1)
