#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: NOAA APT Decoder
# Author: Manolis Surligas, George Vardakis
# Description: A NOAA APT Decoder with automatic image synchronization
# GNU Radio version: 3.8.2.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.filter import pfb
import satnogs
import soapy
import distutils
from distutils import util


class satnogs_noaa_apt_decoder(gr.top_block):

    def __init__(self, antenna="", bb_freq=0.0, bw=0.0, dc_removal="False", decoded_data_file_path="/tmp/.satnogs/data/data", dev_args="", doppler_correction_per_sec=20, enable_iq_dump=0, file_path="test.wav", flip_images=0, gain=0.0, gain_mode="Overall", iq_file_path="/tmp/iq.dat", lo_offset=100e3, other_settings="", ppm=0, rigctl_port=4532, rx_freq=100e6, samp_rate_rx=0.0, soapy_rx_device="driver=invalid", stream_args="", sync=1, tune_args="", udp_IP="127.0.0.1", udp_dump_dest='127.0.0.1', udp_dump_port=7355, udp_port=16887, waterfall_file_path="/tmp/waterfall.dat"):
        gr.top_block.__init__(self, "NOAA APT Decoder")

        ##################################################
        # Parameters
        ##################################################
        self.antenna = antenna
        self.bb_freq = bb_freq
        self.bw = bw
        self.dc_removal = dc_removal
        self.decoded_data_file_path = decoded_data_file_path
        self.dev_args = dev_args
        self.doppler_correction_per_sec = doppler_correction_per_sec
        self.enable_iq_dump = enable_iq_dump
        self.file_path = file_path
        self.flip_images = flip_images
        self.gain = gain
        self.gain_mode = gain_mode
        self.iq_file_path = iq_file_path
        self.lo_offset = lo_offset
        self.other_settings = other_settings
        self.ppm = ppm
        self.rigctl_port = rigctl_port
        self.rx_freq = rx_freq
        self.samp_rate_rx = samp_rate_rx
        self.soapy_rx_device = soapy_rx_device
        self.stream_args = stream_args
        self.sync = sync
        self.tune_args = tune_args
        self.udp_IP = udp_IP
        self.udp_dump_dest = udp_dump_dest
        self.udp_dump_port = udp_dump_port
        self.udp_port = udp_port
        self.waterfall_file_path = waterfall_file_path

        ##################################################
        # Variables
        ##################################################
        self.audio_samp_rate = audio_samp_rate = 48000

        ##################################################
        # Blocks
        ##################################################
        self.soapy_source_0_0 = None
        # Make sure that the gain mode is valid
        if(gain_mode not in ['Overall', 'Specific', 'Settings Field']):
            raise ValueError("Wrong gain mode on channel 0. Allowed gain modes: "
                  "['Overall', 'Specific', 'Settings Field']")

        dev = soapy_rx_device

        # Stream arguments for every activated stream
        tune_args = [tune_args]
        settings = [other_settings]

        # Setup the device arguments
        dev_args = dev_args

        self.soapy_source_0_0 = soapy.source(1, dev, dev_args, stream_args,
                                  tune_args, settings, samp_rate_rx, "fc32")



        self.soapy_source_0_0.set_dc_removal(0,bool(distutils.util.strtobool(dc_removal)))

        # Set up DC offset. If set to (0, 0) internally the source block
        # will handle the case if no DC offset correction is supported
        self.soapy_source_0_0.set_dc_offset(0,0)

        # Setup IQ Balance. If set to (0, 0) internally the source block
        # will handle the case if no IQ balance correction is supported
        self.soapy_source_0_0.set_iq_balance(0,0)

        self.soapy_source_0_0.set_agc(0,False)

        # generic frequency setting should be specified first
        self.soapy_source_0_0.set_frequency(0, rx_freq - lo_offset)

        self.soapy_source_0_0.set_frequency(0,"BB",bb_freq)

        # Setup Frequency correction. If set to 0 internally the source block
        # will handle the case if no frequency correction is supported
        self.soapy_source_0_0.set_frequency_correction(0,ppm)

        self.soapy_source_0_0.set_antenna(0,antenna)

        self.soapy_source_0_0.set_bandwidth(0,bw)

        if(gain_mode != 'Settings Field'):
            # pass is needed, in case the template does not evaluare anything
            pass
            self.soapy_source_0_0.set_gain(0,gain)
        self.satnogs_waterfall_sink_0_0 = satnogs.waterfall_sink(4*4160*4, rx_freq, 10, 1024, waterfall_file_path, 1)
        self.satnogs_tcp_rigctl_msg_source_0 = satnogs.tcp_rigctl_msg_source("127.0.0.1", rigctl_port, False, int(1000.0/doppler_correction_per_sec) + 1, 1500)
        self.satnogs_ogg_encoder_0 = satnogs.ogg_encoder(file_path, audio_samp_rate, 0.8)
        self.satnogs_noaa_apt_sink_1 = satnogs.noaa_apt_sink(decoded_data_file_path, 2080, 1800, True, False)
        self.satnogs_iq_sink_0_0 = satnogs.iq_sink(16768, iq_file_path, False, enable_iq_dump)
        self.satnogs_doppler_compensation_0 = satnogs.doppler_compensation(samp_rate_rx, rx_freq, lo_offset, 4*4160*4, 1, 0)
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=4,
                taps=None,
                fractional_bw=None)
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_fff(
            audio_samp_rate / (4*4160*4),
            taps=None,
            flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                4*4160*4,
                4*4160*1.1,
                1e3,
                firdes.WIN_HAMMING,
                6.76))
        self.hilbert_fc_0 = filter.hilbert_fc(65, firdes.WIN_HAMMING, 6.76)
        self.blocks_udp_sink_0_0 = blocks.udp_sink(gr.sizeof_gr_complex*1, udp_dump_dest, udp_dump_port+1, 1472, True)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_short*1, udp_dump_dest, udp_dump_port, 1472, True)
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 16383.0)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.band_pass_filter_0 = filter.fir_filter_fff(
            4,
            firdes.band_pass(
                1,
                (4*4160*4 ),
                500,
                4.2e3,
                200,
                firdes.WIN_HAMMING,
                6.76))
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=4*4160*4,
        	audio_decimation=1,
        )



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.satnogs_tcp_rigctl_msg_source_0, 'freq'), (self.satnogs_doppler_compensation_0, 'doppler'))
        self.connect((self.analog_wfm_rcv_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.hilbert_fc_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.blocks_float_to_short_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.hilbert_fc_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.satnogs_ogg_encoder_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.satnogs_noaa_apt_sink_1, 0))
        self.connect((self.satnogs_doppler_compensation_0, 0), (self.blocks_udp_sink_0_0, 0))
        self.connect((self.satnogs_doppler_compensation_0, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.satnogs_doppler_compensation_0, 0), (self.satnogs_iq_sink_0_0, 0))
        self.connect((self.satnogs_doppler_compensation_0, 0), (self.satnogs_waterfall_sink_0_0, 0))
        self.connect((self.soapy_source_0_0, 0), (self.satnogs_doppler_compensation_0, 0))


    def get_antenna(self):
        return self.antenna

    def set_antenna(self, antenna):
        self.antenna = antenna
        self.soapy_source_0_0.set_antenna(0,self.antenna)

    def get_bb_freq(self):
        return self.bb_freq

    def set_bb_freq(self, bb_freq):
        self.bb_freq = bb_freq
        self.soapy_source_0_0.set_frequency(0,"BB",self.bb_freq)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.soapy_source_0_0.set_bandwidth(0,self.bw)

    def get_dc_removal(self):
        return self.dc_removal

    def set_dc_removal(self, dc_removal):
        self.dc_removal = dc_removal
        self.soapy_source_0_0.set_dc_removal(0,bool(distutils.util.strtobool(self.dc_removal)))

    def get_decoded_data_file_path(self):
        return self.decoded_data_file_path

    def set_decoded_data_file_path(self, decoded_data_file_path):
        self.decoded_data_file_path = decoded_data_file_path

    def get_dev_args(self):
        return self.dev_args

    def set_dev_args(self, dev_args):
        self.dev_args = dev_args

    def get_doppler_correction_per_sec(self):
        return self.doppler_correction_per_sec

    def set_doppler_correction_per_sec(self, doppler_correction_per_sec):
        self.doppler_correction_per_sec = doppler_correction_per_sec

    def get_enable_iq_dump(self):
        return self.enable_iq_dump

    def set_enable_iq_dump(self, enable_iq_dump):
        self.enable_iq_dump = enable_iq_dump

    def get_file_path(self):
        return self.file_path

    def set_file_path(self, file_path):
        self.file_path = file_path

    def get_flip_images(self):
        return self.flip_images

    def set_flip_images(self, flip_images):
        self.flip_images = flip_images

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.soapy_source_0_0.set_gain(0, self.gain)

    def get_gain_mode(self):
        return self.gain_mode

    def set_gain_mode(self, gain_mode):
        self.gain_mode = gain_mode

    def get_iq_file_path(self):
        return self.iq_file_path

    def set_iq_file_path(self, iq_file_path):
        self.iq_file_path = iq_file_path

    def get_lo_offset(self):
        return self.lo_offset

    def set_lo_offset(self, lo_offset):
        self.lo_offset = lo_offset
        self.soapy_source_0_0.set_frequency(0, self.rx_freq - self.lo_offset)

    def get_other_settings(self):
        return self.other_settings

    def set_other_settings(self, other_settings):
        self.other_settings = other_settings

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm
        self.soapy_source_0_0.set_frequency_correction(0,self.ppm)

    def get_rigctl_port(self):
        return self.rigctl_port

    def set_rigctl_port(self, rigctl_port):
        self.rigctl_port = rigctl_port

    def get_rx_freq(self):
        return self.rx_freq

    def set_rx_freq(self, rx_freq):
        self.rx_freq = rx_freq
        self.soapy_source_0_0.set_frequency(0, self.rx_freq - self.lo_offset)

    def get_samp_rate_rx(self):
        return self.samp_rate_rx

    def set_samp_rate_rx(self, samp_rate_rx):
        self.samp_rate_rx = samp_rate_rx

    def get_soapy_rx_device(self):
        return self.soapy_rx_device

    def set_soapy_rx_device(self, soapy_rx_device):
        self.soapy_rx_device = soapy_rx_device

    def get_stream_args(self):
        return self.stream_args

    def set_stream_args(self, stream_args):
        self.stream_args = stream_args

    def get_sync(self):
        return self.sync

    def set_sync(self, sync):
        self.sync = sync

    def get_tune_args(self):
        return self.tune_args

    def set_tune_args(self, tune_args):
        self.tune_args = tune_args

    def get_udp_IP(self):
        return self.udp_IP

    def set_udp_IP(self, udp_IP):
        self.udp_IP = udp_IP

    def get_udp_dump_dest(self):
        return self.udp_dump_dest

    def set_udp_dump_dest(self, udp_dump_dest):
        self.udp_dump_dest = udp_dump_dest

    def get_udp_dump_port(self):
        return self.udp_dump_port

    def set_udp_dump_port(self, udp_dump_port):
        self.udp_dump_port = udp_dump_port

    def get_udp_port(self):
        return self.udp_port

    def set_udp_port(self, udp_port):
        self.udp_port = udp_port

    def get_waterfall_file_path(self):
        return self.waterfall_file_path

    def set_waterfall_file_path(self, waterfall_file_path):
        self.waterfall_file_path = waterfall_file_path

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate
        self.pfb_arb_resampler_xxx_0.set_rate(self.audio_samp_rate / (4*4160*4))




def argument_parser():
    description = 'A NOAA APT Decoder with automatic image synchronization'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--antenna", dest="antenna", type=str, default="",
        help="Set antenna [default=%(default)r]")
    parser.add_argument(
        "--bb-freq", dest="bb_freq", type=eng_float, default="0.0",
        help="Set Baseband CORDIC frequency (if the device supports it) [default=%(default)r]")
    parser.add_argument(
        "--bw", dest="bw", type=eng_float, default="0.0",
        help="Set Bandwidth [default=%(default)r]")
    parser.add_argument(
        "--dc-removal", dest="dc_removal", type=str, default="False",
        help="Set Remove automatically the DC offset (if the device support it) [default=%(default)r]")
    parser.add_argument(
        "--decoded-data-file-path", dest="decoded_data_file_path", type=str, default="/tmp/.satnogs/data/data",
        help="Set decoded_data_file_path [default=%(default)r]")
    parser.add_argument(
        "--dev-args", dest="dev_args", type=str, default="",
        help="Set Device arguments [default=%(default)r]")
    parser.add_argument(
        "--doppler-correction-per-sec", dest="doppler_correction_per_sec", type=intx, default=20,
        help="Set doppler_correction_per_sec [default=%(default)r]")
    parser.add_argument(
        "--enable-iq-dump", dest="enable_iq_dump", type=intx, default=0,
        help="Set enable_iq_dump [default=%(default)r]")
    parser.add_argument(
        "--file-path", dest="file_path", type=str, default="test.wav",
        help="Set file_path [default=%(default)r]")
    parser.add_argument(
        "--flip-images", dest="flip_images", type=intx, default=0,
        help="Set flip_images [default=%(default)r]")
    parser.add_argument(
        "--gain", dest="gain", type=eng_float, default="0.0",
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--gain-mode", dest="gain_mode", type=str, default="Overall",
        help="Set gain_mode [default=%(default)r]")
    parser.add_argument(
        "--iq-file-path", dest="iq_file_path", type=str, default="/tmp/iq.dat",
        help="Set iq_file_path [default=%(default)r]")
    parser.add_argument(
        "--lo-offset", dest="lo_offset", type=eng_float, default="100.0k",
        help="Set lo_offset [default=%(default)r]")
    parser.add_argument(
        "--other-settings", dest="other_settings", type=str, default="",
        help="Set Soapy Channel other settings [default=%(default)r]")
    parser.add_argument(
        "--ppm", dest="ppm", type=eng_float, default="0.0",
        help="Set ppm [default=%(default)r]")
    parser.add_argument(
        "--rigctl-port", dest="rigctl_port", type=intx, default=4532,
        help="Set rigctl_port [default=%(default)r]")
    parser.add_argument(
        "--rx-freq", dest="rx_freq", type=eng_float, default="100.0M",
        help="Set rx_freq [default=%(default)r]")
    parser.add_argument(
        "--samp-rate-rx", dest="samp_rate_rx", type=eng_float, default="0.0",
        help="Set Device Sampling rate [default=%(default)r]")
    parser.add_argument(
        "--soapy-rx-device", dest="soapy_rx_device", type=str, default="driver=invalid",
        help="Set soapy_rx_device [default=%(default)r]")
    parser.add_argument(
        "--stream-args", dest="stream_args", type=str, default="",
        help="Set Soapy Stream arguments [default=%(default)r]")
    parser.add_argument(
        "--sync", dest="sync", type=intx, default=1,
        help="Set sync [default=%(default)r]")
    parser.add_argument(
        "--tune-args", dest="tune_args", type=str, default="",
        help="Set Soapy Channel Tune arguments [default=%(default)r]")
    parser.add_argument(
        "--udp-IP", dest="udp_IP", type=str, default="127.0.0.1",
        help="Set udp_IP [default=%(default)r]")
    parser.add_argument(
        "--udp-dump-dest", dest="udp_dump_dest", type=str, default='127.0.0.1',
        help="Set udp_dump_dest [default=%(default)r]")
    parser.add_argument(
        "--udp-dump-port", dest="udp_dump_port", type=intx, default=7355,
        help="Set udp_dump_port [default=%(default)r]")
    parser.add_argument(
        "--udp-port", dest="udp_port", type=intx, default=16887,
        help="Set udp_port [default=%(default)r]")
    parser.add_argument(
        "--waterfall-file-path", dest="waterfall_file_path", type=str, default="/tmp/waterfall.dat",
        help="Set waterfall_file_path [default=%(default)r]")
    return parser


def main(top_block_cls=satnogs_noaa_apt_decoder, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(antenna=options.antenna, bb_freq=options.bb_freq, bw=options.bw, dc_removal=options.dc_removal, decoded_data_file_path=options.decoded_data_file_path, dev_args=options.dev_args, doppler_correction_per_sec=options.doppler_correction_per_sec, enable_iq_dump=options.enable_iq_dump, file_path=options.file_path, flip_images=options.flip_images, gain=options.gain, gain_mode=options.gain_mode, iq_file_path=options.iq_file_path, lo_offset=options.lo_offset, other_settings=options.other_settings, ppm=options.ppm, rigctl_port=options.rigctl_port, rx_freq=options.rx_freq, samp_rate_rx=options.samp_rate_rx, soapy_rx_device=options.soapy_rx_device, stream_args=options.stream_args, sync=options.sync, tune_args=options.tune_args, udp_IP=options.udp_IP, udp_dump_dest=options.udp_dump_dest, udp_dump_port=options.udp_dump_port, udp_port=options.udp_port, waterfall_file_path=options.waterfall_file_path)

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
