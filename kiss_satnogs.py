#!/usr/bin/env python3

# usage: kiss_satnogs.py [-h] [-d path] [-s] [-t] [-v] [-j] [-x] kiss-file
#
# Read "gr_satellites-formatted" KISS frames and output the timestamp and data.
#
# positional arguments:
#   kiss-file   Input KISS File.
#
# options:
#   -h, --help  show this help message and exit
#   -d path     Output data path, default: data_
#   -s          Show summary of the file
#   -t          Show timestamps and datalength
#   -v          Add verbosity or hexlify
#   -j          Output JSON PDU format instead of binary
#   -x          Output GetKISS+ format instead of binary

# Example:
# $ wget https://ia601407.us.archive.org/31/items/satnogs-observation-2901793/satnogs_2901793_2020-09-28T20-41-08.ogg
# $ sox satnogs_2901793_2020-09-28T20-41-08.ogg satnogs_2901793_2020-09-28T20-41-08.wav
# $ gr_satellites 'AmicalSat' --wavfile satnogs_2901793_2020-09-28T20-41-08.wav --samp_rate 48e3 \
# --kiss_out satnogs_2901793_2020-09-28T20-41-08.kiss --start_time "2020-09-28 20:41:08" --throttle
# $ ./kiss_satnogs.py satnogs_2901793_2020-09-28T20-41-08.kiss -t

# Copyright 2020 Fabian Schmidt <kerel+satnogs at mailbox.org>
# Extended by SA2KNG <knegge at gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later


import argparse
import struct
import base64
import json

from os import path
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


def read_kiss_frames(kf):
    parts = kf.read().split(FEND)

    # Check that content starts with FEND byte (First Frame start)
    assert (parts[0] == b''), 'does not begin with frame start'

    # Check that content is composed of (empty, timestamp, empty, frame_content)-frame tuples
    parts_len = len(parts)
    assert ((parts_len - 1) % 2 == 0), 'does not contain even number of frame tuples'

    frames_len = (parts_len - 1) // 2

    timestamp_raw = None
    for i in range(0, frames_len):
        if parts[i * 2 + 1][0] == 9:
            timestamp_raw = parts[i * 2 + 1]
            continue
        escaped_frame = parts[i * 2 + 1]

        # Make sure this is a time frame (type = b'\x09')
        assert (timestamp_raw[0] == 9), 'timestamp is not type 9'
        # Make sure this is a data frame (type = b'\x00')
        assert (escaped_frame[0] == 0), 'data is not type 0'

        timestamp_int, = struct.unpack('>Q', kiss_unescape(timestamp_raw[1:]))
        epoch = datetime(1970, 1, 1)
        timestamp_e = epoch + timedelta(seconds=timestamp_int // 1000)

        yield timestamp_e, kiss_unescape(escaped_frame[1:])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read "gr_satellites-formatted" KISS frames'
                                                 ' and output the timestamp and data.')
    parser.add_argument('i', metavar='kiss-file', type=argparse.FileType('rb'), help='Input KISS File.')
    parser.add_argument('-d', metavar='path', type=str, default='data_', help='Output data path, default: %(default)s')
    parser.add_argument('-v', action='store_true', help='Add verbosity or hexlify')
    gr1 = parser.add_mutually_exclusive_group()
    gr1.add_argument('-s', action='store_true', help='Show summary of the file')
    gr1.add_argument('-t', action='store_true', help='Show timestamps and datalength')
    gr1.add_argument('-j', action='store_true', help='Output JSON PDU format instead of binary')
    gr1.add_argument('-x', action='store_true', help='Output GetKISS+ format instead of binary')
    args = parser.parse_args()

    try:
        frame_tuples = list(read_kiss_frames(args.i))
    except AssertionError as e:
        frame_tuples = 0
        print('ERROR: KISS file inconsistent: {}'.format(e))
        exit(1)

    if args.s:
        framelen = 0
        ts = 0
        for (timestamp, frame) in frame_tuples:
            framelen += len(frame)
            if ts == 0:
                ts = timestamp
        print('{}: Found {} frames, total data {}, first timestamp {}'.format(args.i.name, len(frame_tuples),
                                                                              framelen, ts))

    elif args.t:
        for (timestamp, frame) in frame_tuples:
            print('{} len: {}'.format(timestamp, len(frame)))
            if args.v:
                print('{}:\n{}\n'.format(timestamp, hexlify(frame).decode('latin-1')))
        print('{}: Found {} frames.'.format(args.i.name, len(frame_tuples)))

    elif args.x:
        datafile = args.d + '.txt'
        outfile = open(datafile, 'w')
        if args.v:
            print('Output file: {}'.format(datafile))
        for (timestamp, frame) in frame_tuples:
            if len(frame) == 0:
                continue
            outfile.write('{} | len: {} | {}\n'.format(timestamp.strftime('%Y-%m-%d %H:%M:%S'), len(frame),
                                                       hexlify(frame).decode('ascii').upper()))

    else:
        for (timestamp, frame) in frame_tuples:
            datafile = args.d + timestamp.strftime("%Y-%m-%dT%H-%M-%S_g")
            ext = 0
            if len(frame) == 0:
                continue
            while True:
                if path.isfile(datafile+str(ext)):
                    ext += 1
                else:
                    datafile += str(ext)
                    break
            if args.v:
                print('Output file: {}'.format(datafile))
            if args.j:
                data = {'decoder_name': 'gr-satellites',
                        'pdu': base64.b64encode(frame).decode()}
                with open(datafile, 'w') as df:
                    json.dump(data, df, default=str)
            else:
                with open(datafile, 'wb') as df:
                    df.write(frame)
        if args.v:
            print('{}: Wrote {} frames.'.format(args.i.name, len(frame_tuples)))
