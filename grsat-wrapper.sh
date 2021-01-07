#!/bin/bash
# {command} {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}
export PYTHONPATH=/usr/local/lib/python3/dist-packages/

CMD="$1"     # $1 [start|stop]
ID="$2"      # $2 observation ID
FREQ="$3"    # $3 frequency
TLE="$4"     # $4 used tle's
DATE="$5"    # $5 timestamp Y-m-dTH-M-S
BAUD="$6"    # $6 baudrate
SCRIPT="$7"  # $7 script name, satnogs_bpsk.py

PRG="gr-satellites:"
TMP="/tmp/.satnogs"
SATLIST="$TMP/grsat_list.txt"  # SATNOGS_APP_PATH
LOG="$TMP/grsat_$ID.log"
KSS="$TMP/grsat_$ID.kss"
GRPID="$TMP/grsat_$SATNOGS_STATION_ID.pid"
DATA="$TMP/data"   # SATNOGS_OUTPUT_PATH

# Settings
KEEPLOGS=no       # yes = keep, all other = remove KSS LOG

# if IQ mode set, then you also need find_samp_rate.py
IQMODE=no          # yes = use IQ UDP data, all other = use audio UDP data

# uncomment and populate SELECTED with space separated norad id's
# to selectively submit data to the network
# if it's unset it will send all KISS demoded data, with possible dupes
#SELECTED="39444 44830 43803 42017 44832 40074"

#DATE format fudge Y-m-dTH-M-S to Y-m-dTH:M:S
B=${DATE//-/:}
DATEF=${DATE:0:11}${B:11:8}

SATNAME=$(echo "$TLE" | jq .tle0 | sed -e 's/ /_/g' | sed -e 's/[^A-Za-z0-9._-]//g')
NORAD=$(echo "$TLE" | jq .tle2 | awk '{print $2}')
echo "$PRG Observation: $ID, Norad: $NORAD, Name: $SATNAME, Script: $SCRIPT"

if [[ $UDP_DUMP_PORT == ?(-)+([0-9]) ]]; then
        AUDIO_PORT=$UDP_DUMP_PORT
        IQ_PORT=$((UDP_DUMP_PORT + 1))
else
        AUDIO_PORT=7355
        IQ_PORT=7356
fi

if [ ${CMD^^} == "START" ]; then
  if [ ! -f "$SATLIST" ]; then
    echo "$PRG Generating satellite list"
    gr_satellites --list_satellites | sed  -n -Ee  's/.*NORAD[^0-9]([0-9]+).*/\1/p' > "$SATLIST"
  fi

  if grep -Fxq "$NORAD" "$SATLIST"; then
    echo "$PRG Starting observation $ID"
    if [ ${IQMODE^^} == "YES" ]; then
      SAMP=`find_samp_rate.py $BAUD $SCRIPT`
      if [ -z ${SAMP} ]; then  # default 48k if script not found
        SAMP=48000
        echo "$PRG WARNING: find_samp_rate.py did not return valid sample rate!"
      fi
      GROPT="$NORAD --samp_rate $SAMP --iq --throttle --udp --udp_port $IQ_PORT --udp_raw --start_time $DATEF --kiss_out $KSS --ignore_unknown_args --use_agc"
      echo "$PRG running in IQ mode at $SAMP sps"
    else
      SAMP=48000
      GROPT="$NORAD --samp_rate $SAMP --throttle --udp --udp_port $AUDIO_PORT --start_time $DATEF --kiss_out $KSS --ignore_unknown_args --f_offset 12000"  # --clk_limit 0.03
      echo "$PRG running in audio mode at $SAMP sps"
    fi
    gr_satellites $GROPT > "$LOG" 2>> "$LOG" &
    echo $! > "$GRPID"
  else
    echo "$PRG Satellite not supported"
  fi
fi

if [ ${CMD^^} == "STOP" ]; then
  if [ -f "$GRPID" ]; then
    echo "$PRG Stopping observation $ID"
    kill `cat "$GRPID"`
    rm -f "$GRPID"
  fi

  if [ -s "$KSS" ]; then
    if [ -z ${SELECTED+x} ] || [[ ${SELECTED} =~ ${NORAD} ]]; then
      echo "$PRG processing KISS data to network"
      if [ "$NORAD" == "43803" ]; then
        jy1sat_ssdv "$KSS" "${TMP}/data_${ID}_${DATE}" >> "$LOG"
        rm -f "${TMP}/data_${ID}_"*.ssdv
        mv "${TMP}/data_${ID}_"* "$DATA"
      else
        kiss_satnogs.py "$KSS" -d "${DATA}/data_${ID}_" >> "$LOG"
      fi
    else
      echo "$PRG not sending KISS data to network"
    fi
  else
    rm -f "$KSS" # purge empty kiss file
  fi

  if [ ! -s "$LOG" ]; then # purge empty logs
    rm -f "$LOG"
  fi

  if [ ${KEEPLOGS^^} == "YES" ]; then
    echo "$PRG Keeping logs, you need to purge them manually."
  else
    rm -f "$LOG" "$KSS"
  fi
fi

