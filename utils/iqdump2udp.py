#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SatNOGS IQ dump to UDP IQ
# Author: sa2kng, some parts from satnogs_bpsk
# Description: replay iq.raw files to udp iq. Example use with: gr_satellites <sat> --samp_rate  48000 --iq --udp --udp_raw --udp_port 57356
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


class iqdump2udp(gr.top_block):

    def __init__(self, raw_file='', samp_rate='48000', udp_dump_host="127.0.0.1", udp_dump_port=57356):
        gr.top_block.__init__(self, "SatNOGS IQ dump to UDP IQ")

        ##################################################
        # Parameters
        ##################################################
        self.raw_file = raw_file
        self.samp_rate = samp_rate
        self.udp_dump_host = udp_dump_host
        self.udp_dump_port = udp_dump_port

        ##################################################
        # Blocks
        ##################################################
        self.blocks_udp_sink_0_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, udp_dump_host, udp_dump_port, 1472, True)
        self.blocks_throttle_1 = blocks.throttle(gr.sizeof_gr_complex*1, int(samp_rate),True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/16768)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, raw_file, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_throttle_1, 0), (self.blocks_udp_sink_0_0_0, 0))


    def get_raw_file(self):
        return self.raw_file

    def set_raw_file(self, raw_file):
        self.raw_file = raw_file
        self.blocks_file_source_0.open(self.raw_file, False)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_1.set_sample_rate(int(self.samp_rate))

    def get_udp_dump_host(self):
        return self.udp_dump_host

    def set_udp_dump_host(self, udp_dump_host):
        self.udp_dump_host = udp_dump_host

    def get_udp_dump_port(self):
        return self.udp_dump_port

    def set_udp_dump_port(self, udp_dump_port):
        self.udp_dump_port = udp_dump_port




def argument_parser():
    description = 'replay iq.raw files to udp iq. Example use with: gr_satellites <sat> --samp_rate  48000 --iq --udp --udp_raw --udp_port 57356'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-f", "--raw-file", dest="raw_file", type=str, default='',
        help="Set Input file from satnogs iq dump [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=str, default='48000',
        help="Set sample rate [default=%(default)r]")
    parser.add_argument(
        "-u", "--udp-dump-host", dest="udp_dump_host", type=str, default="127.0.0.1",
        help="Set host/ip to bind udp sink [default=%(default)r]")
    parser.add_argument(
        "-p", "--udp-dump-port", dest="udp_dump_port", type=intx, default=57356,
        help="Set host port for udp sink [default=%(default)r]")
    return parser


def main(top_block_cls=iqdump2udp, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(raw_file=options.raw_file, samp_rate=options.samp_rate, udp_dump_host=options.udp_dump_host, udp_dump_port=options.udp_dump_port)

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
