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
TLM="$TMP/grsat_$ID.tlm"
KSS="$TMP/grsat_$ID.kss"
GRPID="$TMP/grsat.pid"
DATA="$TMP/data"   # SATNOGS_OUTPUT_PATH
KEEPLOGS=no       # yes = keep, all other = remove TLM KSS LOG

#DATE format fudge Y-m-dTH-M-S to Y-m-dTH:M:S
B=${DATE//-/:}
DATEF=${DATE:0:11}${B:11:8}

SATNAME=$(echo "$TLE" | jq .tle0 | sed -e 's/ /_/g' | sed -e 's/[^A-Za-z0-9._-]//g')
NORAD=$(echo "$TLE" | jq .tle2 | awk '{print $2}')
echo "$PRG Observation: $ID, Norad: $NORAD, Name: $SATNAME, Script: $SCRIPT"

exit 0

if [ "$CMD" == "start" ]; then
  if [ ! -f "$SATLIST" ]; then
    echo "$PRG Generating satellite list"
    gr_satellites --list_satellites | sed  -n -Ee  's/.*NORAD[^0-9]([0-9]+).*/\1/p' > "$SATLIST"
  fi

  if grep -Fxq "$NORAD" "$SATLIST"; then
    echo "$PRG Starting observation $ID"
    GROPT="$NORAD --samp_rate 48000 --throttle --udp --start_time $DATEF --kiss_out $KSS"
    case ${SCRIPT^^} in
    *BPSK*)
      echo "$PRG using bpsk settings"
      GROPT="$GROPT --clk_limit 0.03 --f_offset 12000"
      ;;
    *)
      echo "$PRG using default settings"
      ;;
    esac
    gr_satellites $GROPT > "$LOG" 2>> "$LOG" &
    echo $! > "$GRPID"
  else
    echo "$PRG Satellite not supported"
  fi
fi

if [ "$CMD" == "stop" ]; then
  echo "$PRG Stopping observation $ID"
  if [ -f "$GRPID" ]; then
    kill `cat "$GRPID"`
    rm -f "$GRPID"
  fi

  if [ -s "$TLM" ]; then
    echo "$PRG Got some telemetry!"
  else
    rm -f "$TLM"
  fi
  
  if [ -s "$KSS" ]; then
    echo "$PRG Got some kiss data!"
    if [ "$NORAD" == "43803" ]; then
      jy1sat_ssdv "$KSS" "${TMP}/data_${ID}_${DATE}" >> "$LOG"
      rm -f "${TMP}/data_${ID}_"*.ssdv
      mv "${TMP}/data_${ID}_"* "$DATA"
    else
      kiss_satnogs.py "$KSS" "${DATA}/data_${ID}_"
    fi
  else
    rm -f "$KSS"
  fi

  if [ -s "$LOG" ]; then
    echo "$PRG Got something in the log!"
  else
    rm -f "$LOG"
  fi

  if [ ${KEEPLOGS^^} == "YES" ]; then
    echo "$PRG Keeping logs, you need to purge them manually."
  else
    rm -f "$LOG" "$KSS" "$TLM"
  fi
fi

