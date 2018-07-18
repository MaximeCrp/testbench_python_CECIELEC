import ctypes
from time import sleep

class ChannelConfig(ctypes.Structure):
    _fields_ = [("ClockRate",   ctypes.c_int),
                ("LatencyTimer",ctypes.c_ubyte),
                ("Options",     ctypes.c_int)]

class I2C_TRANSFER_OPTION(object):
    START_BIT           = 0x01
    STOP_BIT            = 0x02
    BREAK_ON_NACK       = 0x04
    NACK_LAST_BYTE      = 0x08
    FAST_TRANSFER_BYTES = 0x10
    FAST_TRANSFER_BITS  = 0x20
    FAST_TRANSFER       = 0x30
    NO_ADDRESS          = 0x40   

class I2cFTDI():
    """
    allows to use FTDI devices and evaluation boards such as the FT4232H as master devices over the I²C protocol to communicate with slave devices
    """ 
    libMPSSE           = ctypes.cdll.LoadLibrary("libMPSSE.dll") # use of the MPSSE library from FTDI which allows synchronous protocols on FTDI devices
    chn_count          = ctypes.c_int()

    def __init__(self, chn_no = 0, clockrate = 100000):    
        self.chn_conf           = ChannelConfig(clockrate, 5, 0) # clockrate à confirmer  # commenter le LatencyTimer = 5 et Options = 0
        self.chn_no             = chn_no # channels 0 ( = A ) et 1 ( = B ) configurables en MPSSE (dont i2C) grâce à FT_Prog 
        self.handle             = ctypes.c_void_p()
        self.bytes_transfered   = ctypes.c_int()
        self.options            = I2C_TRANSFER_OPTION() ## S = Start, P = stoP
        self.modeS              = I2C_TRANSFER_OPTION.START_BIT  # START-bit only, used for register reading purposes
        self.modeSP             = I2C_TRANSFER_OPTION.START_BIT|I2C_TRANSFER_OPTION.STOP_BIT # START and STOP-bits
        self.modeP              = I2C_TRANSFER_OPTION.STOP_BIT # STOP-bit
        self.retO               = -1 # return value for opening functions
        self.retI               = -1 # return value for initialization functions
        self.retW               = -1 # return value for writing functions
        self.retR               = -1 # return value for reading functions 
        self.retC               = -1 # return value for closing functions 
    
    @classmethod
    def get_nb_channels(cls):
        ret = cls.libMPSSE.I2C_GetNumChannels(ctypes.byref(cls.chn_count))
        return(ret, cls.chn_count)

    def open_channel(self):
        self.retO = I2cFTDI.libMPSSE.I2C_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        self.retI = I2cFTDI.libMPSSE.I2C_InitChannel(self.handle, ctypes.byref(self.chn_conf))
        return(self.retO == 0 and self.retI == 0) # ret value of 0 means no error encountered 

    def read_register(self, address, reg):
        bufT_len = 1
        bufT = ctypes.create_string_buffer(bufT_len)
        bufR_len = 1
        bufR = ctypes.create_string_buffer(bufR_len)
        bufT[0] = reg
        self.retW = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, address, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
        self.retR = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, address, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
        return(self.retW == 0 and self.retR == 0, bufR[0]) # ret value of 0 means no error encountered

    def write_register(self, address, reg, value):
        bufT_len = 2
        bufT = ctypes.create_string_buffer(bufT_len)
        bufT[0] = reg
        bufT[1] = value
        self.retW = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, address, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
        return(self.retW == 0) # ret value of 0 means no error encountered

    def write_verify_register(self, address, reg, value):
        """
        return : 0 read value = written value
                 1 read value != written value
                 2 reading unsuccessful
                 3 writing unsuccessful
        """
        if self.write_register(address, reg, value):
            ret, reg_val = self.read_register(address, reg)
            if not ret == 1 :
                return 2
            else :
                return(not reg_val == value)
        else :
            return 3

    def send_command(self, address, cmd, lenR):
        bufT_len = len(cmd)
        bufR_len = 1
        bufT = ctypes.create_string_buffer(bufT_len)
        bufR = ctypes.create_string_buffer(bufR_len)
        bufOut = bytearray()
        for i in range(bufT_len):
            bufT[i] = cmd[i]
        self.retW = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, address, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
        for i in range(lenR-1):
            self.retR = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, address, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeS) # repeated start sans stop avant, pour garder la main sur le bus
            bufOut.append(int.from_bytes(bufR[0], byteorder='big', signed=False))
            if not self.retR == 0:
                return(False,bufOut) 
        self.retR = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, address, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
        bufOut.append(int.from_bytes(bufR[0], byteorder='big', signed=False))
        return(self.retW == 0 and self.retR == 0, bufOut)
        
    def close_channel(self):
        self.retC = I2cFTDI.libMPSSE.I2C_CloseChannel(self.handle)
        return(self.retC == 0)

    def test1(self):

        while(True):

            bufT_len = 1
            bufT = ctypes.create_string_buffer(3)
            bufR_len = 1
            bufR = ctypes.create_string_buffer(bufR_len)
            bufT[0] = 0x00
            bufT[1] = 0x7C
            bufT[2] = 0x40

            I2Caddress = 0b1010101 #0b1100000  #0b1100010 #0b1010101 

            ret = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
            print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
            ret = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
            print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
            for i in range(bufR_len):
                print(bufR[i])

            bufT_len = 3
            ret= I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
            print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)

            bufT_len = 1
            ret = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
            print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
            ret = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
            print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
            for i in range(bufR_len):
                print(bufR[i])
            sleep(1)

    def test2(self):
        I2Caddress = 0b1100000  #0b1100010 #0b1010101 
        print(self.read_register(I2Caddress, 0x26)[1])
        print(self.write_verify_register(I2Caddress, 0x26, 0xB8))

    def test3(self):
        I2Caddress = 0b1010101
        bufT_len = 1
        bufT = ctypes.create_string_buffer(2)
        bufR_len = 2
        bufR = ctypes.create_string_buffer(bufR_len)
        bufT[0] = 0x0
        bufT[1] = 0xB8
        ret = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
        print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
        ret = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
        print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
        for i in range(bufR_len):
            print(bufR[i])

    def test4(self):
        I2Caddress = 0b1010101
        bufT_len = 2
        bufR_len = 1
        bufT = ctypes.create_string_buffer(bufT_len)
        bufR = ctypes.create_string_buffer(bufR_len)
        bufT[0] = 0x10
        bufT[1] = 0x11
        ret = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
        print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
        """
        bufT[0] = 0x11
        ret = I2cFTDI.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, 1, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
        print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
        """
        ret = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeS) # repeated start sans stop avant, pour garder la main sur le bus
        print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
        for i in range(bufR_len):
            print(bufR[i])
        ret = I2cFTDI.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, 2, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
        print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
        for i in range(bufR_len):
            print(bufR[i])

#testé : écriture de 2 SP puid lecture de 2 SP : LSByte reçu, MSByte :: FF
# à tester : écriture de 1 SP puis lecture de 1 SP, puis encore
# écriture de 2 SP et deux lectures de 1 SP (ou S puis SP)

    def test5(self):
        I2Caddress = 0b1010101
        cmd = [0x08, 0x09]
        out = self.send_command(I2Caddress, cmd, 2)[1]
        print(out)
        outInt = I2cDevice.bytes_to_dec(out, 'little', True)
        print(outInt)

    def __repr__(self):
        return("self.chn_conf :{}, self.chn_no :{}, self.handle :{}, self.bytes_transfered :{}, self.options :{}, self.modeS :{}, self.modeSP :{}, self.modeP :{}, self.retO :{}, self.retI :{}, self.retW :{}, self.retR :{}, self.retC :{}".format(
            self.chn_conf, self.chn_no, self.handle, self.bytes_transfered, self.options, self.modeS, self.modeSP, 
            self.modeP, self.retO, self.retI, self.retW, self.retR, self.retC))

class I2cDevice():

    def __init__(self, address, channel = 0, clockrate = 100000):
        self.master = I2cFTDI(channel, clockrate)
        self.address = address

    def open_channel(self):
        return(self.master.open_channel())

    def read_register(self, reg):
        return(self.master.read_register(self.address, reg))

    def write_register(self, reg, value):
        return(self.master.write_register(self.address, reg, value))

    def write_verify_register(self, reg, value):
        return(self.master.write_verify_register(self.address, reg, value))

    def send_command(self, cmd, lenR):
        return(self.master.send_command(self.address, cmd, lenR))

    def close_channel(self):
        return(self.master.close_channel())

    @staticmethod
    def bytes_to_dec(bytes, byteorder = 'big', signed = False):
        return(int.from_bytes(bytes, byteorder = byteorder, signed = signed))

    def __repr__(self):
        return("master  :{}, address :{}".format(self.master, self.address))

if __name__ == "__main__":
    """
    baro = I2cDevice(0b1100000) # 0b1100000 address of the MPL3115A2 barometer
    print(baro.open_channel())
    print(baro.write_verify_register(0x26, 0xB8))
    """
    ftdi = I2cFTDI()
    ftdi.open_channel()
    ftdi.test5()
    ftdi.test5()

"""
read register :
while(True):
    ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, bufT_len, bufT, ctypes.byref(bytes_transfered), modeS)
    print("I2C_DeviceWrite status:",ret, "transfered:",bytes_transfered)
    ret = libMPSSE.I2C_DeviceRead(handle, I2Caddress, bufR_len, bufR, ctypes.byref(bytes_transfered), modeSP) # repeated start sans stop avant, pour garder la main sur le bus
    print("I2C_DeviceRead status:",ret, "received:", bufR, bytes_transfered)
    for i in range(bufR_len):
        print(buf[i])
    sleep(1)
"""