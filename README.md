# satnogs_gr-satellites
First try on combining gr-satellites with the satnogs-client and satnogs-flowgraphs

## Theory of operation
The main idea is to implement the UDP audio output in the satnogs_xxxx.grc to get the same data that goes to the OGG out into a running gr_satellites in UDP mode, thereby decoding the telemetry live and hopefully be able to submit to the satnogs observations.<br>
UDP data should be the same as GQRX produces and is supported directly with gr-satellites and some other programs<br>
See this for more information on the UDP protocol and examples https://gqrx.dk/doc/streaming-audio-over-udp

The pre-obs script launches gr-satellites in the background and it’s output is directed to /tmp/.satnogs/grsat_ID.log, grsat_ID.kss<br>
It also creates a list of supported sats in the temp dir for faster access between runs.<br>
The post-obs stops the gr_satellites and looks for kiss data, parses and creates the necessary files for upload via the satnogs-client.

So in short, the path implemented: satnogs-flowgraphs -> udp audio (gqrx) -> decoder -> kiss -> kiss_satnogs for the binary extraction -> satnogs-client posting to the db.<br>
The newer version of the flowgraphs also has UDP IQ data on UDP_DUMP_PORT+1 (default 7356).

## Installation
Make sure to investigate if files already exists, versions changed, you already have pre/post-scripts etc. I will not be responsible for any problems so be careful when following this guide!<br>
Follow the instruction on https://gr-satellites.readthedocs.io/en/latest/installation.html<br>
The latest gr-satellites >=3.7.0-git with the --udp_raw and --ignore_unknown_args is required.<br>
Basically this, ymmv:
````
cd
sudo apt-get install swig liborc-0.4-0 python3-pip feh
sudo pip3 install --upgrade construct requests
git clone --depth=1 https://github.com/daniestevez/gr-satellites.git
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

Clone this repo and enter it:<br>
````
cd
git clone --depth=1 https://github.com/kng/satnogs_gr-satellites.git
cd satnogs_gr-satellites
````

Make sure the individual programs work before you enable the automated process!<br>
These are required: `jq, gr_satellites, jy1sat_ssdv, ssdv, kiss_satnogs.py`<br>
If you plan to run with IQ data, you also need: `find_samp_rate.py`<br>
Copy the grsat-wrapper.sh, kiss_satnogs.py, satnogs-pre and satnogs-post to /usr/local/bin<br>

````
sudo apt-get install jq
sudo cp grsat-wrapper.sh kiss_satnogs.py satnogs-pre satnogs-post /usr/local/bin
sudo chmod 0755 /usr/local/bin/satnogs-post /usr/local/bin/satnogs-pre /usr/local/bin/grsat-wrapper.sh /usr/local/bin/kiss_satnogs.py
````

The GNU Radio UDP source need to have memory buffer increased for receiving more than the 48k audio stream, so if using IQ mode you will need to add the following:
````
sudo cp udp.conf /etc/gnuradio/conf.d/
````

Before running these changes, it is recommended that you are on the latest version.<br>
To do this, run `sudo satnogs-setup` and run Update then Apply.<P>

As of current version on the satnogs-flowgraphs 1.3-1 you will also need to replace the satnogs_*.py in /usr/bin<br>
Check the current version with `dpkg -l satnogs-flowgraphs`<br>
Make sure you are already on version 1.3-1 before running the following commands:
````
sudo dpkg -i satnogs-flowgraphs_1.3-1+sa2kng_all.deb
````

Run `sudo satnogs-setup` and set the following parameters under Advanced -> Software:<br>
SATNOGS_CLIENT_URL = `git+https://gitlab.com/knegge/satnogs-client.git@sa2kng_station`<br>
SATNOGS_RADIO_FLOWGRAPHS_VERSION =  `1.3-1+sa2kng`<br>
SATNOGS_SETUP_ANSIBLE_URL = `https://gitlab.com/knegge/satnogs-client-ansible.git`<br>
SATNOGS_SETUP_ANSIBLE_BRANCH = `udp_control`<br>
SATNOGS_SETUP_SATNOGS_CONFIG_URL = `git+https://gitlab.com/knegge/satnogs-config.git@udp_control`<br>
Then update + apply to install these versions.<P>

Still in satnogs-setup; enable pre/post observation scripts under Advanced -> Scripts:<br>
SATNOGS_PRE_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-pre {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
SATNOGS_POST_OBSERVATION_SCRIPT = <br>`/usr/local/bin/satnogs-post {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
Set the UDP destination under Advanced -> Radio:<br>
UDP_DUMP_HOST = `127.0.0.1`<br>
Then update + apply, check the top of the screen that installed flowgraphs version is now 1.3-1+sa2kng.<P>

If the apply or update exits with an error like this, you need to re-install the .deb like described above.
````
Install SatNOGS Flowgraphs...
  Retrying... (1 of 4)
````

## Configuration options

Inside the script `grsat-wrapper.sh` there's some options. 
````
# Settings
KEEPLOGS=no       # yes = keep, all other = remove KSS LOG

# if IQ mode set, then you also need find_samp_rate.py
IQMODE=no          # yes = use IQ UDP data, all other = use audio UDP data

# uncomment and populate SELECTED with space separated norad id's
# to selectively submit data to the network
# if it's unset it will send all KISS demoded data, with possible dupes
SELECTED="39444 44830 43803 42017 44832 40074"
````

It is also totally possible to add other demodulating software to the main script. Check the previous versions of the grsat-wrapper.sh to see some examples on how it worked in earlier releases.<br>
Examples on how to use the UDP audio: https://gqrx.dk/doc/streaming-audio-over-udp

## Deactivation/Uninstall

To revert the installation, reinstall the original flowgraphs:<br>
`sudo apt-get --allow-downgrades install satnogs-flowgraphs`<br>

Then simply clear out the variables with satnogs-setup:<br>
```
SATNOGS_CLIENT_URL
SATNOGS_RADIO_FLOWGRAPHS_VERSION
SATNOGS_SETUP_ANSIBLE_URL
SATNOGS_SETUP_ANSIBLE_BRANCH
SATNOGS_SETUP_SATNOGS_CONFIG_URL
SATNOGS_PRE_OBSERVATION_SCRIPT
SATNOGS_POST_OBSERVATION_SCRIPT
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
