#! /bin/bash
# v0.4

# Check args
if [ $# -ne 2 ] ; then
	echo "Supply segment duration and INPUTFILE file"
    exit 1
fi

# INPUTS
SEGDURATION=$1
INPUTFILE=$2

# FRAMERATE:
# Get the FRAMERATE (fps) of INPUTFILE video
FRAMERATE=$(ffmpeg -i "$INPUTFILE" 2>&1 | sed -n "s/.*, \(.*\) fp.*/\1/p")
echo 'FRAMERATE OF INPUTFILE: '"$FRAMERATE"

## KEYFRAMRATE:
## Should *in theory* only be divided by 1000 (for ms to s), 
## to ensure an I-frame at the start of each segment
KEYFRAMERATE=$(echo "$SEGDURATION"*"$FRAMERATE"/1000 | bc)
echo 'KEYFRAMERATE OF ENCODING: '"$KEYFRAMERATE"

# FILES:
FILENAME="${INPUTFILE%.*}"									# INPUTFILE without file-extension
ENCODING="$FILENAME"_key_"$KEYFRAMERATE".mp4				# Output name of (re-)encoding
MPD="$FILENAME"_"$SEGDURATION"								# Name of manifest file
SEGS="$MPD"'_$RepresentationID$/Segment_$Number$$Init=0$'	# Segment scheme

# Clean up previous runs with same parameters
rm -r "$MPD"*

# (Re-)encode (https://stackoverflow.com/a/30982414)
ffmpeg -i $INPUTFILE											\
	   -c:v libx264 											\
	   -x264-params keyint="$KEYFRAMERATE":scenecut=0 			\
	   -c:a libvo_aacenc										\
	   "$ENCODING"

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
MP4Box -dash $SEGDURATION										\
	   -rap 													\
	   -profile dashavc264:live 								\
	   -out "$MPD"												\
	   -segment-name "$SEGS"									\
	   -bs-switching no											\
	   -url-template											\
	   "$ENCODING"#video:id=video "$ENCODING"#audio:id=audio