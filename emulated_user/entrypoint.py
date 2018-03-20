from splinter import Browser
from time import sleep
import subprocess
from optparse import OptionParser

class Ipfs:
    def __init__(self):
        subprocess.run(["ipfs", "init"])
        subprocess.Popen(["ipfs", "daemon"])

class User:
    def __init__(self, isHeadless=True):
        sleep(10)
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

    def watch_hash(self, manifest):
        # Access IPFS hosted mpd
        self.hashInput.fill(manifest)
        self.hashBtn.click()

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


parser = OptionParser()
# Browser Options
parser.add_option("-m", "--manual", action="store_true", dest="manual", default=False)

# Bandwidth options
parser.add_option("-d","--download", action="store", type="int", dest="download")
parser.add_option("-u","--upload", action="store", type="int", dest="upload")

# IPFS Options
parser.add_option("--noipfs", action="store_true", dest="skipIpfs", default=False)

# Parse options
(options, args) = parser.parse_args()
manual = options.manual
download = options.download
upload = options.upload
skipIpfs = options.skipIpfs

# Handle Options
if not skipIpfs:
    ipfs = Ipfs()

bandwidth_args = []

if download is not None:
    bandwidth_args.append(["-d", download])
if upload is not None:
    bandwidth_args.append(["-u", upload])

if args:
    bandwidth_call = ["tc"]
    bandwidth_call.append(bandwidth_args)
    subprocess.call(bandwidth_call)

if manual:
    subprocess.run(["google-chrome", "host/webplayer.html"])
else:
    user = User(False)
    user.visit_hash("QmPYSNtQ5XMp88zZJVNYSLafjQZXHGN5T3pht71SdukVcG")
    user.watch_hash("QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs")
    sleep(10)