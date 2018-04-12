from time import sleep

from Persona import Persona


class SkipperPersona(Persona):

    def __init__(self, user, hash, leave=False, skip_length=10, watch_time=3):
        super().__init__(user, hash, leave)
        self.skip_length = skip_length
        self.watch_time = watch_time

    def get_time(self):
        return self.user.browser.evaluate_script("player.time()")

    def act(self):
        self.user.visit("http://localhost:8000/webplayer.html")
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

