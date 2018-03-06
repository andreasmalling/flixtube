# Translate encode.sh to python
import sys
import os
import subprocess
import re
from xml.dom import minidom

if (len(sys.argv) < 2):
    print("Please provide segment duration and input file as arguments")
    sys.exit(1)

SEGDURATION = int(sys.argv[1])
INPUTFILE = sys.argv[2]

FRAMERATE = 25

KEYFRAMERATE = (SEGDURATION * FRAMERATE) / 1000

FILENAME = os.path.splitext(INPUTFILE)[0]
ENCODING = FILENAME + "_key_" + str(KEYFRAMERATE) + ".mp4"
MPD = str(SEGDURATION) + FILENAME
SEGS = MPD + "_$RepresentationID$/Segment_$Number$$Init=0$"

print("mpd: " + MPD)


# 1) Add video to IPFS

video_folder_name = FILENAME + "_" + str(SEGDURATION) + "_video"
audio_folder_name = FILENAME + "_" + str(SEGDURATION) + "_audio"


# upload video
process = subprocess.Popen(["ipfs", "add", "-r", video_folder_name], stdout=subprocess.PIPE)
out, err = process.communicate()
m = re.search("added (.+?) " + video_folder_name + "\n", out.decode("utf-8"))
if m:
    video_hash = m.group(1)

#upload audio
process = subprocess.Popen(["ipfs", "add", "-r", audio_folder_name], stdout=subprocess.PIPE)
out, err = process.communicate()
m = re.search("added (.+?) " + audio_folder_name + "\n", out.decode("utf-8"))
if m:
    audio_hash = m.group(1)

print("video hash:", video_hash, "audio hash:", audio_hash)

# 2) Edit mpd
# 3) Add mpd to IPFS

