#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: wav to iq raw
# Author: Daniel Ekman <knegge@gmail.com>
# Description: convert mono 48k wav/ogg to iq raw at 24k
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




class wav2iq_raw(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "wav to iq raw", catch_exceptions=True)

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
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_fcf(1, taps, (samp_rate // 4), samp_rate)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('observation.ogg', False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, 'observation..raw', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_wavfile_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_file_sink_0, 0))


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




def main(top_block_cls=wav2iq_raw, options=None):
    tb = top_block_cls()

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
