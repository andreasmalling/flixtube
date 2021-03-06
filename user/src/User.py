from time import sleep
from random import randint
from splinter import Browser


class User:
    def __init__(self, isHeadless=True):
        while True:
            try:
                self.browser = Browser('chrome', headless=isHeadless)
            except ConnectionResetError as e:
                print(e)
                wait = randint(1,10) / 10
                print("Sleeping for", wait, "seconds")
                sleep( wait )
                continue
            break


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
        self.localCheck = self.browser.find_by_id("localCheck").first

    def watch_hash(self, manifest):
        # Access IPFS hosted mpd
        self.hashInput.fill(manifest)
        self.hashBtn.click()

    def toggle_gateway(self):
        self.localCheck.click()

    def jump_to(self, seconds):
        self.seekPos.fill(str(seconds))
        self.seekBtn.click()