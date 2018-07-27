#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
"""
implementing a ADC device via USB HID connexion
"""
from time import sleep
from msvcrt import kbhit
import pywinusb.hid as hid

# first be kind with local encodings
import sys
if sys.version_info >= (3,):
    # as is, don't handle unicodes
    unicode = str
    raw_input = input
else:
    # allow to show encoded strings
    import codecs
    sys.stdout = codecs.getwriter('mbcs')(sys.stdout)

class InterfaceADC:
    
    def __init__(self, name = "basic adc"):
        self.handler = "basic_handler"
        self.name = name
        self.measures = None

    
    def basic_handler(self, data):
        self.measures = data[2]
        #print(int(data[2]))
        #print("Raw data: {0}".format(data))

    def select_HID(self):
        # simple test
        # browse devices...
        all_hids = hid.find_all_hid_devices()
        if all_hids:
            while True:
                print("Sélectionner l'appareil correspondant à : "+self.name+"\n")
                for index, device in enumerate(all_hids):
                    device_name = unicode("{0.vendor_name} {0.product_name}" \
                            "(vID=0x{1:04x}, pID=0x{2:04x})"\
                            "".format(device, device.vendor_id, device.product_id))
                    print("{0} => {1}".format(index+1, device_name))
                index_option = raw_input()
                if index_option.isdigit() and int(index_option) <= len(all_hids):
                    # invalid
                    break
            int_option = int(index_option)
            if int_option:
                self.device = all_hids[int_option-1]
                device_name = unicode("{0.vendor_name} {0.product_name}" \
                            "(vID=0x{1:04x}, pID=0x{2:04x})"\
                            "".format(self.device, self.device.vendor_id, self.device.product_id))
                print("Vous avez assigné à %s l'appareil %s" %(self.name, device_name))
        else:
            print("Pas de périphérique USB HID trouvé")

    def read_raw_values(self):
        try:
            self.device.open()

            #set custom raw data handler
            self.device.set_raw_data_handler(eval("self."+self.handler))

            print("\nWaiting for data...\nPress any (system keyboard) key to stop...")
            while not kbhit() and self.device.is_plugged():
                #just keep the device opened to receive events
                sleep(0.5)
            return
        finally:
            self.device.close()

class Multimeter(InterfaceADC) :
    """ implementing a multimeter device. The format used is the one from Tenma USB multimeters
    """

    def __init__(self, name = "multimeter", dot = 2, unit = 'V'):
        self.name = name
        self.handler = "multimeter_handler"
        self.dot = dot # the dot value allows to know where to put on the dot on the received value
        self.unit = unit

    def multimeter_handler(self, data):
            # in data list, only meaningfull values are data[1] and data[2] 
        if data[1] != 240 : # data[1] indicates whether the tram send is an actual transmission from the device (241 in that case, 240 if not)
            self.read_byte += 1

                # conversion from ASCII to int :
            if data[2] > 127 :  # some digits have an extra byte that has to be taken off
                measure_int = int(data[2]) - 176 # 176 = 128 + 48 : extra byte + regular ASCII conversion
            else :
                measure_int = int(data[2]) - 48 # regular ASCII conversion

            if self.read_byte in range(9) :
                #measure_int = (int(data[2]) - 176) if data[2]>127 else (int(data[2]) - 48)
                #self.measures[self.nb_measures][self.read_byte] = measure_int
                self.measures[self.nb_measures][self.read_byte] = measure_int

            elif self.read_byte == 10 :
                print(self)
                self.nb_measures+=1
                self.read_byte = -1
        else:
            pass
        if(self.nb_measures >= 5) :
            self.nb_measures = 0
            self.reading_enabled = 0


    def read_multimeter_values(self):
        try:
            self.device.open()
            self.reading_enabled = 1
            self.nb_measures = 0
            self.read_byte = -1
            self.measures = [ [0,0,0,0,0,0,0,0,0] for i in range(5)]
            #self.measures_1 = [0,0,0,0,0,0,0,0,0]
            #set custom raw data handler
            self.device.set_raw_data_handler(eval("self."+self.handler))
            while not kbhit() and self.device.is_plugged() and self.reading_enabled:
                #just keep the device opened to receive events
                sleep(0.5)
            return
        finally:
            self.device.close()
            #print(self.measures)
            #print(self.error)

    def find_value(self):
        while(self.reading_enabled) :
            pass
        sum = 0
        values = [0 for i in range(len(self.measures))]
        for i in range(len(self.measures)) :
            values[i] = self.convert_digits_int(self.measures[i])
            sum += values[i]
        #print(values)
        mean = sum / len(self.measures)
        #print(mean)
        self._value = mean
        #### implémenter l'envoi de l'unité ici

    def convert_digits_int(self, measure):         # [1,2,3,4,5]
        numList = map(str, measure[:5])   # ['1','2','3','4','5']
        numString = ''.join(numList)          # '12345'
        numInt = int(numString)              # 12345
        numFloat = numInt / 10**self.dot     # 123.45
        return numFloat

    def __repr__(self):
        return("values : " + str(self.measures[self.nb_measures][:5]) + \
                " , range : " +  str(self.measures[self.nb_measures][5]) + \
                " , function : " +  str(self.measures[self.nb_measures][6]) + \
                " , 8 : " + str(self.measures[self.nb_measures][7]) + \
                " , 9 : " + str(self.measures[self.nb_measures][8]))

    def _get_value(self):
        return [self._value, self.unit]
    
    def _set_value(self, new_value):
        pass

    value = property(_get_value, _set_value)

### à faire : méthode de test de l'appareil : bien configuré en fonction par rapport au nom 