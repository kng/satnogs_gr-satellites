#!/usr/bin/python3

# This script takes two arguments: {{BAUD}} {{SCRIPT_NAME}}
# and tries to figure out the IQ sample rate
# SA2KNG

import satnogs
import sys

sps=4
audio_samp_rate=48000
baudrate=9600
script='satnogs_fm.py'

if len(sys.argv) == 2 or len(sys.argv) == 3:
    try:
        baudrate = int(float(sys.argv[1]))  # example: 1200 or 1200.0
    except ValueError:
        baudrate = 9600
if len(sys.argv) == 3:
    script = sys.argv[2]

if baudrate < 1 or baudrate > 1e6:  # unknown (?)
    baudrate = 9600

if   '_bpsk' in script:
    print(satnogs.find_decimation(baudrate, 2, audio_samp_rate,sps)*baudrate)
elif '_fsk' in script:
    print(max(4,satnogs.find_decimation(baudrate, 2, audio_samp_rate))*baudrate)
elif '_sstv' in script:
    print(4*4160*4)
elif '_qubik' in script:
    print(max(4,satnogs.find_decimation(baudrate, 2, audio_samp_rate))*baudrate)
else:  # cw, fm, afsk, etc...
    print(audio_samp_rate)

