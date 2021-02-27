#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: satnogs raw int16 to complex
# Author: sa2kng
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation


class rawint2complex(gr.top_block):

    def __init__(self, out_file='', raw_file=''):
        gr.top_block.__init__(self, "satnogs raw int16 to complex")

        ##################################################
        # Parameters
        ##################################################
        self.out_file = out_file
        self.raw_file = raw_file

        ##################################################
        # Blocks
        ##################################################
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/16768)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, raw_file, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, out_file, False)
        self.blocks_file_sink_0.set_unbuffered(False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_file_sink_0, 0))


    def get_out_file(self):
        return self.out_file

    def set_out_file(self, out_file):
        self.out_file = out_file
        self.blocks_file_sink_0.open(self.out_file)

    def get_raw_file(self):
        return self.raw_file

    def set_raw_file(self, raw_file):
        self.raw_file = raw_file
        self.blocks_file_source_0.open(self.raw_file, False)




def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-o", "--out-file", dest="out_file", type=str, default='',
        help="Set out_file [default=%(default)r]")
    parser.add_argument(
        "-f", "--raw-file", dest="raw_file", type=str, default='',
        help="Set raw_file [default=%(default)r]")
    return parser


def main(top_block_cls=rawint2complex, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(out_file=options.out_file, raw_file=options.raw_file)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
