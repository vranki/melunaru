# Melunaru

Virtual audio mixing with really long cables

```
[Source] -----IP-_
                  \
[Source] -----IP--[ Mixer ] --> { Stream }
                  /
[Source] -----IP--
```

Sources are COTS linux machines that stream audio to
the mixer machine using ices2/icecast2. 

Mixer has virtual mixer which can be used to mix between
sources and cue feature to listen to sources without
playing them.

You can use qpwgraph or other pipewire GUI to manage
virtual audio routing to correct devices.

![Mixer GUI](gui-screenshot.png?raw=true "Mixer GUI")

## Source setup

Sources run ices2 for streaming live audio from their soundcards

Install packages (debian): 

```bash
sudo apt install ices2
```

Copy the included ices2.xml config file to the machine and
modify it as needed.

## Mixer setup

Mixer machine runs icecast2 daemon for receiving the streams 
and offers ogg vorbis streams. mixer.py creates virtual 
sinks for each stream and plays them.

Install packages (ubuntu): 

```bash
sudo apt install icecast2 python3-pulsectl mpv python3-mpv python3-asyncio-mqtt
```

### Config file

The config file is quite self-explanatory. Enter names and URLs for desired
source streams.

## MQTT API

Commands:

* melunaru/volume/N -> set source N volume to given value (0-1)
* melunaru/url/N -> set source N playback URL
* melunaru/quit -> quits Melunaru process
* melunaru/update -> request updating number of sources value
* melunaru/cue/N -> enable or disable CUE on given source (parameter is int 0 or 1)

Output: 

* melunaru/status/N -> Int, 1 if source is playing ok
* melunaru/num_sources -> Number of sources available


Examples:
```bash
mosquitto_pub -t melunaru/url/0 -m 'https://stream.radiostaddenhaag.com/stream/1/'
mosquitto_pub -t melunaru/volume/0 -m '0.5'
mosquitto_pub -t melunaru/quit -m ''
mosquitto_sub -v -t melunaru/#
```

## Useful commands

Use qpwgraph to view PipeWire graph

To create PA sinks

```bash
pactl load-module module-remap-sink sink_name=Sink1
pactl load-module module-remap-sink sink_name=Sink2
```

Sinks are connected to default output automatically

PipeWire management:

```bash
pw-link -o     # List outputs
pw-link -i     # List inputs
pw-link alsa_input....:capture_FL tunnel-sink.192.168.1.46:send_FL # Link output to input
pactl set-source-volume alsa_input.pci-000....stereo 50% # Set volume
```


To play audio to sinks

```bash
mpv https://stream.radiostaddenhaag.com/stream/1/ --audio-device=pipewire/Sink1
```

