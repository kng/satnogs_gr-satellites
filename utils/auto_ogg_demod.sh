#!/bin/bash
# takes one argument, URL to satnogs audio file. only rudimentary checks are made on the proper naming
if [ -z "$1" ]; then
	echo "Please use with URL to satnogs audio"
	exit 1
fi

URL="$1"
OGG=${URL##*/}
WAV=${OGG%.ogg}.wav

F=${OGG%.*}
D=${F#*_*_}
B=${D//-/:}
DF=${D:0:11}${B:11:8}

if [ ! -z "${OGG##satnogs_*}" ] || [ "${#DF}" -ne 19 ] ; then
	echo "Something went wrong"
	exit 2
fi

echo "About to fetch: $OGG"
echo "And convert it to: $WAV"
echo "Then demod at timestamp: $DF"
echo "Press CTRL-C to abort, running in 5s"
sleep 5

curl -o "$OGG" "$URL"
sox "$OGG" "$WAV"
gr_satellites DELFI-n3xt --wavfile "$WAV" --samp_rate 48e3 --f_offset 12e3 --start_time "$DF" --throttle
rm -f "$OGG" "$WAV"

