### author: Roberto Vezzani

import paho.mqtt.client as mqtt

class ClientAI():


	def setupMQTT(self):
		self.clientMQTT = mqtt.Client()
		self.clientMQTT.on_connect = self.on_connect
		self.clientMQTT.on_message = self.on_message
		print("connecting...")
		self.clientMQTT.connect("93.66.137.202", 1883, 60)
		self.clientMQTT.loop_start()



	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.clientMQTT.subscribe("sensor/1")


	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic + " " + str(msg.payload))
		if msg.topic=='sensor/1':
			val = int(msg.payload)
			if val < 100:
				self.clientMQTT.publish('openess','ON')
			else:
				self.clientMQTT.publish('openess', 'OFF')

	def setup(self):
		self.setupMQTT()

	def loop(self):
		# infinite loop for serial managing
		#
		while (True):
			pass



if __name__ == '__main__':
	ai = ClientAI()
	ai.setup()
	ai.loop()

