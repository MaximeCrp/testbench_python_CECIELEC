from myI2C import I2cDevice
import ctypes
from time import sleep

class I2cBmsInterface():

    def __init__(self, cmd_current = [0x10, 0x11], cmd_voltage = [0x08, 0x09], cmd_hdq = [0x00, 0x40, 0x7c]):
        self.address = 0b1010101 # 0b1010101 fixed address of the bq34z100-g1
        self.channel = 0
        self.bq = I2cDevice(self.address, self.channel) 
        self.reg_ctrl = 0x00
        self.cmd_current = cmd_current
        self.cmd_voltage = cmd_voltage
        self.cmd_hdq = cmd_hdq

    def __repr__(self):
        return("adresse : {}, channel : {}, device : {}, ctrl : {}, courant : {}, tension : {}".format(
            self.address, self.channel, self.bq, self.reg_ctrl, self.cmd_current, self.cmd_voltage))

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

    def to_hdq(self):
        if not self.bq.open_channel():
            print("Impossible d'ouvrir le canal I2C de la BMS")
            self.bq.close_channel()
            return
        ret, value = self.bq.send_command(self.cmd_hdq, 2)
        val_dec = I2cDevice.bytes_to_dec(value, 'little', False)
        if not ret:
            print("Impossible de lire le registre tension du BMS")
            self.bq.close_channel()
            return
        else:
            self.bq.close_channel()
            return val_dec

if __name__ == '__main__':
    while(True):
        test = I2cBmsInterface()
        print(test.read_voltage())
        print(test.to_hdq())
        sleep(1.5)