### author: Roberto Vezzani

import paho.mqtt.client as mqtt
import time

class ClientAI():


    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        print("connecting...")
        self.clientMQTT.connect("151.81.17.207", 1883, 60)
        self.clientMQTT.publish('openess', 'OFF')
        self.clientMQTT.loop_start()
        return 5

    def setup(self):
        self.setupMQTT()


def main():
    ai = ClientAI()
    ai.setup()
    return "STATO FINESTRA: CHIUSA"
