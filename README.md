# satnogs_gr-satellites
First try on combining gr-satellites with the satnogs-client and satnogs-flowgraphs

## Theory of operation
The main idea is to implement the UDP audio output in the satnogs_xxxx.grc to get the same data that goes to the OGG out into a running gr_satellites in UDP mode, thereby decoding the telemetry live and hopefully be able to submit to the satnogs observations.<br>
UDP data should be the same as GQRX produces and is supported directly with gr-satellites and some other programs<br>
See this for more information on the UDP protocol and examples https://gqrx.dk/doc/streaming-audio-over-udp

The pre-obs script launches gr-satellites in the background and it’s output is directed to /tmp/.satnogs/grsat_ID.log, grsat_ID.tlm, grsat_ID.kss<br>
It also creates a list of supported sats in the temp dir for faster access between runs.<br>
The post-obs stops the gr_satellites and looks for kiss data, parses and creates the necessary files for upload via the satnogs-client.

## Installation
Follow the instruction on https://gr-satellites.readthedocs.io/en/latest/installation.html
Also worth basing the change on a recent copy of the flowgraphs https://gitlab.com/librespacefoundation/satnogs/satnogs-flowgraphs/

Make sure the individual programs work before you enable the automated process!<br>
These are required: jq, gr_satellites, jy1sat_ssdv, ssdv, kiss_satnogs.py<br>
Upload the grsat-wrapper.sh and kiss_satnogs.py to /usr/local/bin<br>
Uncomment the “exit 0” on line 29 in the wrapper when you are ready to run everything.

Enable the pre/post observation scripts in satnogs-setup and put them in the appropriate location. The variables in the curly braces is sent to the script as arguments.

`SATNOGS_PRE_OBSERVATION_SCRIPT = /usr/local/bin/satnogs-pre {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
In the file /usr/local/bin/satnogs-pre:
````
#!/bin/bash
/usr/local/bin/grsat-wrapper.sh start "$@"
````

`SATNOGS_POST_OBSERVATION_SCRIPT = /usr/local/bin/satnogs-post {{ID}} {{FREQ}} {{TLE}} {{TIMESTAMP}} {{BAUD}} {{SCRIPT_NAME}}`<br>
In the file /usr/local/bin/satnogs-post:
````
#!/bin/bash
/usr/local/bin/grsat-wrapper.sh stop "$@"
````

Don't forget to set the executable bit on the scripts:
````
sudo chmod 0755 /usr/local/bin/satnogs-post /usr/local/bin/satnogs-pre /usr/local/bin/grsat-wrapper.sh /usr/local/bin/kiss_satnogs.py
````

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

Issues and features:<br>
https://github.com/daniestevez/gr-satellites/issues/196<br>
https://gitlab.com/librespacefoundation/satnogs/satnogs-client/-/issues/410
