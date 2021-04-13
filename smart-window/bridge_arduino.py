import paho.mqtt.client as mqtt
import requests
import time
from datetime import datetime, timedelta
from DB_Arduino import Database
from setup_arduino import SetupConnection

# broker_ip = "93.66.137.202" # Local Broker
# server_ip = "http://93.66.137.202:3000"  # Local Server

server_ip = "http://151.81.28.142:5000"
broker_ip = "151.81.28.142"
threshold_pm_25 = 100  # µg/mc air
threshold_pm_10 = 100  # µg/mc air

path_db = r"C:\Users\Emanuele\PycharmProjects\iot-clean-air\Smart-Window\db_UUID"
region = 'Modena'


class MQTT:

    def __init__(self, broker_ip, uuid_Arduino, ser):
        self.broker_ip = broker_ip
        self.uuid_Arduino = uuid_Arduino
        self.ser = ser
        self.setupMQTT()

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
        self.clientMQTT.subscribe(f'{self.uuid_Arduino}/command')

        # The callback for when a PUBLISH message is received from the server.

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        # Riceve valore dal Client, lo manda ad Arduino e aggiorna il server
        if msg.topic == f'{self.uuid_Arduino}/command':
            print("Mandato")
            self.ser.write(msg.payload)  # can be ON or OFF, lo mando ad arduino

            value_returned = br.post_state(br.windowState)  # aggiorno il server
            print("Ho fatto una post ed è ritornato: ", value_returned)


class Bridge:

    def __init__(self):
        # The first time that the Bridge will connect to the server it will send its id (used to subscribe to the topic)
        self.windowState = 0  # Arduino will communicate the state of the windows to the Bridge
        self.broker_ip = broker_ip
        self.path_db = path_db
        self.region = region
        self.uuid_Arduino = db.getName()
        self.inbuffer, self.ser = sp.setupSerial()
        # _ = MQTT(self.broker_ip, self.uuid_Arduino, self.ser)
        self.post_state(self.windowState)
        print("Ho comunicato al server il mio ID univoco di Arduino!")
        self.prediction_1h = self.prediction_2h = self.prediction_3h = None

    def loop(self):

        # La prima volta controllare l'inquinamento dopo 2 secondi
        # Successivamente il controllo viene fatto ogni ora
        lasttime = time.time() - 3598
        print(time.localtime(lasttime + 3600))
        while (True):
            # look for a byte from serial (dati da Arduino)
            if self.ser is not None:

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

            # Fa una Get per l'inquinamento ogni ora e prende i valori delle 3 ore successive
            if time.time() - lasttime > 3600:
                pollution_values = self.get_pollution()
                self.evaluete_pollution(pollution_values)
                self.send_info_Arduino()
                lasttime = time.time()
                print(time.localtime(lasttime))

    def send_info_Arduino(self):
        valid_hours = "Nessun dato valido dal DB"
        # Not None: there is the value
        # != 0: the value respect legal limits
        """
            Guardo quante ore successive hanno valori accettabili di inquinamento e comunico quel numero
            Se la prossima sono sotto ai limiti di legge ma dalla seconda ora in poi l'inquinamento è alto mando H1
            Se anche la seconda ora rispetta i limiti --> H2
            Se li rispetta anche la terma --> H3
            is not None: controlla che i dati siano relativi alle ore future (vedi funzione evaluete_pollution)
            Questo controllo viene fatto ogni ora; se non arrivano nuovi dati aggiornati dalla get sulla centralina
            La terza ora futura diventerà la seconda ora futura e la seconda la prossima.
            Arduino sarà sempre aggiornato capendo se in quell'ora può aprire la finestra o se deve tenerla chiusa.
        """

        if self.prediction_3h is not None:
            valid_hours = "Dati validi delle future 3 ore!"
            if self.prediction_1h != 0 and self.prediction_2h != 0 and self.prediction_3h != 0:
                self.ser.write(b'H3')
                print("mandato 3h")
            elif self.prediction_1h != 0 and self.prediction_2h != 0:
                self.ser.write(b'H2')
                print("mandato 2h")
            elif self.prediction_1h != 0:
                self.ser.write(b'H1')
                print("mandato 1h")
        elif self.prediction_2h is not None:
            valid_hours = "Dati validi delle future 2 ore!"
            if self.prediction_1h != 0 and self.prediction_2h != 0:
                print("mandato 2h")
                self.ser.write(b'H2')

            elif self.prediction_1h != 0:
                print("mandato 1h")
                self.ser.write(b'H1')

        elif self.prediction_1h is not None:
            valid_hours = "Dati validi della futura ora!"
            if self.prediction_1h != 0:
                self.ser.write(b'H1')
                print("mandato 1h")
        print(valid_hours)

    def evaluete_pollution(self, pollution_values):
        """
            If Arduino find an indoor low air quality it requires the predictions of the future 3 hours and
            makes choices with respect what has been acquired by the pollution detection control unit.
            If the outside air quality is good enough it can open the windows for the next hours (w.r.t. predictions permissions)
            if instead the outdoor air quality is not good, the windows remain closed
        """

        timestamp = datetime.strptime(pollution_values['timestamp'], '%Y-%m-%d %H:%M:%S')
        pm_10_1h = pm_25_1h = pm_10_2h = pm_25_2h = pm_10_3h = pm_25_3h = None
        self.prediction_1h = self.prediction_2h = self.prediction_3h = None

        # If the results have been updated less then 10 minutes I can take all of them
        if datetime.now() < timestamp + timedelta(minutes=10):
            pm_10_1h = pollution_values['pm_10_1h']
            pm_25_1h = pollution_values['pm_25_1h']
            pm_10_2h = pollution_values['pm_10_2h']
            pm_25_2h = pollution_values['pm_25_2h']
            pm_10_3h = pollution_values['pm_10_3h']
            pm_25_3h = pollution_values['pm_25_3h']

        # If the results have been updated less then 1h and 10m I can also the 2h predictions
        elif datetime.now() < timestamp + timedelta(hours=1, minutes=10):
            pm_10_1h = pollution_values['pm_10_2h']
            pm_25_1h = pollution_values['pm_25_2h']
            pm_10_2h = pollution_values['pm_10_3h']
            pm_25_2h = pollution_values['pm_25_3h']

        # If the results have been updated less then 2h and 10m I can also the last hour predictions
        elif datetime.now() < timestamp + timedelta(hours=2, minutes=10):
            # These values ware related with the last hour but the last values have been uploaded a long time ago
            # Scenario in which an error in the pollution control unit has occurred
            pm_10_1h = pollution_values['pm_10_3h']
            pm_25_1h = pollution_values['pm_25_3h']

        # Check the air quality and decide if is right to keep the windows open
        # Let's assume that if we have the pm 2.5 we have also the pm 10 because the sensor is the same
        if pm_10_1h is not None:
            if pm_10_1h < threshold_pm_10 and pm_25_1h < threshold_pm_25:
                self.prediction_1h = 1
            else:
                self.prediction_1h = 0

        if pm_10_2h is not None:
            if pm_10_2h < threshold_pm_10 and pm_25_2h < threshold_pm_25:
                self.prediction_2h = 1
            else:
                self.prediction_2h = 0

        if pm_10_3h is not None:
            if pm_10_3h < threshold_pm_10 and pm_25_3h < threshold_pm_25:
                self.prediction_3h = 1
            else:
                self.prediction_3h = 0

    def useData(self):
        # I have received a line from the serial port. I can use it
        if len(self.inbuffer) < 3:  # at least header, size, footer
            return False
        # split parts
        if self.inbuffer[0] != b'\xff':
            return False

        val = int.from_bytes(self.inbuffer[2], byteorder='little')
        print("valore sensore: ", val)
        # Se è la prima volta che il valore viene aggiornato avverto il server che avvertirà il client

        if self.windowState != val and val != 2 and val != 3 and val != 4:
            self.windowState = val
            # Send the data to the Server
            value_returned = self.post_state(self.windowState)
            print("E' cambiato lo stato della finestra (da Arduino) con ritorno: ", value_returned)

    def get_pollution(self):
        url = f'{server_ip}/api/v1/predictions?region={self.region}'
        # myid = {'region': self.region}
        pollution_values = requests.get(url)
        print("Valori dal DB: ", pollution_values.json())
        return pollution_values.json()

    def post_state(self, status):
        # I send the state and the uuid to the server
        url = server_ip + '/api/v1/sensor/status'
        myinfo = {'id': self.uuid_Arduino, 'status': status, 'region': self.region}
        value_sent = requests.post(url, json=myinfo)
        return value_sent


if __name__ == '__main__':
    db = Database()
    sp = SetupConnection()
    br = Bridge()
    _ = MQTT(br.broker_ip, br.uuid_Arduino, br.ser)
    br.loop()
