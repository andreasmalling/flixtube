from splinter import Browser
from time import sleep
import subprocess

class User:

    def setup_ipfs(self):
        subprocess.run(["ipfs", "init"])
        subprocess.Popen(["ipfs", "daemon"])

    def __init__(self, isHeadless=True):
        self.setup_ipfs()

        self.browser = Browser('chrome', headless=isHeadless)

    def visit(self, url):
        self.browser.visit(url)
        self.init_elements()

    def visit_hash(self, hash):
        self.browser.visit('http://127.0.0.1:8080/ipfs/' + hash)
        self.init_elements()

    def init_elements(self):
        self.player = self.browser.find_by_id("videoPlayer").first
        self.hashInput = self.browser.find_by_id('videoHash').first
        self.hashBtn = self.browser.find_by_id("loadHashBtn").first
        self.seekPos = self.browser.find_by_id("seekPos").first
        self.seekBtn = self.browser.find_by_id("seekBtn").first
        self.randBtn = self.browser.find_by_id("seekRandomBtn").first

    def execute(self, manifest):
        # Access IPFS hosted mpd
        self.hashInput.fill(manifest)
        self.hashBtn.click()

        sleep(600)

        # Skip to 2:00
        # seekPos.fill(120)
        # seekBtn.click()
        #
        # pos = player["currentTime"]
        #
        # assert (pos == '120')
        #
        # sleep(3)
        #
        # # Skip to random position
        # randBtn.click()
        #
        #browser.quit()

user = User(False)
user.visit_hash("QmPYSNtQ5XMp88zZJVNYSLafjQZXHGN5T3pht71SdukVcG")
user.execute("QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs")