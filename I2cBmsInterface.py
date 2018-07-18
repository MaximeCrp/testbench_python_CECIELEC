from myFTDI import I2cDevice
import ctypes
from time import sleep

class I2cBmsInterface():

    def __init__(self):
        self.address = 0b1010101 # 0b1010101 fixed address of the bq34z100-g1
        self.channel = 0
        self.bq = I2cDevice(self.address, self.channel) 
        self.reg_ctrl = 0x00
        self.cmd_current = [0x10, 0x11]
        self.cmd_voltage = [0x08, 0x09]

    def read_current(self):
        if not self.bq.open_channel():
            print("Impossible d'ouvrir le canal I2C de la BMS")
            self.bq.close_channel()
            return
        ret, value = self.bq.send_command(self.cmd_current, 2)
        val_dec = I2cDevice.bytes_to_dec(value, 'little', True)
        if not ret:
            print("Impossible de lire le registre courant du BMS")
            self.bq.close_channel()
            return
        else:
            self.bq.close_channel()
            return val_dec

    def read_voltage(self):
        if not self.bq.open_channel():
            print("Impossible d'ouvrir le canal I2C de la BMS")
            self.bq.close_channel()
            return
        ret, value = self.bq.send_command(self.cmd_voltage, 2)
        val_dec = I2cDevice.bytes_to_dec(value, 'little', False)
        if not ret:
            print("Impossible de lire le registre tension du BMS")
            self.bq.close_channel()
            return
        else:
            self.bq.close_channel()
            return val_dec

    def __repr__(self):
        return("adresse : {}, channel : {}, device : {}, ctrl : {}, courant : {}, tension : {}".format(
            self.address, self.channel, self.bq, self.reg_ctrl, self.cmd_current, self.cmd_voltage))

if __name__ == '__main__':
    test = I2cBmsInterface()
    print(test.read_voltage())
    sleep(2)
    print(test.read_current())
    sleep(2)
    print(test.read_voltage())
    sleep(5)
    print(test.read_voltage())
    sleep(2)
    print(test.read_current())
    sleep(5)
    print(test.read_voltage())
    sleep(2)
    print(test.read_current())