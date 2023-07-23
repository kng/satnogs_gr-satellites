#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SatNOGS IQ dump to UDP IQ and audio
# Author: sa2kng, some parts from satnogs_bpsk and satnogs_fm
# Description: replay iq.raw files to udp iq. Example use with: gr_satellites <sat> --samp_rate  48000 --iq --udp --udp_raw --udp_port 57356
# GNU Radio version: 3.8.2.0

from gnuradio import analog
import math
from gnuradio import blocks
import pmt
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.filter import pfb


class iqdump2udp_audio(gr.top_block):

    def __init__(self, audio_samp_rate=48000, deviation=5e3, if_freq=12000, max_modulation_freq=3e3, raw_file='', samp_rate=48000, udp_dump_host="127.0.0.1", udp_dump_port=57356):
        gr.top_block.__init__(self, "SatNOGS IQ dump to UDP IQ and audio")

        ##################################################
        # Parameters
        ##################################################
        self.audio_samp_rate = audio_samp_rate
        self.deviation = deviation
        self.if_freq = if_freq
        self.max_modulation_freq = max_modulation_freq
        self.raw_file = raw_file
        self.samp_rate = samp_rate
        self.udp_dump_host = udp_dump_host
        self.udp_dump_port = udp_dump_port

        ##################################################
        # Blocks
        ##################################################
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
            audio_samp_rate/samp_rate,
            taps=None,
            flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                audio_samp_rate,
                0.42*audio_samp_rate/2.0,
                0.05 * audio_samp_rate,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                audio_samp_rate,
                deviation+max_modulation_freq,
                1000,
                firdes.WIN_HAMMING,
                6.76))
        self.dc_blocker_xx_0_0 = filter.dc_blocker_ff(1024, True)
        self.blocks_udp_sink_0_0_0_0_0 = blocks.udp_sink(gr.sizeof_short*1, udp_dump_host, udp_dump_port+2, 1472, True)
        self.blocks_udp_sink_0_0_0_0 = blocks.udp_sink(gr.sizeof_short*1, udp_dump_host, udp_dump_port+1, 1472, True)
        self.blocks_udp_sink_0_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, udp_dump_host, udp_dump_port, 1472, True)
        self.blocks_throttle_1 = blocks.throttle(gr.sizeof_gr_complex*1, int(samp_rate),True)
        self.blocks_rotator_cc_0_0 = blocks.rotator_cc(2.0 * math.pi * (if_freq / audio_samp_rate))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/16768)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False)
        self.blocks_float_to_short_0_0 = blocks.float_to_short(1, 16384)
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 16384)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, raw_file, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((2*math.pi*deviation)/audio_samp_rate)
        self.analog_agc2_xx_0_0 = analog.agc2_cc(0.01, 0.001, 0.015, 1.0)
        self.analog_agc2_xx_0_0.set_max_gain(65536)
        self.analog_agc2_xx_0 = analog.agc2_cc(1e-3, 1e-3, 0.5, 1.0)
        self.analog_agc2_xx_0.set_max_gain(65536)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.analog_agc2_xx_0_0, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.dc_blocker_xx_0_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_float_to_short_0, 0), (self.blocks_udp_sink_0_0_0_0, 0))
        self.connect((self.blocks_float_to_short_0_0, 0), (self.blocks_udp_sink_0_0_0_0_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_rotator_cc_0_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_throttle_1, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.blocks_throttle_1, 0), (self.blocks_udp_sink_0_0_0, 0))
        self.connect((self.blocks_throttle_1, 0), (self.low_pass_filter_0, 0))
        self.connect((self.dc_blocker_xx_0_0, 0), (self.blocks_float_to_short_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_rotator_cc_0_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.analog_agc2_xx_0_0, 0))


    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.analog_quadrature_demod_cf_0.set_gain((2*math.pi*self.deviation)/self.audio_samp_rate)
        self.blocks_rotator_cc_0_0.set_phase_inc(2.0 * math.pi * (self.if_freq / self.audio_samp_rate))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.audio_samp_rate, self.deviation+self.max_modulation_freq, 1000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.audio_samp_rate, 0.42*self.audio_samp_rate/2.0, 0.05 * self.audio_samp_rate, firdes.WIN_HAMMING, 6.76))
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate/self.samp_rate)

    def get_deviation(self):
        return self.deviation

    def set_deviation(self, deviation):
        self.deviation = deviation
        self.analog_quadrature_demod_cf_0.set_gain((2*math.pi*self.deviation)/self.audio_samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.audio_samp_rate, self.deviation+self.max_modulation_freq, 1000, firdes.WIN_HAMMING, 6.76))

    def get_if_freq(self):
        return self.if_freq

    def set_if_freq(self, if_freq):
        self.if_freq = if_freq
        self.blocks_rotator_cc_0_0.set_phase_inc(2.0 * math.pi * (self.if_freq / self.audio_samp_rate))

    def get_max_modulation_freq(self):
        return self.max_modulation_freq

    def set_max_modulation_freq(self, max_modulation_freq):
        self.max_modulation_freq = max_modulation_freq
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.audio_samp_rate, self.deviation+self.max_modulation_freq, 1000, firdes.WIN_HAMMING, 6.76))

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
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate/self.samp_rate)

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
        "-a", "--audio-samp-rate", dest="audio_samp_rate", type=eng_float, default="48.0k",
        help="Set audio sample rate [default=%(default)r]")
    parser.add_argument(
        "--deviation", dest="deviation", type=eng_float, default="5.0k",
        help="Set FM deviation (Hz) [default=%(default)r]")
    parser.add_argument(
        "-i", "--if-freq", dest="if_freq", type=eng_float, default="12.0k",
        help="Set SSB IF frequency [default=%(default)r]")
    parser.add_argument(
        "--max-modulation-freq", dest="max_modulation_freq", type=eng_float, default="3.0k",
        help="Set The highest frequency in the FM modulating signal [default=%(default)r]")
    parser.add_argument(
        "-f", "--raw-file", dest="raw_file", type=str, default='',
        help="Set Input file from satnogs iq dump [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=eng_float, default="48.0k",
        help="Set sample rate [default=%(default)r]")
    parser.add_argument(
        "-u", "--udp-dump-host", dest="udp_dump_host", type=str, default="127.0.0.1",
        help="Set host/ip to bind udp sink [default=%(default)r]")
    parser.add_argument(
        "-p", "--udp-dump-port", dest="udp_dump_port", type=intx, default=57356,
        help="Set host port for udp sink [default=%(default)r]")
    return parser


def main(top_block_cls=iqdump2udp_audio, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(audio_samp_rate=options.audio_samp_rate, deviation=options.deviation, if_freq=options.if_freq, max_modulation_freq=options.max_modulation_freq, raw_file=options.raw_file, samp_rate=options.samp_rate, udp_dump_host=options.udp_dump_host, udp_dump_port=options.udp_dump_port)

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
