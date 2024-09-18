# Melunaru

Virual audio mixing with really long cables

WIP

## Source setup

Sources run ices2 for streaming audio from their soundcards

Install packages (debian): 

'''bash
sudo apt install ices2
'''

Copy the included ices2.xml config file to the machine and
modify it as needed.

## Mixer setup

Mixer machine runs icecast2 daemon for receiving the streams and
offers ogg vorbis streams. 
mixer.py creates virtual sinks for each stream and plays
them.

Install packages (ubuntu): 

'''bash
sudo apt install icecast2 python3-pulsectl mpv python3-mpv python3-asyncio-mqtt
'''

## MQTT API

Commands:

melunaru/volume/N -> set source N volume to given value (0-1)
melunaru/url/N -> set source N playback URL
melunaru/quit -> quits Melunaru process

Output: 

melunaru/status/N -> Boolean, true if source is playing ok

Examples:
'''bash
mosquitto_pub -t melunaru/url/0 -m 'https://stream.radiostaddenhaag.com/stream/1/'
mosquitto_pub -t melunaru/volume/0 -m '0.5'
mosquitto_pub -t melunaru/quit -m ''
mosquitto_sub -v -t melunaru/#
'''

## Useful commands

Use qpwgraph to view PipeWire graph

To create PA sinks

'''bash
pactl load-module module-remap-sink sink_name=Sink1
pactl load-module module-remap-sink sink_name=Sink2
'''

Sinks are connected to default output automatically

PipeWire management:

'''bash
pw-link -o     # List outputs
pw-link -i     # List inputs
pw-link alsa_input....:capture_FL tunnel-sink.192.168.1.46:send_FL # Link output to input
pactl set-source-volume alsa_input.pci-000....stereo 50% # Set volume
'''


To play audio to sinks

'''bash
mpv https://stream.radiostaddenhaag.com/stream/1/ --audio-device=pipewire/Sink1
'''

