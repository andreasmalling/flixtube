from splinter import Browser
from time import sleep

browser = Browser('chrome')

url='http://localhost:63343/IPFS-Playground/NodeHelloWorld/webplayer.html?_ijt=h6d5lha25ahi9dvv623gujt3t7'

browser.visit(url)

# Get elements
player = browser.find_by_id("videoPlayer").first
steamedHams = browser.find_option_by_text("Steamed Hams").first
hashInput = browser.find_by_id('videoHash').first
hashBtn = browser.find_by_id("loadHashBtn").first
localCheck = browser.find_by_id("localCheck").first
seekPos = browser.find_by_id("seekPos").first
seekBtn = browser.find_by_id("seekBtn").first
randBtn = browser.find_by_id("seekRandomBtn").first

# Select from list
steamedHams.click()
sleep(2)

# Access IPFS hosted mpd
hash = "QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs"
hashInput.fill(hash)
hashBtn.click()

sleep(3)

# Skip to 2:00
seekPos.fill(120)
seekBtn.click()

pos = player["currentTime"]

assert (pos == '120')


sleep(3)

# Skip to random position
randBtn.click()

sleep(3)

#browser.quit()