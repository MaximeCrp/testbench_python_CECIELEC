from I2cBmsInterface import I2cBmsInterface
from HdqBmsInterface import HdqBmsInterface

class BMS :
    """ class for BMS to test on the testbench
    """
    def __init__(self):
        self.cmd_current = [0x10, 0x11]
        self.cmd_voltage = [0x08, 0x09]
        self.cmd_hdq = [0x00, 0x40, 0x7c]
        self.cmd_i2c = [0x00, 0xe7, 0x29]
        self.i2c = I2cBmsInterface(self.cmd_current, self.cmd_voltage, self.cmd_hdq)
        self.hdq = HdqBmsInterface(self.cmd_current, self.cmd_voltage, self.cmd_i2c)