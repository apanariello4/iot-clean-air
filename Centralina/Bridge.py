import serial
import numpy as np
import urllib.request

## configuration
PORTNAME = 'COM5'

class Bridge():

    def setup(self):
        self.ser = serial.Serial(PORTNAME, 9600, timeout=0)
        #self.ser.open()
        self.inbuffer = []


    def loop(self):
        while(True):

            if self.ser.in_waiting > 0:
                lastchar = self.ser.read(1)

                if lastchar == b'\xfe': #End of packet
                    print("\nValue received")
                    self.useData()
                    self.inbuffer = []
                else:
                    self.inbuffer.append(lastchar)


    def useData(self):
        if len(self.inbuffer) < 3: #at least header, size, footer
            return False
        if self.inbuffer[0] != b'\xff': #Start of packet
            return False

        #Packet that stars with xff, has size 3 and ends with xfe
        numval = int.from_bytes(self.inbuffer[1], byteorder='little')
        for i in range(numval):
            val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
            print("Sensor " + i + ": " + val)


if __name__== '__main__':
    br = Bridge()
    br.setup()
    br.loop()