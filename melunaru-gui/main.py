#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import paho
import paho.mqtt.client as mqtt

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Signal, Slot

QML_IMPORT_NAME = "org.vranki.melunaru"
QML_IMPORT_MAJOR_VERSION = 1

def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    client.subscribe("melunaru/#")
    client.publish('melunaru/update')

def on_message(client, userdata, msg):
    global ml
    if msg.topic.startswith('melunaru/status/'):
        num = int(msg.topic.split('/')[2])
        status = int(msg.payload)
        ml.sourceStatuses[num] = status
        ml.updated.emit()
    elif msg.topic.startswith('melunaru/media_name/'):
            num = int(msg.topic.split('/')[2])
            name = msg.payload.decode('utf-8')
            ml.sourceNames[num] = name
            ml.updated.emit()
    elif msg.topic.startswith('melunaru/num_sources'):
        ml.setSourceCount(int(msg.payload))

class Melunaru(QObject):
    updated = Signal()

    def __init__(self):
         super(Melunaru, self).__init__()
         self.sourceStatuses = {}
         self.sourceNames = {}
         self.mqttc = mqtt.Client()
         self.mqttc.on_connect = on_connect
         self.mqttc.on_message = on_message

    @Slot(result=int)
    def sourceCount(self):
        return len(self.sourceStatuses)

    @Slot()
    def start(self):
        self.mqttc.connect("localhost", 1883, 60)
        self.mqttc.loop_start()

    @Slot()
    def update(self):
        self.mqttc.publish('melunaru/update')

    @Slot(int, float)
    def setVolume(self, source, volume):
        self.mqttc.publish('melunaru/volume/' + str(source), volume)

    @Slot(int, int)
    def setCue(self, source, enabled):
        self.mqttc.publish('melunaru/cue/' + str(source), enabled)

    @Slot(int, result=int)
    def sourceStatus(self, num):
        if num in self.sourceStatuses:
            return self.sourceStatuses[num]
        else:
            return 0

    @Slot(int, result=str)
    def sourceName(self, num):
        if num in self.sourceNames:
            return self.sourceNames[num]
        else:
            return ''

    def setSourceCount(self, newCount):
        self.sourceStatuses = {}
        for i in range(0, newCount):
            self.sourceStatuses[i] = 0
        self.updated.emit()

    @Slot(int)
    def showVU(self, source):
        self.mqttc.publish('melunaru/show_vu/' + str(source))

    @Slot()
    def quit(self):
        self.mqttc.publish('melunaru/quit')


if __name__ == "__main__":
    global ml
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    ml = Melunaru()
    engine.rootContext().setContextProperty('melunaru', ml)
    engine.load(os.fspath(Path(__file__).resolve().parent / "main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
