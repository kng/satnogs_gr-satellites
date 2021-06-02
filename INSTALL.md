Make sure to investigate if files already exists, versions changed, you already have pre/post-scripts etc. I will not be responsible for any problems so be careful when following this guide!<br>

## Prerequisites
Follow the instruction on https://gr-satellites.readthedocs.io/en/latest/installation.html<br>
The latest gr-satellites >=3.7.0-git with the --udp_raw and --ignore_unknown_args is required.<br>
Basically this, ymmv:
```
cd
sudo apt-get install swig liborc-0.4-0 python3-pip feh cmake
sudo pip3 install --upgrade construct requests
git clone -b maint-3.8 --depth=1 https://github.com/daniestevez/gr-satellites.git
cd gr-satellites
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

cd
git clone --depth=1 https://github.com/daniestevez/ssdv
cd ssdv
make
sudo make install
```

A simple check to see if gr_satellites is working is by executing: `gr_satellites --version`<br>
This should give an output similar to this (the version can be different):

```
gr_satellites v3.9.0-git
Copyright (C) 2020 Daniel Estevez
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

If you get the error: ModuleNotFoundError: No module named 'satellites'<br>
You can add this to `~/.bashrc` : `export PYTHONPATH=/usr/local/lib/python3/dist-packages/`<br>

## Download
Clone this repo and enter it:<br>
```
cd
git clone --depth=1 https://github.com/kng/satnogs_gr-satellites.git
cd satnogs_gr-satellites
```

## Installation (auto)
```
sudo apt-get install jq
sudo make install
```

## Installation (manual)
Make sure the individual programs work before you enable the automated process!<br>
These are required: `jq, gr_satellites, jy1sat_ssdv, ssdv, kiss_satnogs.py, find_samp_rate.py`<br>
Copy the grsat-wrapper.sh, kiss_satnogs.py, find_samp_rate.py, satnogs-pre and satnogs-post to /usr/local/bin<br>

```
sudo apt-get install jq
sudo cp grsat-wrapper.sh kiss_satnogs.py find_samp_rate.py satnogs-pre satnogs-post /usr/local/bin
sudo chmod 0755 /usr/local/bin/satnogs-post /usr/local/bin/satnogs-pre /usr/local/bin/grsat-wrapper.sh /usr/local/bin/kiss_satnogs.py /usr/local/bin/find_samp_rate.py
```

The GNU Radio UDP source need to have memory buffer increased for receiving more than a ~48k stream, so will need to add the following:
```
sudo cp udp.conf /etc/gnuradio/conf.d/
```

## SatNOGS setup

In satnogs-setup; enable pre/post observation scripts under Advanced -> Scripts:<br>
SATNOGS_PRE_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-pre {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
SATNOGS_POST_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-post {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
Under Advanced -> Radio settings:<br>
UDP_DUMP_HOST = `127.0.0.1`<br>
This will enable the UDP output. Select Apply and exit.

## Configuration options

Inside the script [grsat-wrapper.sh](grsat-wrapper.sh) there's some options. Make sure to edit the installed version.
```
# Settings
KEEPLOGS=no       # yes = keep, all other = remove KSS LOG

# uncomment and populate SELECTED with space separated norad id's
# to selectively submit data to the network
# if it's unset it will send all KISS demoded data, with possible dupes
SELECTED="39444 44830 43803 42017 44832 40074"
```

Please note that enabling KEEPLOGS it will eventually fill up the filesystem, also these are by default stored in tmpfs and it means they will be removed at reboot.<br>
It is also totally possible to add other demodulating software to the main script. Check the previous versions of the grsat-wrapper.sh to see some examples on how it worked in earlier releases.<br>

## Updating
Enter the repo and do a pull:
```
cd satnogs_gr-satellites
git pull
```
Then follow the install step again.


## Deactivation/Uninstall

Note: reverting certain software with satnogs-client-ansible is not possible, for example going from experimental to stable is not supported.<br>

Clear out the variables with satnogs-setup:<br>
```
SATNOGS_PRE_OBSERVATION_SCRIPT
SATNOGS_POST_OBSERVATION_SCRIPT
UDP_DUMP_HOST
```
Then update + apply.

If you want to you can remove the scripts installed:<br>
`cd /usr/local/bin && sudo rm -f find_samp_rate.py grsat-wrapper.sh kiss_satnogs.py satnogs-post satnogs-pre`
