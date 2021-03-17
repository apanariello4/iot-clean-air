### author: Roberto Vezzani

import serial
import serial.tools.list_ports
import sqlite3
from sqlite3 import Error
import paho.mqtt.client as mqtt
import uuid
import os
import requests

uuid_Arduino = 0
path_db = r"C:\Users\Emanuele\PycharmProjects\iot-clean-air\Smart window\db_UUID"
broker_ip = "93.66.137.202"
# server_ip = "http://93.66.137.202:3000"  # MIO
server_ip = "http://151.81.17.207:5000"


class Bridge:

    def __init__(self):
        self.windowState = None  # Arduino comunica lo stato della finestra al Bridge
        # La prima volta che si connette al Server gli manda il suo id in modo tale che possa sottoscriversi al topic
        self.post_state(self.windowState)
        print("Ho comunicato al server il mio ID univoco di Arduino!")

    # Connection
    def setupSerial(self):
        # open serial port
        self.ser = None
        print("list of available ports: ")

        ports = serial.tools.list_ports.comports()
        self.portname = None
        for port in ports:
            print(port.device)
            print(port.description)
            if 'arduino' in port.description.lower():
                self.portname = port.device
        print("connecting to " + self.portname)

        try:
            if self.portname is not None:
                self.ser = serial.Serial(self.portname, 9600, timeout=0)
        except:
            self.ser = None

        # self.ser.open()

        # internal input buffer from serial
        self.inbuffer = []

    # Setup Client
    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        self.clientMQTT.on_connect = self.on_connect
        self.clientMQTT.on_message = self.on_message
        print("connecting...")
        self.clientMQTT.connect(broker_ip, 1883, 60)
        self.clientMQTT.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.clientMQTT.subscribe(f'{uuid_Arduino}/command')


    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        # Riceve valore dal Client, lo manda ad Arduino e aggiorna il server
        if msg.topic == f'{uuid_Arduino}/command':
            self.ser.write(msg.payload)  # can be ON or OFF
            self.post_state(self.windowState)

    def setup(self):
        self.setupSerial()
        self.setupMQTT()

    def loop(self):

        while (True):
            # look for a byte from serial (dati da Arduino)
            if not self.ser is None:

                if self.ser.in_waiting > 0:
                    # data available from the serial port
                    lastchar = self.ser.read(1)

                    if lastchar == b'\xfe':  # EOL
                        print("\nValue received")
                        self.useData()
                        self.inbuffer = []
                    else:
                        # append
                        self.inbuffer.append(lastchar)

    def useData(self):
        # I have received a line from the serial port. I can use it
        if len(self.inbuffer) < 3:  # at least header, size, footer
            return False
        # split parts
        if self.inbuffer[0] != b'\xff':
            return False

        # Arduino può inviare più dati diversi, quindi è utile questa struttura dati
        numval = int.from_bytes(self.inbuffer[1], byteorder='little')

        val = int.from_bytes(self.inbuffer[2], byteorder='little')
        print("valore sensore: ", val)
        # Se è la prima volta che il valore viene aggiornato avverto il server che avvertirà il client

        if self.windowState != val and val != 2:
            self.windowState = val
            # Send the data to the Server

            print(self.post_state(self.windowState))


    def post_state(self, status):
        # id deve essere UUID
        url = server_ip + '/api/v1/sensor/status'
        myobj = {'id': uuid_Arduino, 'status': status}
        x = requests.post(url, json=myobj)
        return x

class Database:

    def getName(self):

        """ create a database connection to a SQLite database """
        # Exists => there is also the name
        if os.path.isfile(path_db):

            conn = None
            try:
                conn = sqlite3.connect(path_db)
            except Error as e:
                print(e)
            finally:
                if conn:
                    cur = conn.cursor()
                    uuid_Arduino = cur.execute('SELECT uuid FROM dataArduino').fetchone()[0]
                conn.close()

        else:
            conn = None
            try:
                conn = sqlite3.connect(path_db)
            except Error as e:
                print(e)
            finally:
                if conn:
                    cur = conn.cursor()
                    cur.execute('''CREATE TABLE dataArduino
                                   (uuid text)''')
                    uuid_Arduino = str(uuid.uuid4())
                    cur.execute("INSERT INTO dataArduino VALUES (?)", (uuid_Arduino,))
                    print("Valore immesso")
                    conn.commit()
                    conn.close()
        print("uuid_Arduino:", uuid_Arduino)
        return uuid_Arduino


if __name__ == '__main__':
    db = Database()
    uuid_Arduino = db.getName()
    print(uuid_Arduino)
    br = Bridge()
    br.setup()
    br.loop()
