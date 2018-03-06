# Translate encode.sh to python
import sys
import os
import subprocess
import re
from xml.dom import minidom
import subprocess

print("v0.5\n")

if (len(sys.argv) < 2):
    print("Please provide segment duration and input file as arguments")
    sys.exit(1)

SEGDURATION = int(sys.argv[1])
INPUTFILE = sys.argv[2]

FRAMERATE = 29.97

KEYFRAMERATE = (SEGDURATION * FRAMERATE) / 1000

FILENAME = os.path.splitext(os.path.basename(INPUTFILE))[0]
ENCODING = FILENAME + "_key_" + str(KEYFRAMERATE) + ".mp4"
MPD = str(SEGDURATION) + "_" + FILENAME
SEGS = MPD + "_$RepresentationID$/Segment_$Number$$Init=0$"

# Clean up previous runs with same parameters
subprocess.run(["rm", "-r", MPD + "*"])

# (Re-)encode (https://stackoverflow.com/a/30982414)
subprocess.run(["ffmpeg",
                "-i", INPUTFILE,
                "-c:v", "libx264",
                "-x264-params", "keyint=" + str(KEYFRAMERATE) + ":scenecut=0",
                "-c:a", "libvo_aacenc",
                ENCODING])

# Notes on encoding:
# ==================
# Results in poor quility due to scenecut:0, which avoids dynamic I-frames at scene cuts.
# https://stackoverflow.com/a/41735741
# https://videoblerg.wordpress.com/2017/11/10/ffmpeg-and-how-to-use-it-wrong/
# Alt. versions at
#   https://stackoverflow.com/a/36185180
#   https://gist.github.com/ddennedy/16b7d0c15843829b4dc4
# Audio codec change?: https://trac.ffmpeg.org/wiki/Encode/AAC#NativeFFmpegAACencoder

# Package
subprocess.run(["MP4Box",
                "-dash", str(SEGDURATION),
                "-rap",
                "-profile", "dashavc264:live",
                "-out", MPD,
                "-segment-name", SEGS,
                "-bs-switching", "no",
                "-url-template",
                ENCODING + "#video:id=video",
                ENCODING + "#audio:id=audio"])

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

# 2) Edit mpd

mpd = minidom.parse(FILENAME + "_" + str(SEGDURATION) + ".mpd")
adaptionSets = mpd.getElementsByTagName("AdaptationSet")
for a in adaptionSets:
    if (a.getElementsByTagName("Representation")[0].attributes["id"].value == "video"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          video_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", video_hash + "/Segment_0.mp4")
    elif (a.getElementsByTagName("Representation")[0].attributes["id"].value == "audio"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          audio_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", audio_hash + "/Segment_0.mp4")
# write to file
f = open("fixed.mpd", "w")
mpd.writexml(f)
f.close()


# 3) Add mpd to IPFS
print("")
subprocess.call(["ipfs", "add", "fixed.mpd"])
