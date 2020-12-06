# satnogs_gr-satellites
First try on combining gr-satellites with the satnogs-client and satnogs-flowgraphs

## Theory of operation
The main idea is to implement the UDP audio output in the satnogs_xxxx.grc to get the same data that goes to the OGG out into a running gr_satellites in UDP mode, thereby decoding the telemetry live and hopefully be able to submit to the satnogs observations.<br>
UDP data should be the same as GQRX produces and is supported directly with gr-satellites and some other programs<br>
See this for more information on the UDP protocol and examples https://gqrx.dk/doc/streaming-audio-over-udp

The pre-obs script launches gr-satellites in the background and it’s output is directed to /tmp/.satnogs/grsat_ID.log, grsat_ID.tlm, grsat_ID.kss<br>
It also creates a list of supported sats in the temp dir for faster access between runs.<br>
The post-obs stops the gr_satellites and looks for kiss data, parses and creates the necessary files for upload via the satnogs-client.

So in short, the path implemented: satnogs-flowgraphs -> udp audio (gqrx) -> decoder -> kiss -> kiss_satnogs for the binary extraction -> satnogs-client posting to the db. 

## Installation
Make sure to investigate if files already exists, versions changed, you already have pre/post-scripts etc. I will not be responsible for any problems so be careful when following this guide!<br>
Follow the instruction on https://gr-satellites.readthedocs.io/en/latest/installation.html<br>
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
These are required: jq, gr_satellites, jy1sat_ssdv, ssdv, kiss_satnogs.py<br>
Copy the grsat-wrapper.sh, kiss_satnogs.py, satnogs-pre and satnogs-post to /usr/local/bin<br>
Uncomment the “exit 0” on line 29 in the wrapper when you are ready to run everything.
````
sudo apt-get install jq psmisc
sudo cp grsat-wrapper.sh kiss_satnogs.py satnogs-pre satnogs-post /usr/local/bin
sudo chmod 0755 /usr/local/bin/satnogs-post /usr/local/bin/satnogs-pre /usr/local/bin/grsat-wrapper.sh /usr/local/bin/kiss_satnogs.py
````

As of current version on the satnogs-flowgraphs 1.2.2 you will also need to replace the satnogs_bpsk.py in /usr/bin<br>
Probably worth basing the change on a recent copy of the flowgraphs https://gitlab.com/librespacefoundation/satnogs/satnogs-flowgraphs/<br>
Use the bpsk_udp.png as reference to make this change in newer versions. Check the diff between the original satnogs_bpsk.py and your newly generated one.<br>
````
sudo cp satnogs_bpsk.py /usr/bin
sudo chmod 0755 /usr/bin/satnogs_bpsk.py
````

Enable the pre/post observation scripts in satnogs-setup and put them in the appropriate location. The variables in the curly braces is sent to the script as arguments.

`SATNOGS_PRE_OBSERVATION_SCRIPT = /usr/local/bin/satnogs-pre {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
`SATNOGS_POST_OBSERVATION_SCRIPT = /usr/local/bin/satnogs-post {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>

## References

gr-satellites cli reference<br>
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
https://github.com/kerel-fs/
https://gist.githubusercontent.com/kerel-fs/910738286c4fed9409550b4efb34cab6/raw/263c2df701e632980021048792e9b39db74cfe09/show_kiss_timestamp.py

Issues and features:<br>
https://github.com/daniestevez/gr-satellites/issues/196<br>
https://gitlab.com/librespacefoundation/satnogs/satnogs-client/-/issues/410
