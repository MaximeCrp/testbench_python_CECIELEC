from I2cBmsInterface import I2cBmsInterface
from HdqBmsInterface import HdqBmsInterface

class BMS :
    """ 
        class for testing BMS bq34z100-G1 on the testbench
    """
    def __init__(self):
        """
            initialize commands for current and voltage control
        """
        self.cmd_current = [0x10, 0x11]
        self.cmd_voltage = [0x08, 0x09]
        self.cmd_remain_capacity = [0x04, 0x05]
        self.cmd_maximum_capacity = [0x06, 0x07]
        self.cmd_hdq = [0x00, 0x40, 0x7c]
        self.cmd_i2c = [0x00, 0xe7, 0x29]
        self.i2c = I2cBmsInterface(self.cmd_current, self.cmd_voltage, self.cmd_hdq)
        self.hdq = HdqBmsInterface(self.cmd_current, self.cmd_voltage, self.cmd_i2c)