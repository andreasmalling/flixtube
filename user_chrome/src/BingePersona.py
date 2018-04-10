from time import sleep

from Persona import Persona
from User import User

class BingePersona(Persona):
    def act(self):
        self.user.visit("http://localhost:8000/webplayer.html")
        # self.user.browser.find_option_by_text("Bitmovin (Adaptive)").first.click()
        self.user.watch_hash(self.hash)
        duration = None
        while (duration is None):
            sleep(0.1)
            duration = self.user.browser.evaluate_script("player.duration()")
        sleep(duration)

        #leave
        if (not self.leave):
            while True:
                print("slep")
                sleep(1)
        self.user.browser.quit()