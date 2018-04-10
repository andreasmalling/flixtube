# Translate encode.sh to python
import sys
import os
from shutil import rmtree, move
from xml.dom import minidom
import subprocess
from ffprobe3 import FFProbe

print("v0.8\n")

if (len(sys.argv) < 2):
    print("Please provide segment duration (ms) and input file as arguments, followed by optional CFR (0-51 where 0 is best) and duration (s)")
    sys.exit(1)

segment_duration = int(sys.argv[1])
input_filepath = sys.argv[2]

# probe metadata
input_metadata = FFProbe(input_filepath)
for stream in input_metadata.streams:
    if stream.is_video():
        input_framerate = stream.frames() / stream.duration_seconds()

output_keyinput_framerate = round((segment_duration * input_framerate) / 1000)

dir_dashed = "video_dashed"
dir_encoded = "video_encoded"

### SETUP FOLDERS ###
# Set up folders if first run
def makeFolder(folderpath):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

dashed = os.path.join(os.getcwd(), dir_dashed)
encoded = os.path.join(os.getcwd(), dir_encoded)

makeFolder(dashed)
makeFolder(encoded)

### SETUP FFMPEG ###

ffmpeg_options = ["ffmpeg",
                "-i", input_filepath,
                "-codec:v", "libx264",
                "-x264-params", "keyint=" + str(output_keyinput_framerate) + 
                				":min-keyint=" + str(output_keyinput_framerate) +
                				":scenecut=0",
                "-strict", "-2",
                "-codec:a", "aac"]

input_name = os.path.splitext(os.path.basename(input_filepath))[0]
output_filename = input_name + "_key-" + str(output_keyinput_framerate)
output_dir = input_name + "_key-" + str(segment_duration)

if (len(sys.argv) > 2):
	output_crf = sys.argv[3]
	ffmpeg_options.extend( ["-crf", output_crf] )
	output_filename += "_crf-" + output_crf
	output_dir += "_crf-" + output_crf

if (len(sys.argv) > 3):
	output_duration = sys.argv[4]
	ffmpeg_options.extend( ["-t", output_duration] )
	output_filename += "_dur-" + output_duration
	output_dir += "_dur-" + output_duration

mpd_filepath = input_name + ".mpd"
segment_formating = input_name + "_$RepresentationID$/Segment_$Number$$Init=0$"

### CLEAN UP ###
# Clean up previous runs with same parameters
for fname in os.listdir(dashed):
    if fname.startswith(output_dir):
        path = os.path.join(dashed, fname)
        if os.path.isfile(path):
            os.remove(path)
        else:
            rmtree(path)

# (Re-)encode (https://stackoverflow.com/a/30982414)
output_filepath = dir_encoded + "/" + output_filename + ".mp4"
ffmpeg_options.append(output_filepath)

subprocess.run(ffmpeg_options)

# Notes on encoding:
# ==================
# Results in poor quility due to scenecut:0, which avoids dynamic I-frames at scene cuts.
# https://stackoverflow.com/a/41735741
# https://videoblerg.wordpress.com/2017/11/10/ffmpeg-and-how-to-use-it-wrong/
# Alt. versions at
#   https://stackoverflow.com/a/36185180
#   https://gist.github.com/ddennedy/16b7d0c15843829b4dc4
# Audio codec change?: https://trac.ffmpeg.org/wiki/Encode/AAC#NativeFFmpegAACencoder

### DASHing ###
mp4box_options = ["MP4Box",
                  "-dash", str(segment_duration),
                  "-rap",
                  "-profile", "dashavc264:live",
                  "-out", input_name,
                  "-segment-name", segment_formating,
                  "-bs-switching", "no",
                  "-url-template",
                  output_filepath + "#video:id=video",
                  output_filepath + "#audio:id=audio"]

subprocess.run(mp4box_options)

### Generate IPFS Hashes of video and audio ###

video_folder_name = input_name + "_video"
audio_folder_name = input_name + "_audio"

if not(os.path.exists(video_folder_name) and os.path.exists(audio_folder_name) and os.path.exists(mpd_filepath)):
    print("Files not generated for upload to IPFS")
    sys.exit(2)

def ipfs_hash_path(path):
    ipfs_options = ["ipfs", "add", "-Q", "--only-hash", "-r"]
    ipfs_options.append( path )

    process = subprocess.Popen(ipfs_options, stdout=subprocess.PIPE)
    out, err = process.communicate()

    return out.decode("utf-8")

audio_hash = ipfs_hash_path(audio_folder_name).rstrip()
video_hash = ipfs_hash_path(video_folder_name).rstrip()

### Edit MPD with IPFS Hashes ###
if audio_hash is None or video_hash is None:
    print("Files not hashed for IPFS")
    sys.exit(1)

mpd = minidom.parse(mpd_filepath)
adaptionSets = mpd.getElementsByTagName("AdaptationSet")
for a in adaptionSets:
    if (a.getElementsByTagName("Representation")[0].attributes["id"].value == "video"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          video_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", video_hash + "/Segment_0.mp4")
    elif (a.getElementsByTagName("Representation")[0].attributes["id"].value == "audio"):
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("media",          audio_hash + "/Segment_$Number$.m4s")
        a.getElementsByTagName("SegmentTemplate")[0].setAttribute("initialization", audio_hash + "/Segment_0.mp4")

# write to file
f = open(mpd_filepath, "w")
mpd.writexml(f)
f.close()

### Move newly created files to output destination ###
makeFolder(dashed + "/" + output_dir)
move(os.path.join(os.getcwd(), video_folder_name), dashed + "/" + output_dir)
move(os.path.join(os.getcwd(), audio_folder_name), dashed + "/" + output_dir)
move(os.path.join(os.getcwd(), mpd_filepath), dashed + "/" + output_dir)