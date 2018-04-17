from time import sleep

from Persona import Persona
from User import User

class BingePersona(Persona):

    def __init__(self, user, hash, leave, other_args):
        super().__init__(user, hash, leave, other_args)

        # set if leech (False by default)
        if len(other_args) > 0:
            self.leech = int(other_args[0])
        else:
            self.leech = 0

    def act(self):
        self.user.visit("http://host/webplayer.html")
        if self.leech == 1:
            self.user.toggle_gateway()
        self.user.watch_hash(self.hash)
        duration = None
        while duration is None:
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")
        sleep(duration)
