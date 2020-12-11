#!/bin/bash
FREQ=145917000
FILE=/tmp/rec
set -a
source /etc/default/satnogs-client

#/usr/bin/satnogs_bpsk.py --soapy-rx-device=$SATNOGS_SOAPY_RX_DEVICE --samp-rate-rx=$SATNOGS_RX_SAMP_RATE --rx-freq=$FREQ --file-path=$FILE.out --waterfall-file-path=$FILE.dat --decoded-data-file-path=$FILE.dec --gain=$SATNOGS_RF_GAIN --antenna=$SATNOGS_ANTENNA
/usr/bin/satnogs_fsk.py --soapy-rx-device=$SATNOGS_SOAPY_RX_DEVICE --samp-rate-rx=$SATNOGS_RX_SAMP_RATE --rx-freq=$FREQ --file-path=$FILE.out --waterfall-file-path=$FILE.dat --decoded-data-file-path=$FILE.dec --gain=$SATNOGS_RF_GAIN --antenna=$SATNOGS_ANTENNA

