#!/usr/bin/env python3

# usage: kiss_satnogs.py [-h] KISS_IN DATAPATH
# 
# Read "gr_satellites-formatted" KISS frames and output the timestamp and binary data.
# 
# positional arguments:
#   KISS_IN     Input KISS File.
#   DATAPATH    prefix for output files
# 
# optional arguments:
#   -h, --help  show this help message and exit

# Example:
# $ wget https://ia601407.us.archive.org/31/items/satnogs-observation-2901793/satnogs_2901793_2020-09-28T20-41-08.ogg
# $ sox satnogs_2901793_2020-09-28T20-41-08.ogg satnogs_2901793_2020-09-28T20-41-08.wav
# $ gr_satellites 'AmicalSat' --wavfile satnogs_2901793_2020-09-28T20-41-08.wav --samp_rate 48e3 --kiss_out satnogs_2901793_2020-09-28T20-41-08.kiss --start_time "2020-09-28 20:41:08" --throttle
# $ ./show_kiss.py satnogs_2901793_2020-09-28T20-41-08.kiss data_

# Copyright 2020 Fabian Schmidt <kerel+satnogs at mailbox.org>
# SPDX-License-Identifier: GPL-3.0-or-later
# Mod by SA2KNG


import argparse
import struct

from binascii import hexlify
from datetime import datetime, timedelta


# Define KISS Special Codes
# http://www.ax25.net/kiss.aspx
FEND = b'\xc0'
FESC = b'\xdb'
TFEND = b'\xdc'
TFESC = b'\xdd'


def kiss_unescape(escaped_frame):
    return escaped_frame.replace(
        FESC + TFEND,
        FEND
    ).replace(
        FESC + TFESC,
        FESC
    )


def read_kiss_frames(kiss_file):
    parts = kiss_file.read().split(FEND)

    # Check that content starts with FEND byte (First Frame start)
    assert(parts[0] == b'')

    # Check that content is composed of (empty, timestamp, empty, frame_content)-frame tuples
    parts_len = len(parts)
    assert((parts_len - 1) % 4 == 0)

    frames_len = (parts_len - 1) // 4

    for i in range(0, frames_len):
        timestamp_raw = parts[i * 4 + 1]
        escaped_frame = parts[i * 4 + 3]

        # Make sure this is a KISS control frame (type = b'\x09')
        assert(timestamp_raw[0] == 9)
        # Make sure this is a data frame (type = b'\x00')
        assert(escaped_frame[0] == 0)

        timestamp_int, = struct.unpack('>Q', kiss_unescape(timestamp_raw[1:]))
        epoch = datetime(1970, 1, 1)
        timestamp = epoch + timedelta(seconds=timestamp_int // 1000)

        yield timestamp, kiss_unescape(escaped_frame[1:])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read "gr_satellites-formatted" KISS frames and output the timestamp and data.')
    parser.add_argument('KISS_IN', type=str,
                        help='Input KISS File.')
    parser.add_argument('DATAPATH', type=str,
                        help='Output data path, timestamp will be added')

    args = parser.parse_args()

    with open(args.KISS_IN, 'rb') as kiss_file:
        frame_tuples = list(read_kiss_frames(kiss_file))

    for (timestamp, frame) in frame_tuples:
        datafile = args.DATAPATH + timestamp.strftime("%Y-%m-%dT%H-%M-%S")
        #print(datafile)
        with open(datafile, 'wb') as df:
            df.write(frame)
        # print('{}'.format(timestamp))
        # print('{}:\n{}\n'.format(timestamp,  hexlify(frame).decode('latin-1')))

    print('Found {} frames.'.format(len(frame_tuples)))
