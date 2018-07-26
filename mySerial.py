import serial
import sys
import glob
import serial.tools.list_ports
import binascii

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

    MIT License

    Copyright (c) 2017 Jens J.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """
    HDQ_BIT1 = 0xFE
    HDQ_BIT0 = 0xC0
    HDQ_BIT_THRESHOLD = 0xF8

    def __init__(self, name, port = None):
        super().__init__(name, port)
        self.baudrate = 57600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_TWO

    def reset(self):
        #reset
        self.send_break()
        self.read()

    def write_byte(self, byte):
        #convert and write 8 data bits
        buf = bytearray()
        for i in range(8):
            if (byte & 1) == 1:
                    buf.append(Hdq.HDQ_BIT1)
            else:
                    buf.append(Hdq.HDQ_BIT0)
            byte = byte >> 1
        print("sending:", binascii.hexlify(buf))
        self.write(buf)
        # chew echoed bytes
        self.read(8)

    def write_bytes(self, byte):
        #convert and write 8 data bits
        buf = bytearray()
        for i in range(16):
            if (byte & 1) == 1:
                    buf.append(Hdq.HDQ_BIT1)
            else:
                    buf.append(Hdq.HDQ_BIT0)
            byte = byte >> 1
        print("sending:", binascii.hexlify(buf))
        self.write(buf)
        # chew echoed bytes
        self.read(8)

    def read_byte(self):
        #read and convert 8 data bits
        buf = self.read(8)
        buf = bytearray(buf)
        # lsb first, so reverse:
        buf.reverse()
        print("recv buf:", binascii.hexlify(buf))
        byte = 0
        for i in range(8):
            byte = byte << 1
            if buf[i] > Hdq.HDQ_BIT_THRESHOLD:
                byte = byte | 1       
        return byte

    @staticmethod
    def uint16le(bl, bh):
        word = bh << 8 | bl
        return word

    def read_reg(self, reg):
        self.write_byte(reg)
        return self.read_byte()

    def write_reg(self, reg, byte):
        self.write_byte(0x80 | reg)
        self.write_byte(byte)

    def write_cmd(self, reg, cmd):
        self.write_byte(0x80 | reg)
        self.write_bytes(cmd)

    @staticmethod
    def bytes_to_dec(bytes, byteorder = 'big', signed = False):
            return(int.from_bytes(bytes, byteorder = byteorder, signed = signed))

    

    if __name__ == "__main__":
        bms = Hdq("bms")
        print(bms.open_serial())
        bms.read_reg(0x00)
        bms.close_serial()
            

