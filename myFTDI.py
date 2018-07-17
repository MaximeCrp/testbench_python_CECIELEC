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

class I2C_FTDI():
    """
    allows to use FTDI devices and evaluation boards such as the FT4232H as master devices over the I²C protocol to communicate with slave devices
    """ 
    def __init__(self, chn_no = 0, clockrate = 100000):    
        self.libMPSSE           = ctypes.cdll.LoadLibrary("libMPSSE.dll") # use of the MPSSE library from FTDI which allows synchronous protocols on FTDI devices
        self.chn_count          = ctypes.c_int()
        self.chn_conf           = ChannelConfig(clockrate, 5, 0) # clockrate à confirmer
                                                                 # commenter le LatencyTimer = 5 et Options = 0
        self.chn_no             = chn_no # channels 0 ( = A ) et 1 ( = B ) configurables en MPSSE (dont i2C) grâce à FT_Prog 
        self.handle             = ctypes.c_void_p()
        self.bytes_transfered   = ctypes.c_int()
        """
        bufT[0]                 = 0x26 # 0x0C : who am i register (fixed device id number) of MPL3115A2 = 0xC4 reset value
        bufT[1]                 = 0xB8
        """
        self.options            = I2C_TRANSFER_OPTION()
        ## S = Start, P = stoP
        self.modeS              = I2C_TRANSFER_OPTION.START_BIT  # START-bit only, used for register reading purposes
        self.modeSP             = I2C_TRANSFER_OPTION.START_BIT|I2C_TRANSFER_OPTION.STOP_BIT # START and STOP-bits
        self.retO               = -1 # return value for opening functions
        self.retI               = -1 # return value for initialization functions
        self.retW               = -1 # return value for writing functions
        self.retR               = -1 # return value for reading functions 
        self.retC               = -1 # return value for closing functions 
    
    @staticmethod
    def get_nb_channels():
        ret = self.libMPSSE.I2C_GetNumChannels(ctypes.byref(self.chn_count))
        return(ret, self.chn_count)

    def open_channel(self):
        self.retO = self.libMPSSE.I2C_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        self.retI = self.libMPSSE.I2C_InitChannel(self.handle, ctypes.byref(self.chn_conf))
        return(self.retO == 0 and self.retI == 0) # ret value of 0 means no error encountered 

    def read_register(self, address, reg):
        bufT_len = 1
        bufT = ctypes.create_string_buffer(bufT_len)
        bufR_len = 1
        bufR = ctypes.create_string_buffer(bufR_len)
        bufT[0] = reg
        self.retW = self.libMPSSE.I2C_DeviceWrite(self.handle, address, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
        self.retR = self.libMPSSE.I2C_DeviceRead(self.handle, address, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
        return(self.retW == 0 and self.retR == 0, bufR[0]) # ret value of 0 means no error encountered

    def write_register(self, address, reg, value):
        bufT_len = 2
        bufT = ctypes.create_string_buffer(bufT_len)
        bufT[0] = reg
        bufT[1] = value
        self.retW = self.libMPSSE.I2C_DeviceWrite(self.handle, address, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)
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

    def close_channel(self):
        self.retC = self.libMPSSE.I2C_CloseChannel(self.handle)
        return(self.retC == 0)

    def test1(self):

        while(True):

            bufT_len = 1
            bufT = ctypes.create_string_buffer(2)
            bufR_len = 1
            bufR = ctypes.create_string_buffer(bufR_len)
            bufT[0] = 0x26
            bufT[1] = 0xB8

            I2Caddress = 0b1100000  #0b1100010 #0b1010101 

            ret = self.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
            print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
            ret = self.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
            print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
            for i in range(bufR_len):
                print(bufR[i])

            bufT_len = 2
            ret= self.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeSP)

            bufT_len = 1
            ret = self.libMPSSE.I2C_DeviceWrite(self.handle, I2Caddress, bufT_len, bufT, ctypes.byref(self.bytes_transfered), self.modeS)
            print("I2C_DeviceWrite status:",ret, "transfered:",self.bytes_transfered)
            ret = self.libMPSSE.I2C_DeviceRead(self.handle, I2Caddress, bufR_len, bufR, ctypes.byref(self.bytes_transfered), self.modeSP) # repeated start sans stop avant, pour garder la main sur le bus
            print("I2C_DeviceRead status:",ret, "received:", bufR, self.bytes_transfered)
            for i in range(bufR_len):
                print(bufR[i])
            sleep(1)

    def test2(self):
        I2Caddress = 0b1100000  #0b1100010 #0b1010101 
        print(self.read_register(I2Caddress, 0x26)[1])
        print(self.write_verify_register(I2Caddress, 0x26, 0xB8))


class I2C_device():

    def __init__(self, address, channel = 0, clockrate = 100000):
        self.master = I2C_FTDI(channel, clockrate)
        self.address = address

    def open_channel(self):
        return(self.master.open_channel())

    def read_register(self, reg):
        return(self.master.read_register(self.address, reg))

    def write_register(self, reg, value):
        return(self.master.write_register(self.address, reg, value))

    def write_verify_register(self, reg, value):
        return(self.master.write_verify_register(self.address, reg, value))

    def close_channel(self):
        return(self.master.close_channel())

if __name__ == "__main__":
    FT4232H = I2C_device(0b1100000)
    print(FT4232H.open_channel())
    print(FT4232H.write_verify_register(0x26, 0xB8))

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