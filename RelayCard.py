import mySerial
from time import sleep

class RelayCard:
    
    def __init__(self, name = "relay1", port = None):
        port = mySerial.Serial.select_serial(name)
        if port == None : ### à ne pas mettre ici, mais bug pour l'instant sinon
            port = mySerial.Serial.select_serial(name)
        self.ser = mySerial.Serial(name, port)
        self.name = name
        self.relays = self.init_relays()
        self.ser.open()
        self.ser.write('\x50'.encode())
        sleep(1)
        self.ser.write('\x51'.encode())

    def __del__(self):
        self.ser.close()

    def init_relays(self):
        return [1,1,1,1,1,1,1,1]

    def toggle(self, index, apply = True):
        if type(index) == list :
            for i in index :
                self.toggle(i, False)
        else :
            index = -index
            self.relays[index] = 1 - self.relays[index-1]
        if apply:
            self.apply()

    def close(self, index, apply = True):
        if type(index) == list :
            for i in index :
                self.close(i, False)
        else :
            index = -index
            self.relays[index] = 0
        if apply:
            self.apply()

    def open(self, index, apply = True):
        if type(index) == list :
            for i in index :
                self.open(i, False)
        else :
            index = -index
            self.relays[index] = 1
        if apply:
            self.apply()

    def close_all(self, apply = True):
        self.close([1,2,3,4,5,6,7,8], False)
        if apply:
            self.apply()

    def open_all(self, apply = True):
        self.open([1,2,3,4,5,6,7,8], False)
        if apply:
            self.apply()

    def apply(self):
        self.ser.write(self.get_serial_cmd())
        sleep(1)

    def get_serial_cmd(self):
        byt = ""
        bytelist = []
        for bit in self.relays:
            byt += str(bit)
        bytelist.append(int(byt,2))
        return bytes(bytelist)
