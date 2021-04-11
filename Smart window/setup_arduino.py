from serial.tools.list_ports import comports
from serial import Serial
import platform


def get_serial_port():
    portname = ''
    if platform.system() == 'Linux':
        ports = comports()
        for port in ports:
            print(port.device)
            if 'tty' in port.device.lower():
                portname = port.device

        return portname

    elif platform.system() == 'Windows':
        ports = comports()
        for port in ports:
            print(port.device)
            print(port.description)
            if 'arduino' in port.description.lower():
                portname = port.device
        return portname


class SetupConnection:

    def __init__(self):
        self.setupSerial()

    # Connection
    def setupSerial(self):
        # open serial port
        self.ser = None
        print("list of available ports: ")

        self.portname = get_serial_port()

        print("connecting to " + self.portname)

        try:
            if self.portname is not None:
                self.ser = Serial(self.portname, 9600, timeout=0)
        except Exception:
            self.ser = None

        # self.ser.open()

        # internal input buffer from serial
        self.inbuffer = []
        return self.inbuffer, self.ser
