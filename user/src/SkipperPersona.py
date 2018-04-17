from time import sleep

from Persona import Persona

DEFAULTSKIPLENGTH = 10
DEFAULTWATCHTIME = 3

class SkipperPersona(Persona):

    def __init__(self, user, hash, leave, other_args):
        super().__init__(user, hash, leave, other_args)
        if len(other_args) > 0:
            self.skip_length = int(other_args[0])
        else:
            self.skip_length = DEFAULTSKIPLENGTH

        if len(other_args) > 1:
            self.watch_time = int(other_args[1])
        else:
            self.watch_time = DEFAULTWATCHTIME

    def get_time(self):
        return self.user.browser.evaluate_script("player.time()")

    def act(self):
        self.user.visit("http://host/webplayer.html")
        self.user.watch_hash(self.hash)
        duration = None
        while duration is None:
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")

        jump_to = 0
        while jump_to < duration:
            if self.user.browser.evaluate_script("player.isSeeking()"):
                sleep(0.1)
                continue
            self.user.jump_to(jump_to)
            sleep(self.watch_time)
            jump_to = self.get_time() + self.skip_length

