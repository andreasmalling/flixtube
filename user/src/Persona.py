from time import sleep


class Persona:
    def __init__(self, user, hash, leave, other_args):
        self.user = user
        self.hash = hash
        self.leave = leave
        self.other_args = other_args

    def act(self):
        raise NotImplementedError("Persona class is abstract")

    def leave_website(self):
        self.user.browser.quit()
        if not self.leave:
            while True:
                print("sleep")
                sleep(5)
