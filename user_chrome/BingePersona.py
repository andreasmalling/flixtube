from Persona import Persona


class BingePersona(Persona):
    def act(self):
        self.user.visit("http://localhost:8000/webplayer.html")
        self.user.browser.find_option_by_text("Bitmovin (Adaptive)").first.click()