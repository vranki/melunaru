#!/usr/bin/env python3
import pulsectl
import mpv
import asyncio
import paho
import paho.mqtt.client as mqtt

NUM_SOURCES = 2
running = True

def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("melunaru/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global running
    global pulse
    global urls
    global players
    
    # print(msg.topic+" "+str(msg.payload))
    if msg.topic == 'melunaru/quit':
    	running = False
    if msg.topic.startswith('melunaru/volume/'):
    	num = int(msg.topic.split('/')[2])
    	vol = float(msg.payload)
    	print('Setting volume of', num, vol)
    	set_volume(pulse, num, vol)
    if msg.topic.startswith('melunaru/url/'):
    	num = int(msg.topic.split('/')[2])
    	urls[num] = msg.payload.decode('utf-8')
    	players[num].stop()
    	print('Playing URL', urls[num], 'on player', num)

def send_command(command):
    sock = pulsectl.connect_to_cli(socket_timeout=1)
    sock.write(command+"\n")
    sock.flush()

def find_sink(pulse, num):
	for sink in pulse.sink_list():
		if(sink.description == 'Sink' + str(num) + ' sink'):
			return sink
	return None

def create_source(pulse, num):
	sink = find_sink(pulse, num)
	if(sink):
		print('Sink', num, 'Already exists')
	else:
		pulse.module_load('module-remap-sink', 'sink_name=Sink' + str(num))
		print('Created sink', num)

def delete_source(pulse, num):
	for module in pulse.module_list():
		if(module.argument == 'sink_name=Sink' + str(num)):
			print('Unloading module', module.index, module.name)
			pulse.module_unload(module.index)

def set_volume(pulse, num, volume):
	pulse.volume_set_all_chans(find_sink(pulse, num), volume)

def player_ok(player):
	eof = getattr(player, 'eof-reached')
	if eof == True:
		return False
	if eof == False:
		return True
	return False

def check_players(players):
	global urls
	for i in range(0,NUM_SOURCES):
		if not player_ok(players[i]):
			players[i].play(urls[i])
			print('Starting player', i, players[i].path)

async def main():
	global running
	global pulse
	global urls
	global players
	running = True
	players = []
	urls = []
	
	mqttc = mqtt.Client()
	mqttc.on_connect = on_connect
	mqttc.on_message = on_message
	mqttc.connect("localhost", 1883, 60)
	pulse = pulsectl.Pulse('melunaru')
	for i in range(0,NUM_SOURCES):
		print('Setting up source', i)
		create_source(pulse, i)
		set_volume(pulse, i, 1)
		player = mpv.MPV()
		player['audio-device'] = 'pipewire/Sink' + str(i)
		players.append(player)
		urls.append('http://localhost:8000/streamer' + str(i) + '.ogg')

	print('Mixer started')
	mqttc.loop_start()
	while running:
		check_players(players)
		for i in range(0,NUM_SOURCES):
			ok = player_ok(players[i])
			print('Player', i, 'ok:', ok)
			mqttc.publish('melunaru/status/' + str(i), 1 if ok else 0)
		await asyncio.sleep(1)
	mqttc.loop_stop()
	for i in range(0,NUM_SOURCES):
		players[i].stop()
		delete_source(pulse, i)
	pulse.close()
	print('Shut down gracefully')

asyncio.run(main())


