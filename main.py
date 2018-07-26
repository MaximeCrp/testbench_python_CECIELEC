import datetime
import os
from time import sleep
from threading import Thread
from I2cBmsInterface import I2cBmsInterface
from Tester import Tester
from myADC import InterfaceADC, Multimeter
from RelayCard import RelayCard


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
    #test_i2c()
    #test_multimetre()
    #test_relais()
    test_tester()

def test_tester():
    tester = Tester()
    os.system("clear")
    if not tester.setup():
        return
    if not tester.reveil():
        return
    if not tester.liberer_leds():
        return
    if not tester.switch_18():
        return
    if not tester.switch_5():
        return
    if not tester.switch_12():
        return
    if not tester.switch_9():
        return
    if not tester.charge_rapide():
        return
    if not tester.charge_normale():
        return
    if not tester.batterie_faible():
        return
    if not tester.batterie_min():
        return
    if not tester.batterie_max():
        return
    if not tester.jack_debranche():
        return

    pass
def test_multimetre():
    voltage = Multimeter("voltmetre")
    voltage.select_HID()
    voltage.read_multimeter_values()
    voltage.find_value()
    V, U = voltage.value
    print(V,U)

def test_relais():
    card = RelayCard()
    for i in range(1,9):
        sleep(2)
        card.close(i)
    card.open_all()

def test_i2c():
    bms = I2cBmsInterface()
    print(bms.read_voltage())
    sleep(2)
    print(bms.read_current())

if __name__ == "__main__" :
    main()