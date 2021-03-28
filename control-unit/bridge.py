import serial
import numpy as np
#import serial.tools.list_ports
import time
import random
from prediction import Prediction


class Bridge():

    def setup(self):
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
        print(f"connecting to {self.portname}\n")

        try:
            if self.portname is not None:
                self.ser = serial.Serial(self.portname, 9600, timeout=0)
        except Exception:
            self.ser = None

        # self.ser.open()

        # internal input buffer from serial
        self.inbuffer = []

    def loop(self):

        while (True):
            # look for a byte from serial (dati da Arduino)
            if self.ser is not None:

                if self.ser.in_waiting > 0:
                    # data available from the serial port
                    lastchar = self.ser.read(1)

                    if lastchar == b'\xfe':  # EOL
                        # print("\nValue received")
                        self.useData()
                        self.inbuffer = []
                    else:
                        # append
                        self.inbuffer.append(lastchar)

    def useData(self):
        # print(f"len {len(self.inbuffer)}")
        print(f"buff {(self.inbuffer)}")
        if len(self.inbuffer) < 3:  # at least header, size, footer
            return False
        if self.inbuffer[0] != b'\xff':  # Start of packet
            return False

        # Packet that stars with xff, has size 3 and ends with xfe
        # numval = int.from_bytes(self.inbuffer[1], byteorder='little')
        # print(f"numval {numval}")

        concentration_PM25_ugm3 = int.from_bytes(
            self.inbuffer[2], byteorder='little', signed=False)
        concentration_PM10_ugm3 = int.from_bytes(
            self.inbuffer[3], byteorder='little', signed=False)

        concentration_PM25_ugm3 = np.interp(
            concentration_PM25_ugm3, [0, 253], [0, 500])
        concentration_PM10_ugm3 = np.interp(
            concentration_PM10_ugm3, [0, 253], [0, 500])

        print(f"PM25 = {concentration_PM25_ugm3}")
        print(f"PM10 = {concentration_PM10_ugm3}\n")


if __name__ == '__main__':
    br = Bridge()
    pr = Prediction()
    # br.setup()
    # br.loop()

    # TEST WITHOUT ARDUINO
    starttime = time.time()
    while True:
        sensorValuePM25 = random.uniform(0, 100)
        sensorValuePM10 = random.uniform(0, 100)
        pr.prediction(sensorValuePM25, sensorValuePM10)
        time.sleep(60.0 - ((time.time() - starttime) %
                   60.0))  # do every 60 sec
