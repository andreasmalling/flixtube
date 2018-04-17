from time import sleep

from Persona import Persona

DEFAULTSECONDSLEFT = 10

class IncognitoPersona(Persona):

    def __init__(self, user, hash, leave, other_args):
        super().__init__(user, hash, leave, other_args)

        # set seconds left
        if len(other_args) > 0:
            self.seconds_left = int(other_args[0])
        else:
            self.seconds_left = DEFAULTSECONDSLEFT

    def act(self):
        self.user.visit("http://host/webplayer.html")
        self.user.watch_hash(self.hash)
        duration = None
        while duration is None:
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")
        self.user.jump_to(duration - self.seconds_left)
        sleep(self.seconds_left)
