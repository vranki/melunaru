# Melunaru

Virtual audio mixing with really long cables.

This project was created for a rock festival to stream music
from various stages to a central point, where a DJ could mix it 
and send it over FM radio and internet stream.

Other possible uses could be events with multiple stages such
as demoparties and conventions that want to stream their content
as audio.

```
[Source] -----IP-_
                  \
[Source] -----IP--[ Mixer ] --> { Stream }
                  /
[Source] -----IP--
```

Sources are any COTS linux machines that can stream audio to
the mixer machine using ices2/icecast2. Even Raspberry PI 1 is 
good enough.

Mixer has virtual mixer which can be used to mix between
sources and cue feature to listen to sources without
playing them. Mixer uses mpv to play the streams.

![Mixer GUI](gui-screenshot.png?raw=true "Mixer GUI")

You can use qpwgraph or other Pipewire GUI to manage
virtual audio routing to correct devices. You could even 
ignore the mixer GUI and connect the streams to a physical 
digital mixer. 

![qpwgraph](qpwgraph.png?raw=true "qpwgraph showing two playing sources")

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

* melunaru/volume/N -> set source N volume to given value (0-N)
* melunaru/url/N -> set source N playback URL
* melunaru/quit -> quits Melunaru process (deletes created sinks)
* melunaru/update -> request updating number of sources value
* melunaru/cue/N -> enable or disable CUE on given source (parameter is int 0 or 1)
* melunaru/show_vu/N - > open pavumeter on given source

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

## Networking

This is just my setup, you can handle networking however you want.

I set up a private IP space for streamers and the mixer machine, 
which can be run alongside normal dhcp LAN.

This way you can plug the machines to any LAN and they will
find each other without changes to config.

My Melunaru network is 192.168.42.x/16.

* Mixer ip 192.168.42.1
* Streamer 1 ip 192.168.42.101
* Streamer 2 ip 192.168.42.102
* Streamer 3 ip 192.168.42.103
* etc..

You can setup /etc/network/interfaces like this:
```
iface enp3s0 inet dhcp

iface enp3s0:1 inet static
    address 192.168.42.100
    netmask 255.255.0.0
```

You can also add the IP dynamically with command like this:
```
sudo ip addr add 192.168.42.1/16 dev enp3s0
```

