#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: wav to iq
# Author: Daniel Ekman <knegge@gmail.com>
# Description: convert mono 48k wav to raw/iq at 24k
# GNU Radio version: 3.10.4.0

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation




class wav2iq(gr.top_block):

    def __init__(self, infile='recording.wav', outfile='recording.raw'):
        gr.top_block.__init__(self, "wav to iq", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.infile = infile
        self.outfile = outfile

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 48e3
        self.filter_transition = filter_transition = 2e3
        self.filter_cutoff = filter_cutoff = samp_rate // 4
        self.taps = taps = firdes.low_pass(1, samp_rate, filter_cutoff, filter_transition)

        ##################################################
        # Blocks
        ##################################################
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_fcf(2, taps, (samp_rate // 4), samp_rate)
        self.blocks_wavfile_source_0 = blocks.wavfile_source(infile, False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, outfile, False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_wavfile_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_file_sink_0, 0))


    def get_infile(self):
        return self.infile

    def set_infile(self, infile):
        self.infile = infile

    def get_outfile(self):
        return self.outfile

    def set_outfile(self, outfile):
        self.outfile = outfile
        self.blocks_file_sink_0.open(self.outfile)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_filter_cutoff(self.samp_rate // 4)
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.filter_cutoff, self.filter_transition))
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((self.samp_rate // 4))

    def get_filter_transition(self):
        return self.filter_transition

    def set_filter_transition(self, filter_transition):
        self.filter_transition = filter_transition
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.filter_cutoff, self.filter_transition))

    def get_filter_cutoff(self):
        return self.filter_cutoff

    def set_filter_cutoff(self, filter_cutoff):
        self.filter_cutoff = filter_cutoff
        self.set_taps(firdes.low_pass(1, self.samp_rate, self.filter_cutoff, self.filter_transition))

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.taps)



def argument_parser():
    description = 'convert mono 48k wav to raw/iq at 24k'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-i", "--infile", dest="infile", type=str, default='recording.wav',
        help="Set input [default=%(default)r]")
    parser.add_argument(
        "-o", "--outfile", dest="outfile", type=str, default='recording.raw',
        help="Set output [default=%(default)r]")
    return parser


def main(top_block_cls=wav2iq, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(infile=options.infile, outfile=options.outfile)

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
