#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: satnogs raw to udp
# Author: sa2kng, some parts from satnogs_bpsk
# Description: replay iq.raw files to udp audio/iq
# GNU Radio version: 3.8.2.0

from gnuradio import analog
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
import math
import satnogs


class satnogs_raw_to_udp(gr.top_block):

    def __init__(self, baudrate=1200.0, raw_file='', udp_IP="127.0.0.1", udp_port=7355):
        gr.top_block.__init__(self, "satnogs raw to udp")

        ##################################################
        # Parameters
        ##################################################
        self.baudrate = baudrate
        self.raw_file = raw_file
        self.udp_IP = udp_IP
        self.udp_port = udp_port

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.audio_samp_rate = audio_samp_rate = 48000
        self.decimation = decimation = satnogs.find_decimation(baudrate, 2, audio_samp_rate,sps)
        self.target_rate = target_rate = baudrate*decimation
        self.if_freq = if_freq = 12000

        ##################################################
        # Blocks
        ##################################################
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
            audio_samp_rate/(baudrate*decimation),
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
        self.blocks_udp_sink_0_0 = blocks.udp_sink(gr.sizeof_short*1, udp_IP, udp_port-1, 1472, True)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_short*1, udp_IP, udp_port, 1472, True)
        self.blocks_throttle_1 = blocks.throttle(gr.sizeof_gr_complex*1, baudrate*decimation,True)
        self.blocks_rotator_cc_0_0 = blocks.rotator_cc(2.0 * math.pi * (if_freq / audio_samp_rate))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/16768)
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_float*1, 1)
        self.blocks_float_to_short_1 = blocks.float_to_short(1, 32767.0)
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 32767.0)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, raw_file, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.analog_agc2_xx_0_0 = analog.agc2_cc(0.01, 0.001, 0.015, 1.0)
        self.analog_agc2_xx_0_0.set_max_gain(65536)
        self.analog_agc2_xx_0 = analog.agc2_cc(1e-3, 1e-3, 0.5, 1.0)
        self.analog_agc2_xx_0.set_max_gain(65536)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.analog_agc2_xx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.analog_agc2_xx_0_0, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_float_to_short_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.blocks_float_to_short_1, 0), (self.blocks_udp_sink_0_0, 0))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_float_to_short_1, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_rotator_cc_0_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_throttle_1, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_rotator_cc_0_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.analog_agc2_xx_0_0, 0))


    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        self.set_decimation(satnogs.find_decimation(self.baudrate, 2, self.audio_samp_rate,self.sps))
        self.set_target_rate(self.baudrate*self.decimation)
        self.blocks_throttle_1.set_sample_rate(self.baudrate*self.decimation)
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate/(self.baudrate*self.decimation))

    def get_raw_file(self):
        return self.raw_file

    def set_raw_file(self, raw_file):
        self.raw_file = raw_file
        self.blocks_file_source_0.open(self.raw_file, False)

    def get_udp_IP(self):
        return self.udp_IP

    def set_udp_IP(self, udp_IP):
        self.udp_IP = udp_IP

    def get_udp_port(self):
        return self.udp_port

    def set_udp_port(self, udp_port):
        self.udp_port = udp_port

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_decimation(satnogs.find_decimation(self.baudrate, 2, self.audio_samp_rate,self.sps))

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.set_decimation(satnogs.find_decimation(self.baudrate, 2, self.audio_samp_rate,self.sps))
        self.blocks_rotator_cc_0_0.set_phase_inc(2.0 * math.pi * (self.if_freq / self.audio_samp_rate))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.audio_samp_rate, 0.42*self.audio_samp_rate/2.0, 0.05 * self.audio_samp_rate, firdes.WIN_HAMMING, 6.76))
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate/(self.baudrate*self.decimation))

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_target_rate(self.baudrate*self.decimation)
        self.blocks_throttle_1.set_sample_rate(self.baudrate*self.decimation)
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate/(self.baudrate*self.decimation))

    def get_target_rate(self):
        return self.target_rate

    def set_target_rate(self, target_rate):
        self.target_rate = target_rate

    def get_if_freq(self):
        return self.if_freq

    def set_if_freq(self, if_freq):
        self.if_freq = if_freq
        self.blocks_rotator_cc_0_0.set_phase_inc(2.0 * math.pi * (self.if_freq / self.audio_samp_rate))




def argument_parser():
    description = 'replay iq.raw files to udp audio/iq'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--baudrate", dest="baudrate", type=eng_float, default="1.2k",
        help="Set baudrate [default=%(default)r]")
    parser.add_argument(
        "-f", "--raw-file", dest="raw_file", type=str, default='',
        help="Set raw_file [default=%(default)r]")
    parser.add_argument(
        "--udp-IP", dest="udp_IP", type=str, default="127.0.0.1",
        help="Set udp_IP [default=%(default)r]")
    parser.add_argument(
        "--udp-port", dest="udp_port", type=intx, default=7355,
        help="Set udp_port [default=%(default)r]")
    return parser


def main(top_block_cls=satnogs_raw_to_udp, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(baudrate=options.baudrate, raw_file=options.raw_file, udp_IP=options.udp_IP, udp_port=options.udp_port)

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
