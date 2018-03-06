# Translate encode.sh to python
import sys
import os

if (len(sys.argv) < 2):
    print("Please provide segment duration and input file as arguments")
    sys.exit(1)

SEGDURATION = int(sys.argv[1])
INPUTFILE = sys.argv[2]

FRAMERATE = 25

KEYFRAMERATE = (SEGDURATION * FRAMERATE) / 1000

FILENAME = os.path.splitext(INPUTFILE)[0]
ENCODING = FILENAME + "_key_" + KEYFRAMERATE + ".mp4"
MPD = str(SEGDURATION) + FILENAME
SEGS = MPD + "_$RepresentationID$/Segment_$Number$$Init=0$"

print("mpd: " + MPD)


# 1) Add video to IPFS
# 2) Edit mpd
# 3) Add mpd to IPFS

