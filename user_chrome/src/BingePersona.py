from time import sleep

from Persona import Persona


class BingePersona(Persona):
    def act(self):
        self.user.visit("http://localhost:8000/webplayer.html")
        self.user.watch_hash(self.hash)
        duration = None
        while duration is None:
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")
        sleep(duration)
