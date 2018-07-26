#!/usr/bin/python

# hdq over uart implementation
# based on http://www.ti.com/lit/an/slua408a/slua408a.pdf
# (c) 2017 jens jensen

"""
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

import serial
import argparse
import binascii
import ctypes

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", action="store_true")
ap.add_argument("-f","--file", help="csvfile containing reg info")
args = ap.parse_args()

ser = serial.Serial('COM22', 57600, stopbits=2, timeout=1)

HDQ_BIT1 = 0xFE
HDQ_BIT0 = 0xC0
HDQ_BIT_THRESHOLD = 0xF8

def reset():
    #reset
    ser.send_break()
    ser.read()

def write_byte(byte):
    #convert and write 8 data bits
    buf = bytearray()
    for i in range(8):
        if (byte & 1) == 1:
                buf.append(HDQ_BIT1)
        else:
                buf.append(HDQ_BIT0)
        byte = byte >> 1
    if args.debug:
        print("sending:", binascii.hexlify(buf))
    ser.write(buf)
    # chew echoed bytes
    ser.read(8)

def write_bytes(byte):
    #convert and write 8 data bits
    buf = bytearray()
    for i in range(16):
        if (byte & 1) == 1:
                buf.append(HDQ_BIT1)
        else:
                buf.append(HDQ_BIT0)
        byte = byte >> 1
    if args.debug:
        print("sending:", binascii.hexlify(buf))
    ser.write(buf)
    # chew echoed bytes
    ser.read(8)

def read_byte():
    #read and convert 8 data bits
    buf = ser.read(8)
    buf = bytearray(buf)
    # lsb first, so reverse:
    buf.reverse()
    if args.debug:
        print("recv buf:", binascii.hexlify(buf))
    byte = 0
    for i in range(8):
        byte = byte << 1
        if buf[i] > HDQ_BIT_THRESHOLD:
            byte = byte | 1       
    return byte

def uint16le(bl, bh):
    word = bh << 8 | bl
    return word

def read_reg(reg):
    write_byte(reg)
    return read_byte()

def write_reg(reg, byte):
    write_byte(0x80 | reg)
    write_byte(byte)

def write_cmd(reg, cmd):
    write_byte(0x80 | reg)
    write_bytes(cmd)

def bytes_to_dec(bytes, byteorder = 'big', signed = False):
        return(int.from_bytes(bytes, byteorder = byteorder, signed = signed))

def read_voltage()
#main
if __name__ == '__main__':
    #reset()
    #demo
    b1 = read_reg(0x08)
    b2 = read_reg(0x09)
    a = bytes([b1, b2])
    print(int.from_bytes(a, byteorder = 'little', signed = False))
    value = uint16le(b1, b2)
    print("value: 0x%04X" % value)
    """
    write_reg(0x00, 0xe7)
    write_reg(0x01, 0x29)
    """
    
