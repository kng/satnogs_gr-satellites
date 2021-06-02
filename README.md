# satnogs_gr-satellites
First try on combining gr-satellites with the satnogs-client and satnogs-flowgraphs.<br>
Now finally completely integrated in satnogs stable client.

## Theory of operation
The main idea is to extract the doppler corrected IQ stream in the satnogs_xxxx.grc to get the same data that goes to the demod and audio output into a running gr_satellites in UDP raw mode, thereby decoding the telemetry live and hopefully be able to submit to the satnogs observations and other data aggregators.<br>

The pre-obs script launches gr-satellites in the background and it’s output is directed to /tmp/.satnogs/grsat_ID.log, grsat_ID.kss<br>
It also creates a list of supported sats in the temp dir for faster access between runs.<br>
The post-obs stops the gr_satellites and looks for kiss data, parses and creates the necessary files for upload via the satnogs-client.

So in short, the path implemented: satnogs-flowgraphs -> udp data -> demod -> kiss -> kiss_satnogs for the binary extraction -> satnogs-client posting to the db.<br>

## Installation
Make sure to investigate if files already exists, versions changed, you already have pre/post-scripts etc. I will not be responsible for any problems so be careful when following this guide!<br>
Follow the instruction on https://gr-satellites.readthedocs.io/en/latest/installation.html<br>
The latest gr-satellites >=3.7.0-git with the --udp_raw and --ignore_unknown_args is required.<br>
Basically this, ymmv:
````
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
````
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


Clone this repo and enter it:<br>
````
cd
git clone --depth=1 https://github.com/kng/satnogs_gr-satellites.git
cd satnogs_gr-satellites
````

Make sure the individual programs work before you enable the automated process!<br>
These are required: `jq, gr_satellites, jy1sat_ssdv, ssdv, kiss_satnogs.py, find_samp_rate.py`<br>
Copy the grsat-wrapper.sh, kiss_satnogs.py, find_samp_rate.py, satnogs-pre and satnogs-post to /usr/local/bin<br>

````
sudo apt-get install jq
sudo cp grsat-wrapper.sh kiss_satnogs.py find_samp_rate.py satnogs-pre satnogs-post /usr/local/bin
sudo chmod 0755 /usr/local/bin/satnogs-post /usr/local/bin/satnogs-pre /usr/local/bin/grsat-wrapper.sh /usr/local/bin/kiss_satnogs.py /usr/local/bin/find_samp_rate.py
````

The GNU Radio UDP source need to have memory buffer increased for receiving more than a ~48k stream, so will need to add the following:
````
sudo cp udp.conf /etc/gnuradio/conf.d/
````

## SatNOGS setup:

In satnogs-setup; enable pre/post observation scripts under Advanced -> Scripts:<br>
SATNOGS_PRE_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-pre {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
SATNOGS_POST_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-post {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
Under Advanced -> Radio settings:<br>
UDP_DUMP_HOST = `127.0.0.1`<br>
This will enable the UDP output. Select Apply and exit.

## Configuration options

Inside the script `grsat-wrapper.sh` there's some options. 
````
# Settings
KEEPLOGS=no       # yes = keep, all other = remove KSS LOG

# uncomment and populate SELECTED with space separated norad id's
# to selectively submit data to the network
# if it's unset it will send all KISS demoded data, with possible dupes
SELECTED="39444 44830 43803 42017 44832 40074"
````

Please note that enabling KEEPLOGS it will eventually fill up the filesystem, also these are by default stored in tmpfs and it means they will be removed at reboot.<br>
It is also totally possible to add other demodulating software to the main script. Check the previous versions of the grsat-wrapper.sh to see some examples on how it worked in earlier releases.<br>

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

## References

My relevant project forks:<br>
https://gitlab.com/knegge/satnogs-flowgraphs<br>
https://gitlab.com/knegge/satnogs-client<br>
https://gitlab.com/knegge/satnogs-client-ansible<br>
https://gitlab.com/knegge/satnogs-config<br>

gr-satellites cli reference:<br>
https://gr-satellites.readthedocs.io/en/latest/command_line.html<br>
https://github.com/daniestevez/gr-satellites<br>
https://github.com/daniestevez/gr-frontends

Main idea:<br>
https://community.libre.space/t/integrating-gr-satellites-into-satnogs/2440

Post upload script and parsing from:<br>
https://community.libre.space/t/uploading-compressed-iq-files-to-dropbox-or-any-other-cloud-storage-provider/5395/2

File naming for the satnogs-client:<br>
https://gitlab.com/librespacefoundation/satnogs/satnogs-client/-/blob/1.4/satnogsclient/observer/observer.py#L112-151

JY1-sat image decoding:<br>
https://destevez.net/2019/04/decoding-ssdv-from-jy1sat/

Modified show_kiss parser from Fabian Schmidt:<br>
https://gist.githubusercontent.com/kerel-fs/910738286c4fed9409550b4efb34cab6/raw/263c2df701e632980021048792e9b39db74cfe09/show_kiss_timestamp.py

Issues and features:<br>
https://github.com/daniestevez/gr-satellites/issues/196<br>
https://gitlab.com/librespacefoundation/satnogs/satnogs-client/-/issues/410

<br>Final notes, this was a terrible experience and had I known better I would simply have posted patches for the files and left it at that. It took way too much time and effort to complete and did end up destroying my interest in the project. There were several good people involved and I leave them with the credit for getting me to push through with it. Ingen nämnd, ingen glömd.
