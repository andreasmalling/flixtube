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


    def get_time(self):
        time = self.user.browser.evaluate_script("player.time()")
        while time is None:
            print("Retrying get_time")
            sleep(0.01)
            time = self.user.browser.evaluate_script("player.time()")
        return time


    def get_duration(self):
        dur = self.user.browser.evaluate_script("player.duration()")
        while dur is None:
            print("Retrying get_duration")
            sleep(0.01)
            dur = self.user.browser.evaluate_script("player.duration()")
        return dur


    def sleep_until(self, end, interval=1):
        progress = self.get_time()

        while progress < end:
            sleep(interval)
            progress = self.get_time()