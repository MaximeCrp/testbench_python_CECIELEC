import serial
import sys
import glob
import serial.tools.list_ports

if sys.version_info >= (3,):
    # as is, don't handle unicodes
    unicode = str
    raw_input = input
else:
    # allow to show encoded strings
    import codecs
    sys.stdout = codecs.getwriter('mbcs')(sys.stdout)

class Serial(serial.Serial) :
    """ class for serial communications
    """
    def __init__(self, name, port = None):
        super().__init__()
        #port = Serial.select_serial(name)
        if port == None :
            self.port = Serial.select_serial(name)
        else :
            self.port = port
        #self.xonxoff = True
        self.custom_name = name

    @staticmethod 
    def ListPorts():
        return [comport.device for comport in serial.tools.list_ports.comports()]

    @staticmethod
    def select_serial(custom_name):
        all_serial = Serial.ListPorts()
        if all_serial:
            while True:
                print("Sélectionner l'appareil correspondant à : " + custom_name + "\n")
                for index, device in enumerate(all_serial):
                    print("{0} => {1}".format(index+1, device))
                index_option = raw_input()
                if index_option.isdigit() and int(index_option) <= len(all_serial):
                    # invalid
                    break
            int_option = int(index_option)
            if int_option:
                return all_serial[int_option-1]
        else:
            print("Pas de périphérique USB Série trouvé")

    def open_serial(self):
        self.open()
        return(self.is_open)

    def close_serial(self):
        self.close()
        return(self.is_open==0)

class Hdq(Serial):
    """ class for HDQ communications over a serial port
    """
    
    def __init__(self, name, port = None):
        super().__init__(name, port)
        self.baudrate = 57600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_TWO
        
    def read_reg(self, reg, size = 1):
        self.write('\x00\xc0\xc0\xC0\xFE\xc0\xc0\xC0'.encode())
        print(self.read(16))

if __name__ == "__main__":
    bms = Hdq("bms")
    print(bms.open_serial())
    bms.read_reg(0x00)
    bms.close_serial()
        

