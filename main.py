import datetime
import myADC
import RelayCard
import mySerial
from time import sleep
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController
from array import array
from binascii import hexlify
import pyftdi.serialext
from threading import Thread
import sys
from I2cBmsInterface import I2cBmsInterface


def bonjour() :
    date_now = datetime.datetime.now()
    date_format = date_now.strftime('%d/%m/%Y')
    fileC = open("dates.log", 'a')
    fileC.close()
    with open("dates.log", 'r') as fileR :
        whole_file = fileR.read()
        lines = whole_file.split('\n')
    if lines[len(lines)-2] != date_format :
        print("\nBonjour opérateur !\n")
        with open("dates.log", 'a') as fileW :
            fileW.write(date_format + "\n")
    else :
        print("\nRe cher collègue !\n")

def main() :
    bonjour()
    test_i2c()
    #test_multimetre()
    test_relais()

def test_multimetre():
    voltage = myADC.multimeter("voltmetre")
    voltage.select_HID()
    voltage.read_multimeter_values()
    voltage.find_value()
    V, U = voltage.value
    print(V,U)

def test_relais():
    #port = mySerial.Serial.select_serial("relai 1")
    card = RelayCard.RelayCard()
    for i in range(1,9):
        sleep(2)
        card.close(i)
    card.open_all()

def test_i2c():
    bms = I2cBmsInterface()
    print(bms.read_voltage())

def test_serial():
    # Open a serial port on the second FTDI device interface (IF/2) @ 3Mbaud
    port0 = pyftdi.serialext.serial_for_url('ftdi:///1', baudrate=9600)
    port1 = pyftdi.serialext.serial_for_url('ftdi://ftdi:4232:FTY1X8SU/1', baudrate=9600)


    sr0 = Sender(port0, "port0")
    rr0 = Receiver(port0, "port0")
    sr1 = Sender(port1, "port1")
    rr1 = Receiver(port1, "port1")
 
    sr0.start()
    rr0.start()
    sr1.start()
    rr1.start()

    
    sr0.join()
    rr0.join()
    sr1.join()
    rr1.join()


    """
    # Send bytes
    port.write(b'0x50')
    sleep(1)
    port.write(b'0x51')
    sleep(1)
    port.write(b'0xFF')
    sleep(1)
    port.write(b'0x00')
    """
    # Receive bytes
    #print(port.read(1))
    port0.close()
    port1.close()

class Sender(Thread):
    def __init__(self, port, name):
        Thread.__init__(self)
        self.port = port
        self.name = name
    
    def run(self):
        i = 0
        while i<5:
            sleep(1)
            self.port.write(self.name.encode())
            i += 1

class Receiver(Thread):
    def __init__(self, port, name):
        Thread.__init__(self)
        self.port = port
        self.name = name
    
    def run(self):
        data = self.port.read(5)
        print(self.name, data)

def test_ftdi():
    
    i2c = I2cController()
    i2c.configure('ftdi://ftdi:4232:FT30VMWS/1', frequency = 400000)
    dev = i2c._ftdi
    
    """
    dev = Ftdi()
    dev.open_from_url('ftdi://ftdi:4232:FTY1X8SU/1') 
    dev.write_data(b'0x50')
    sleep(1)
    dev.write_data(b'0x51')
    sleep(1)
    dev.write_data(b'0xFF')
    sleep(1)
    dev.write_data(b'0x00')
    #dev.enable_3phase_clock(True)
    """
    
    data = bytearray(1)
    #data[0] = 0xAA
    data[0] = 0x00
    #data[1] = 0x7c
    #data[2] = 0x40
    
    write_custom(0x55, data, dev, False)
    #print(read_custom(0x55, dev))
    #dev.write_data(data)
    print(dev.read_data_bytes(10))
    dev.close()
    """
    
    # Instanciate an I2C controller
    i2c = I2cController()

    # Configure the first interface (IF/1) of the FTDI device as an I2C master
    #i2c.configure('ftdi://ftdi:4232:FTY1X8SU/1', frequency = 400000) ### /0 marche aussi
    i2c.configure('ftdi://ftdi:4232:FT30VMWS/1', frequency = 400000) ### /0 marche aussi

    # Get a port to an I2C slave device
    address = 0x55 ### 7 premiers bits de 0xAA/0xAB
    slave = i2c.get_port(address)
    """
    """
    success = 0
    while(success != 1):
        try:
            print("essai : " , address)
            slave = i2c.get_port(address)
            success = 1
            print("succès sur : ", address)
        except:
            success =0
            address +=1
        finally:
            if address>128:
                slave.close()
                break
    """
    """
    slave.write_to(0, b'\x7c40')
    # Read a register from the I2C slave
    #slave.read_from(0x00, 2) ### start byte, 2 to read
    """
    
    
def read_custom(address, ftdi, readlen=1, relax=True):
        """Read one or more bytes from a remote slave

           :param address: the address on the I2C bus, or None to discard start
           :type address: int or None
           :param int readlen: count of bytes to read out.
           :param bool relax: not used
           :return: read bytes
           :rtype: array
           :raise I2cIOError: if device is not configured or input parameters
                              are invalid

           Address is a logical slave address (0x7f max)

           Most I2C devices require a register address to read out
           check out the exchange() method.
        """
        if address is None:
            i2caddress = None
        else:
            i2caddress = (address << 1) & 0xff
            i2caddress |= 0x01
        retries = 3
        do_epilog = True
        while True:
            try:
                _do_prolog(i2caddress, ftdi)
                data = _do_read(readlen, ftdi)
                do_epilog = relax
                return data
            except :
                retries -= 1
                if not retries:
                    print('Retry read')
            finally:
                if do_epilog:
                    _do_epilog(ftdi)

def write_custom(address, out, ftdi, relax=True):
        """Write one or more bytes to a remote slave

           :param address: the address on the I2C bus, or None to discard start
           :type address: int or None
           :param out: the byte buffer to send
           :type out: array or bytes or list(int)
           :param bool relax: whether to relax the bus (emit STOP) or not
           :raise I2cIOError: if device is not configured or input parameters
                              are invalid

           Address is a logical slave address (0x7f max)

           Most I2C devices require a register address to write into. It should
           be added as the first (byte)s of the output buffer.
        """
        i2caddress = (address << 1) & 0xff
        i2caddress |= 0x01 #### read register
        retries = 3
        do_epilog = True
        while True:
            try:
                _do_prolog(i2caddress, ftdi)
                _do_write(out, ftdi)
                do_epilog = relax
                return
            except :
                print('nack')
                retries -= 1
                if not retries:
                    raise 
            finally:
                if do_epilog:
                    _do_epilog(ftdi)

class MyException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


def _do_prolog(i2caddress, ftdi):
        print('   prolog 0x%x', i2caddress >> 1)
        cmd = array('B', (128, 255, 3))
        cmd.extend((128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3))
        cmd.extend((17, 0, 0))
        cmd.append(i2caddress)
        if (128, 0, 1):
            cmd.extend((128, 0, 1))
            cmd.extend((34, 0))
            cmd.extend((128, 254, 3))
        """
        else:
            cmd.extend(self._clk_lo_data_hi)
            cmd.extend(self._read_bit)
        """
        cmd.extend((135,))
        ftdi.write_data(cmd)
        ack = ftdi.read_data_bytes(1, 4)
        if not ack:
            print('No answer from FTDI')
        if ack[0] & 0x01:
            print('NACK')
            print('NACK from slave')

def _do_epilog(ftdi):
    print('   epilog')
    cmd = array('B', (128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 252, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 253, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3, 128, 255, 3))
    ftdi.write_data(cmd)
    # be sure to purge the MPSSE reply
    ftdi.read_data_bytes(1, 1)

def _do_read(readlen, ftdi):
    print('- read %d byte(s)', readlen)
    if not readlen:
        # force a real read request on device, but discard any result
        cmd = array('B')
        cmd.extend((135,))
        ftdi.write_data(cmd)
        ftdi.read_data_bytes(0, 4)
        return array('B')
    if (128, 0, 1):
        read_byte = (128, 0, 1) + \
                    (32, 0, 0) + \
                    (128, 254, 3)
        read_not_last = \
            read_byte + (19, 0, 0) + (128, 252, 3) * 10
        read_last = \
            read_byte + (19, 0, 255) + (128, 254, 3) * 10
    """
    else:
        read_not_last = \
            (32, 0, 0) + (19, 0, 0) + \
            self._clk_lo_data_hi * self._ck_delay
        read_last = \
            self._read_byte + self._nack + \
            self._clk_lo_data_hi * self._ck_delay
    """
    # maximum RX size to fit in FTDI FIFO, minus 2 status bytes
    chunk_size = 2048-2
    cmd_size = len(read_last)
    # limit RX chunk size to the count of I2C packable commands in the FTDI
    # TX FIFO (minus one byte for the last 'send immediate' command)
    tx_count = (2048-1) // cmd_size
    chunk_size = min(tx_count, chunk_size)
    chunks = []
    cmd = None
    rem = readlen
    while rem:
        if rem > chunk_size:
            if not cmd:
                cmd = array('B')
                cmd.extend(read_not_last * chunk_size)
                size = chunk_size
        else:
            cmd = array('B')
            cmd.extend(read_not_last * (rem-1))
            cmd.extend(read_last)
            cmd.extend((135,))
            size = rem
        ftdi.write_data(cmd)
        buf = ftdi.read_data_bytes(size, 4)
        print('- read %d byte(s): %s',
                        len(buf), hexlify(buf).decode())
        chunks.append(buf)
        rem -= size
    return array('B', b''.join(chunks))

def _do_write(out, ftdi):
    if not isinstance(out, array):
        out = array('B', out)
    if not out:
        return
    print('- write %d byte(s): %s',
                    len(out), hexlify(out).decode())
    for byte in out:
        cmd = array('B', (17, 0, 0))
        cmd.append(byte)
        if (128, 0, 1):
            cmd.extend((128, 0, 1))
            cmd.extend((34, 0))
            cmd.extend((128, 254, 3))
        else:
            cmd.extend((128, 254, 3))
            cmd.extend((34, 0))
        cmd.extend((135,))
        ftdi.write_data(cmd)
        ack = ftdi.read_data_bytes(1, 4)
        if not ack:
            msg = 'No answer from FTDI'
            print(msg)
        if ack[0] & 0x01 :
            msg = 'NACK from slave'
            print(msg)


if __name__ == "__main__" :
    main()