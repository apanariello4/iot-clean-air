### author: Roberto Vezzani

import serial
import serial.tools.list_ports
import numpy as np
import urllib.request

import paho.mqtt.client as mqtt

class Bridge():


# Connection
    def setupSerial(self):
        # open serial port
        self.ser = None
        print("list of available ports: ")

        ports = serial.tools.list_ports.comports()
        self.portname=None
        for port in ports:
            print (port.device)
            print (port.description)
            if 'arduino' in port.description.lower():
                self.portname = port.device
        print ("connecting to " + self.portname)

        try:
            if self.portname is not None:
                self.ser = serial.Serial(self.portname, 9600, timeout=0)
        except:
            self.ser = None

        # self.ser.open()

        # internal input buffer from serial
        self.inbuffer = []

# -------------- End Connection --------------

# Setup Client
    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        self.clientMQTT.on_connect = self.on_connect
        self.clientMQTT.on_message = self.on_message
        print("connecting...")
        self.clientMQTT.connect("151.81.17.207", 1883, 60)

        self.clientMQTT.loop_start()



    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed. (rinnovata)
        self.clientMQTT.subscribe("openess")



    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        if msg.topic== 'openess':
            self.ser.write (msg.payload) #can be ON or OFF

    def setup(self):
        self.setupSerial()
        self.setupMQTT()

    def loop(self):
        # infinite loop for serial managing
        #
        while (True):
            #look for a byte from serial (dati da Arduino)
            if not self.ser is None:

                if self.ser.in_waiting>0:
                    # data available from the serial port
                    lastchar=self.ser.read(1)


                    if lastchar==b'\xfe': #EOL
                        print("\nValue received")
                        self.useData()
                        self.inbuffer =[]
                    else:
                        # append
                        self.inbuffer.append(lastchar)

    def useData(self):
        # I have received a line from the serial port. I can use it
        if len(self.inbuffer)<3:   # at least header, size, footer
            return False
        # split parts
        if self.inbuffer[0] != b'\xff':
            return False

#arduino può inviare più dati diversi, quindi è utile questa struttura dati
        numval = int.from_bytes(self.inbuffer[1], byteorder='little')
        for i in range (numval):
            val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
            strval = "Sensor %d: %d " % (i, val)
            print(strval)
            # I send the data to the Client
            self.clientMQTT.publish('sensor/{:d}'.format(i),'{:d}'.format(val))




if __name__ == '__main__':
    br=Bridge()
    br.setup()
    br.loop()
