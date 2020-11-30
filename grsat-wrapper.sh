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
DATA="$TMP/data"   # SATNOGS_OUTPUT_PATH

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
    case "$NORAD" in
    43803)  # JY1SAT
      echo "$PRG Decoding JY1SAT"
      gr_satellites "$NORAD" --clk_limit 0.03 --samp_rate 48000 --f_offset 12000 --throttle --udp --start_time "$DATEF" --kiss_out "$KSS" > "$LOG" &
      ;;
    42017)  # NAYIF-1
      echo "$PRG Decoding NAYIF-1"
      gr_satellites "$NORAD" --clk_limit 0.03 --samp_rate 48000 --f_offset 12000 --throttle --udp --start_time "$DATEF" --telemetry_output "$TLM" --kiss_out "$KSS" > "$LOG" &
      ;;
    39444)  # FUNCUBE-1
      echo "$PRG Decoding FUNCUBE-1"
      gr_satellites "$NORAD" --clk_limit 0.03 --samp_rate 48000 --f_offset 12000 --throttle --udp --start_time "$DATEF" --telemetry_output "$TLM" --kiss_out "$KSS" > "$LOG" &
      ;;
    *)
      echo "$PRG Decoding default"
      gr_satellites "$NORAD" --samp_rate 48000 --throttle --udp --start_time "$DATEF" --kiss_out "$KSS" > "$LOG" &
      ;;
    esac
  else
    echo "$PRG Satellite not supported"
  fi
fi

if [ "$CMD" == "stop" ]; then
  echo "$PRG Stopping observation $ID"
  killall -q -9 gr_satellites

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
fi

