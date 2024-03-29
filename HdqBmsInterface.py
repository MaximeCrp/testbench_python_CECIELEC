from threading import Thread
from mySerial import Hdq

class HdqBmsInterface():
    """
        implements a HDQ protocol interface to the BMS bq34z100-G1 for testing purpose
    """

    def __init__(self, cmd_current = [0x10, 0x11], cmd_voltage = [0x08, 0x09], cmd_i2c = [0x00, 0xe7, 0x29]):
        """
            initialize commands and aggregate an Hdq device
        """
        self.hdq = Hdq("BMS HDQ")
        self.cmd_current = cmd_current
        self.cmd_voltage = cmd_voltage
        self.cmd_i2c = cmd_i2c
        
    def read_voltage(self):
        """
            returns a voltage read from the voltage register of the BMS via HDQ protocol
        """
        self.hdq.open_serial()
        b1 = self.hdq.read_reg(self.cmd_voltage[0])
        b2 = self.hdq.read_reg(self.cmd_voltage[1])
        bytearr = bytes([b1, b2])
        value = Hdq.uint16le(b1, b2)
        print("value: 0x%04X" % value)
        self.hdq.close_serial()
        return(int.from_bytes(bytearr, byteorder = 'little', signed = False))

    def read_current(self):
        """
            returns a current read from the current register of the BMS via HDQ protocol
        """
        self.hdq.open_serial()
        b1 = self.hdq.read_reg(self.cmd_current[0])
        b2 = self.hdq.read_reg(self.cmd_current[1])
        bytearr = bytes([b1, b2])
        value = Hdq.uint16le(b1, b2)
        print("value: 0x%04X" % value)
        self.hdq.close_serial()
        return(int.from_bytes(bytearr, byteorder = 'little', signed = True))
