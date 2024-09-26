#!/usr/bin/env python3
import pulsectl
import mpv
import asyncio
import yaml
import paho
import paho.mqtt.client as mqtt
import subprocess

# TODO: Use when available
#from pipewire_python import link

def on_connect(client, userdata, flags, reason_code):
	client.subscribe("melunaru/#")

def on_message(client, userdata, msg):
	global mm
	if msg.topic == 'melunaru/quit':
		mm.running = False
	if msg.topic == 'melunaru/update':
		client.publish('melunaru/num_sources', mm.num_sources)
	if msg.topic.startswith('melunaru/volume/'):
		num = int(msg.topic.split('/')[2])
		vol = float(msg.payload)
		mm.set_volume(num, vol)
	if msg.topic.startswith('melunaru/url/'):
		num = int(msg.topic.split('/')[2])
		mm.urls[num] = msg.payload.decode('utf-8')
		mm.players[num].stop()
		print('Playing URL', urls[num], 'on player', num)
	if msg.topic.startswith('melunaru/cue/'):
		num = int(msg.topic.split('/')[2])
		enabled = int(msg.payload)
		mm.set_cue(num, True if enabled else False)
	if msg.topic.startswith('melunaru/show_vu/'):
		num = int(msg.topic.split('/')[2])
		mm.show_VU(num)

class MelunaruMixer:
	def __init__(self):
		self.num_sources = 0
		self.running = True

	def sink_name(self, num):
		return 'Melunaru_stream_' + str(num)

	def find_sink(self, num):
		for sink in self.pulse.sink_list():
			if(sink.description == self.sink_name(num) + ' sink'):
				return sink
		return None

	def create_source(self, num):
		sink = self.find_sink(num)
		if(sink):
			print('Sink', num, 'Already exists')
		else:
			self.pulse.module_load('module-remap-sink', 'sink_name=' + self.sink_name(num))
			print('Created sink', num)

	def delete_sink(self, sinkname):
		for module in self.pulse.module_list():
			if(module.argument == 'sink_name=' + sinkname):
				print('Deleting sink', sinkname, ' - Unloading module', module.index, module.name)
				self.pulse.module_unload(module.index)

	def delete_source(self, num):
		self.delete_sink(self.sink_name(num))

	def set_volume(self, num, volume):
		sink = self.find_sink(num)
		if sink:
			self.pulse.volume_set_all_chans(sink, volume)

	def player_ok(self, player):
		eof = getattr(player, 'eof-reached')
		if eof == True:
			return False
		if eof == False:
			return True
		return False

	def media_name(self, num):
		try:
			attrname = getattr(self.players[num], 'metadata/by-key/icy-name')
			if attrname:
				return attrname
		except AttributeError:
			pass
		return self.config['sources'][num]['name']

	def check_players(self):
		for i in range(0,self.num_sources):
			if not self.player_ok(self.players[i]):
				self.players[i].play(self.urls[i])
				print('Starting player', i, self.players[i].path)

	def link_ports(self, source, dest, enabled):
		ul = ''
		if not enabled:
			ul = ' -d '
		pwlink = subprocess.Popen('pw-link ' + ul + source + ' ' + dest, shell=True)
		pwlink.wait()

	def create_cue(self):
		for sink in self.pulse.sink_list():
			if(sink.description == 'Melunaru_CUE sink'):
				return
		self.pulse.module_load('module-remap-sink', 'sink_name=Melunaru_CUE')
		print('Created CUE sink')

	def delete_cue(self):
		self.delete_sink('Melunaru_CUE')

	def set_cue(self, num, enabled):
		self.link_ports('Sink' + str(num) + ':monitor_FL', 'Melunaru_CUE:playback_FL', enabled)
		self.link_ports('Sink' + str(num) + ':monitor_FR', 'Melunaru_CUE:playback_FR', enabled)

	def show_VU(self, num):
		subprocess.Popen('pavumeter ' + self.sink_name(num), shell=True)		

	def init(self):
		self.running = True
		self.players = []
		self.urls = []
		self.config = yaml.safe_load(open("config.yml"))
		self.num_sources = len(self.config['sources'])
		if self.num_sources == 0:
			print('No sources defined in config file! Make sure you have config.yml')
			return

		self.mqttc = mqtt.Client()
		self.mqttc.on_connect = on_connect
		self.mqttc.on_message = on_message
		self.mqttc.connect(self.config['mqtt']['hostname'], 1883, 60)
		self.pulse = pulsectl.Pulse('melunaru')
		for i in range(0, self.num_sources):
			print('Setting up source', i)
			self.create_source(i)
			self.set_volume(i, self.config['default_volume'])
			player = mpv.MPV()
			player['audio-device'] = 'pipewire/' + self.sink_name(i)
			self.players.append(player)
			self.urls.append(self.config['sources'][i]['url'])

		self.create_cue()

		print('Mixer started')

	async def run(self):
		self.mqttc.loop_start()
		while self.running:
			self.check_players()
			for i in range(0, self.num_sources):
				ok = self.player_ok(self.players[i])
				print('Player', i, 'ok:', ok, self.media_name(i))
				self.mqttc.publish('melunaru/status/' + str(i), 1 if ok else 0)
				self.mqttc.publish('melunaru/media_name/' + str(i), self.media_name(i))
			await asyncio.sleep(1)

	def cleanup(self):
		self.mqttc.loop_stop()
		for i in range(0, self.num_sources):
			self.set_cue(i, False)
			self.players[i].stop()
			self.delete_source(i)
		self.delete_cue()
		self.pulse.close()
		print('Shut down gracefully')

async def main():
	global mm
	mm = MelunaruMixer()
	mm.init()
	try:
		await mm.run()
	except asyncio.exceptions.CancelledError:
		pass
	mm.cleanup()

asyncio.run(main())


