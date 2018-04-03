from splinter import Browser
from time import sleep
import subprocess
from optparse import OptionParser

class Ipfs:
    def __init__(self):
        subprocess.run(["ipfs", "init"])

    def run_daemon(self):
        subprocess.Popen(["ipfs", "daemon"])

    def bootstrap_local(self):
        address = "/dnsaddr/bootstrap/tcp/4001/ipfs/QmRuQ3sSxtuJBHYKJnLcYDFK4RVELydNDJ9F2vPg9Uj1H3"
        subprocess.run(["ipfs", "bootstrap", "rm", "all"])
        subprocess.run(["ipfs", "bootstrap", "add", address])

    def bootstrap_default(self):
        subprocess.run(["ipfs", "bootstrap", "add", "default"])

    def add(self, path):
        subprocess.run(["ipfs", "add", path])

class User:
    def __init__(self, isHeadless=True):
        sleep(10)
        self.browser = Browser('firefox', headless=isHeadless)

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
parser.add_option("--head", action="store_true", dest="browserHead", default=False)

# IPFS Options
parser.add_option("--noipfs", action="store_false", dest="ipfsDaemon", default=True)
parser.add_option("-b", "--bootstrap", action="store_false", dest="ipfsLocal", default=True)

# Parse options
(options, args) = parser.parse_args()

# Init IPFS
ipfs = Ipfs()

# Handle Options
if options.ipfsDaemon:
    ipfs.run_daemon()

if options.ipfsLocal:
    ipfs.bootstrap_local()

if options.manual:
    subprocess.run(["firefox", "http://users-cs.au.dk/amao/exercises/website/webplayer.html"])
else:
    user = User(options.browserHead)
    # Persona Behaviour

    user.visit("http://host/webplayer.html")
    user.watch_hash("QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs")
    user.browser.find_option_by_text("Bitmovin (Adaptive)").first.click()
    sleep(301)