from splinter import Browser
from time import sleep
import subprocess

# Setup IPFS
subprocess.run(["ipfs", "init"])
subprocess.Popen(["ipfs", "daemon"])

browser = Browser('chrome')

url='http://127.0.0.1:8080/ipfs/QmPYSNtQ5XMp88zZJVNYSLafjQZXHGN5T3pht71SdukVcG'

browser.visit(url)

# Get elements
player = browser.find_by_id("videoPlayer").first
demo = browser.find_option_by_text("IPFS").first
hashInput = browser.find_by_id('videoHash').first
hashBtn = browser.find_by_id("loadHashBtn").first
localCheck = browser.find_by_id("localCheck").first
seekPos = browser.find_by_id("seekPos").first
seekBtn = browser.find_by_id("seekBtn").first
randBtn = browser.find_by_id("seekRandomBtn").first

# Select from list
# demo.click()
# sleep(2)

# Access IPFS hosted mpd
hash = "QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs"
hashInput.fill(hash)
hashBtn.click()


# # Skip to 2:00
# seekPos.fill(120)
# seekBtn.click()
#
# pos = player["currentTime"]
#
# assert (pos == '120')
#
#
# sleep(3)
#
# # Skip to random position
# randBtn.click()
#
sleep(600)

#browser.quit()