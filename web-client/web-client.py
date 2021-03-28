import paho.mqtt.client as mqtt
import requests

# server_ip = "http://93.66.137.202:3000"   # Mio
# server_ip = "http://151.81.17.207:5000"   # Nello


class ClientWeb:

    def __init__(self):
        self.broker_ip = "93.66.137.202"
        self.server_ip = "http://151.81.17.207:5000"
        self.uuid_Arduino = 'ac0a2590-85d0-11eb-8c68-3065ecc9cc2c'  # l'utente deve conoscerlo
        # Solo all'inizio faccio una get per sapere lo stato della finestra
        str = self.getState()
        print(str['status'])

    def getState(self):
        myobj = {'id': self.uuid_Arduino}
        value = requests.get(
            self.server_ip + '/api/v1/sensor/status', json=myobj)
        print("Valore di stato ritornato: " + str(value.json()))
        return value.json()

    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        self.clientMQTT.on_connect = self.on_connect
        self.clientMQTT.on_message = self.on_message
        print("connecting...")
        self.clientMQTT.connect(self.broker_ip, 1883, 60)
        self.clientMQTT.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # Su questo
        self.clientMQTT.subscribe(f'{self.uuid_Arduino}/window')

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        if msg.topic == f'{self.uuid_Arduino}/window':
            val = int(msg.payload)
            if val < 100:
                # self.post_state(self.windowState)
                self.clientMQTT.publish(f'{self.uuid_Arduino}/command', 'ON')
            else:
                # self.clientMQTT.publish(f'{self.uuid_Arduino}/CS', self.windowState)
                self.clientMQTT.publish(f'{self.uuid_Arduino}/command', 'OFF')

    def setup(self):
        self.setupMQTT()

    def loop(self):
        # infinite loop for serial managing
        #
        while (True):
            pass


if __name__ == '__main__':
    ai = ClientWeb()
    ai.setup()
    ai.loop()
