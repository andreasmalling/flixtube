# Translate encode.sh to python
import sys
import os
from shutil import rmtree, move
from xml.dom import minidom
import subprocess
from ffprobe3 import FFProbe

print("v0.7\n")

if (len(sys.argv) < 2):
    print("Please provide segment duration and input file as arguments")
    sys.exit(1)

SEGDURATION = int(sys.argv[1])
INPUTFILE = sys.argv[2]

# probe metadata
metadata = FFProbe(INPUTFILE)
for stream in metadata.streams:
    if stream.is_video():
        FRAMERATE = stream.frames() / stream.duration_seconds()

KEYFRAMERATE = round((SEGDURATION * FRAMERATE) / 1000)

DIR_DASHED = "video_dashed"
DIR_ENCODED = "video_encoded"

FILENAME = os.path.splitext(os.path.basename(INPUTFILE))[0]
FILE_ENCODED = DIR_ENCODED + "/" + FILENAME + "_key_" + str(KEYFRAMERATE) + ".mp4"
MPD = FILENAME + "_" + str(SEGDURATION)
SEGS = MPD + "_$RepresentationID$/Segment_$Number$$Init=0$"

# Set up folders if first run
def makeFolder(folderpath):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

dashed = os.path.join(os.getcwd(), DIR_DASHED)
encoded = os.path.join(os.getcwd(), DIR_ENCODED)

makeFolder(dashed)
makeFolder(encoded)

# Clean up previous runs with same parameters
for fname in os.listdir(dashed):
    if fname.startswith(MPD):
        path = os.path.join(dashed, fname)
        if os.path.isfile(path):
            os.remove(path)
        else:
            rmtree(path)

print("Calculated KEYFRAMERATE:", KEYFRAMERATE)

# (Re-)encode (https://stackoverflow.com/a/30982414)
subprocess.run(["ffmpeg",
                "-loglevel", "error",
                "-i", INPUTFILE,
                "-c:v", "libx264",
                "-x264-params", "keyint=" + str(KEYFRAMERATE) + ":scenecut=0",
                "-strict", "-2", "-c:a", "aac",
                FILE_ENCODED])

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
                FILE_ENCODED + "#video:id=video",
                FILE_ENCODED + "#audio:id=audio"])

# 1) Add video to IPFS

video_folder_name = MPD + "_video"
audio_folder_name = MPD + "_audio"

if not(os.path.exists(video_folder_name) and os.path.exists(audio_folder_name) and os.path.exists(MPD + ".mpd")):
    print("Files not generated for upload to IPFS")
    sys.exit(2)


def ipfs_hash(folder_name):
    process = subprocess.Popen(["ipfs", "add", "-r", "-Q", "--only-hash", folder_name], stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode("utf-8")

audio_hash = ipfs_hash(audio_folder_name)
video_hash = ipfs_hash(video_folder_name)

# 2) Edit mpd

if audio_hash is None or video_hash is None:
    print("Files not hashed for IPFS")
    sys.exit(1)

mpd = minidom.parse(MPD + ".mpd")
adaptionSets = mpd.getElementsByTagName("AdaptationSet")
for a in adaptionSets:
    if (a.getElementsByTagName("Representation")[0].attributes["id"].value == "video"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          video_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", video_hash + "/Segment_0.mp4")
    elif (a.getElementsByTagName("Representation")[0].attributes["id"].value == "audio"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          audio_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", audio_hash + "/Segment_0.mp4")
# write to file
f = open(MPD + ".mpd", "w")
mpd.writexml(f)
f.close()


# 3) Add mpd to IPFS
print("")
subprocess.call(["ipfs", "add", "-Q", "--only-hash", MPD + ".mpd"])

# Move newly created files
move(os.path.join(os.getcwd(), video_folder_name), dashed)
move(os.path.join(os.getcwd(), audio_folder_name), dashed)
move(os.path.join(os.getcwd(), MPD + ".mpd"), dashed)