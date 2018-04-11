from time import sleep

from Persona import Persona


class IncognitoPersona(Persona):
    seconds_left = 10

    def act(self):
        self.user.visit("http://localhost:8000/webplayer.html")
        self.user.watch_hash(self.hash)
        duration = None
        while duration is None:
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")
        self.user.jump_to(duration - self.seconds_left)
        sleep(self.seconds_left)
