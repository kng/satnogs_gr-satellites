#!/usr/bin/env python3
# Made by sa2kng <knegge@gmail.com>

from binascii import hexlify
from datetime import datetime, timedelta
from io import BytesIO
from os import path
import struct
from sys import argv


def main():
    if len(argv) != 3:
        print(f'Useage: {path.basename(argv[0])} <infile> <outprefix>\n'
              'Process KISS from Geoscan-Edelveis to image for SatNOGS.\n')
        exit(1)

    try:
        with open(argv[1], 'rb') as kf:
            frame_tuples = list(read_kiss_frames(kf))
    except AssertionError as e:
        print('ERROR: KISS file inconsistent: {}'.format(e))
        exit(2)

    frames = []
    ts = datetime.now()
    for (timestamp, frame) in frame_tuples:
        if len(frame) == 64:
            frames.append(hexlify(frame).decode('ascii').upper())
            if timestamp < ts:
                ts = timestamp

    if len(frames) < 100:
        print('Too little data to produce image')
        exit(3)

    image = BytesIO()
    for row in frames:
        cmd = row[0:4]
        addr = int((row[12:14] + row[10:12]), 16) % 32768
        dlen = (int(row[4:6], 16) + 2) * 2
        payload = row[16:dlen]
        if cmd == '0100':
            image.seek(addr)
            image.write(bytes.fromhex(payload))

    image.seek(0)
    if image.read(3) != b'\xff\xd8\xff':
        print('Wrong image beginning')
        exit(4)

    with open(argv[2] + ts.strftime("%Y-%m-%dT%H-%M-%S") + '.jpg', 'wb') as f:
        f.write(image.getbuffer().tobytes())


# kiss functions:
# Copyright 2020 Fabian Schmidt <kerel+satnogs at mailbox.org>
# Extended by SA2KNG <knegge at gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

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
    main()
