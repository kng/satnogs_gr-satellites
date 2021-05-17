#!/usr/bin/env bash
#
# Created by: SA2KNG
# Updated by: PE0SAT
#
# Dependecies:
#   gr_satellites, ffmpeg and wget
#
# The script needs three arguments:
#   NoradID, URL to satnogs audio file and OFFSET
#
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo ""
	echo " Please use NoradID, URL to satnogs audio link and OFFSET value"
    echo " ogg2sids \$1 \$2 \$3, example: NoradID URL OFFSET (0 or 1)"
	exit 1
fi

SAT="$1"
URL="$2"
OFFSET="$3"
OGG=${URL##*/}
WAV=${OGG%.ogg}.wav

F=${OGG%.*}
D=${F#*_*_}
B=${D//-/:}
DF=${D:0:11}${B:11:8}

if [ ! -z "${OGG##satnogs_*}" ] || [ "${#DF}" -ne 19 ] ; then
	echo " Something went wrong"
	exit 2
fi

echo "#-----------------------------------------------------------------------------#"
echo "#"
echo "#          About to fetch: $OGG"
echo "#       And convert it to: $WAV"
echo "# Then demod at timestamp: $DF"
echo "#                 NoradID: $SAT"
echo "#                  OFFSET: $OFFSET"
echo "#"
echo "# Sleep 5 seconds, Press CTRL-C to abort"
echo "#"

sleep 5

echo "# Download the audio file and convert it to gr_satellites input format."
echo "#"

wget --quiet -O "$OGG" "$URL"
ffmpeg -loglevel quiet -i "$OGG" "$WAV"

if [ "${OFFSET}" == "1" ] ; then
    echo "# Decoding Satellite $SAT with OFFSET enabled."
    gr_satellites "$SAT" --wavfile "$WAV" --samp_rate 48e3 --f_offset 12e3 --start_time "$DF" --throttle
else
    echo "# Decoding Satellite $SAT."
    if [ "$SAT" == "46276" ]; then
        gr_satellites "$SAT" --wavfile "$WAV" --samp_rate 48e3 --start_time "$DF" --throttle --disable_dc_block --deviation 500 --clk_bw 0.15
    else
        gr_satellites "$SAT" --wavfile "$WAV" --samp_rate 48e3 --start_time "$DF" --throttle
    fi
fi

echo "#"
echo "# End of SatNOGS audio file decoding"
echo "#"
echo "#-----------------------------------------------------------------------------#"

rm -f "$OGG" "$WAV"
