# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import paho
import paho.mqtt.client as mqtt

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Slot

QML_IMPORT_NAME = "org.vranki.melunaru"
QML_IMPORT_MAJOR_VERSION = 1

def on_connect(client, userdata, flags, reason_code):
    global ml
    print(f"Connected with result code {reason_code}")
    client.subscribe("melunaru/#")

def on_message(client, userdata, msg):
    global ml
    if msg.topic.startswith('melunaru/status/'):
        num = int(msg.topic.split('/')[2])
        status = int(msg.payload)
        sourceStatuses[num] = status

class Melunaru(QObject):
    def __init__(self):
         self.sourceStatuses = {}
         self.mqttc = mqtt.Client()
         self.mqttc.on_connect = on_connect
         self.mqttc.on_message = on_message
         super().__init__()

    @Slot(result=int)
    def sourceCount(self):
        return 3

    @Slot()
    def start(self):
        self.mqttc.connect("localhost", 1883, 60)
        self.mqttc.loop_start()

    @Slot(int, float)
    def setVolume(self, source, volume):
        self.mqttc.publish('melunaru/volume/' + str(source), volume)

    @Slot(int, result=int)
    def sourceStatus(self, num):
        if num in self.sourceStatuses:
            return self.sourceStatuses[num]
        else:
            return 0


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
