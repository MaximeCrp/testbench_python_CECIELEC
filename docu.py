import sys
import glob
import serial

def ListPorts_old(cls):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        #result.append("dummy") #pour pas que le gui bug quand il ny a pas dinterface serie
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
ListPorts_old = classmethod(ListPorts_old)

def test_relais():
    a = mySerial.Serial()
    a.select_serial()
    print(a.open_serial())

    """
    print("x50")
    a.write('x50'.encode())
    sleep(1)
    print("x51")
    a.write('x51'.encode())
    """
    
    """
    sleep(1)
    command=b'\x50'
    a.write(command)

    sleep(1)
    command=b'\x51'
    a.write(command)
    """
    sleep(1)
    bits = [0,1,0,0,0,0,0,0]
    code = convert(bits)
    a.write(code)


    sleep(1)
    bits = [1,1,1,1,1,1,1,1]
    code = convert(bits)
    a.write(code)

    sleep(1)
    bits = [0,1,0,0,0,0,0,0]
    code = convert(bits)
    a.write(code)

    sleep(1)
    bits = [1,1,1,1,1,1,1,1]
    code = convert(bits)
    a.write(code)

    """
    sleep(1)
    command=b'\xFD'
    a.write(command)

    sleep(1)
    command=b'\xFF'
    a.write(command)

    sleep(1)
    code = '\x01'
    a.write(code.encode())

    
    """
    """
        sleep(1)
        command=b"00000001"
        print("00000001")
        a.write(command)

        sleep(1)
        command=b"00000000"
        a.write(command)
    """
    """
    """
    sleep(1)
    print(a.close_serial())