import paho.mqtt.client as mqtt
import time

class ClientAI():

    def __init__(self, uuid_Arduino):
        self.uuid_Arduino = uuid_Arduino

    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        print("connecting...")
        self.clientMQTT.connect("151.81.17.207", 1883, 60)
        self.clientMQTT.publish(f'{self.uuid_Arduino}/command', 'OFF')
        self.clientMQTT.loop_start()


    def setup(self):
        self.setupMQTT()


def main(uuid_Arduino):
    ai = ClientAI(uuid_Arduino)
    ai.setup()
    return "STATO FINESTRA: CHIUSA"
