# LEGACY
Do note that this repository is considered legacy by now.<br>
The new python version `grsat.py` is in my [addons](https://github.com/kng/satnogs-client-docker/tree/main/addons).

# satnogs_gr-satellites
First try on combining gr-satellites with the satnogs-client and satnogs-flowgraphs.<br>
Now finally completely integrated in satnogs stable client.<br>
Read the installation [instructions](INSTALL.md).

## Theory of operation
The main idea is to extract the doppler corrected IQ stream in the satnogs_xxxx.grc to get the same data that goes to the demod and audio output into a running gr_satellites in UDP raw mode, thereby decoding the telemetry live and hopefully be able to submit to the satnogs observations and other data aggregators.<br>

The pre-obs script launches gr-satellites in the background and it’s output is directed to /tmp/.satnogs/grsat_ID.log, grsat_ID.kss<br>
It also creates a list of supported sats in the temp dir for faster access between runs.<br>
The post-obs stops the gr_satellites and looks for kiss data, parses and creates the necessary files for upload via the satnogs-client.

So in short, the path implemented: satnogs-flowgraphs -> udp data -> demod -> kiss -> kiss_satnogs for the binary extraction -> satnogs-client posting to the db.<br>

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
