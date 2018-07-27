from BMS import BMS
from RelayCard import RelayCard
from myADC import Multimeter
import os
import sys

class Tester():

    def __init__(self):
        self.bms = BMS()
        self.relais1 = RelayCard("relais 1")
        self.relais2 = RelayCard("relais 2")
        self.voltmetre = Multimeter("voltmètre")
        self.voltmetre.unit = 'V'
        self.amperemetre = Multimeter("ampèremètre")
        self.amperemetre.unit = 'A'

        self.voltmetre.select_HID()
        self.amperemetre.select_HID()
        # définition des numéros des relais (carte,relai)
        self.Jack       =   (1,1)
        self.Rout       =   (1,2)
        self.USB        =   (1,3)
        self.Ibat       =   (1,4)
        self.BatHL      =   (1,5)
        self.BatVH      =   (1,6)
        self.LED_R      =   (2,1)
        self.LED_G      =   (2,2)
        self.LED_B      =   (2,3)
        self.I2C_V      =   (2,5)
        self.I2C_SDA    =   (2,6)
        self.I2C_SCL    =   (2,7)

        self.tests = [0 for i in range(33)]

        self.test_setup = 1
        self.test_connexion = 2
        self.test_alimentation = 3
        self.test_reveil_vout = 4
        self.test_cpmmunication = 5


        self.test_leds = 10
        self.test_18_vout = 11
        self.test_18_a = 12
        self.test_5_vout = 13
        self.test_5_a = 14
        self.test_12_vout = 15
        self.test_12_a = 16
        self.test_9_vout = 17
        self.test_9_a = 18
        self.test_led_bleue = 19
        self.test_charge_rapide_a = 20
        self.test_charge_normale_a = 21
        self.test_batterie_faible_vout = 22
        self.test_batterie_faible_ibat = 23
        self.test_led_rouge = 24
        self.test_batterie_min_v = 25

        self.test_leds_turquoise = 27
        self.test_batterie_max_v = 28
        
        self.test_batterie_max_vout = 30
        self.test_jack_debranche_vout = 31
        self.test_jack_debranche_ibat = 32

    def fermer_relais(self, *args):
        for i in args:
            if i[0] == 1:
                self.relais1.close(i[1])
            else:
                self.relais2.close(i[1])

    def ouvrir_relais(self, *args):
        for i in args:
            if i[0] == 1:
                self.relais1.open(i[1])
            else:
                self.relais2.open(i[1])

    def setup(self):
        print("\n" + " SETUP ".center(80, '*'), "\nVoltmètre calibre continu, ampèremètre calibre µA, RANGE = 200, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.relais1.open_all()
        self.relais2.open_all()
        self.fermer_relais(self.Rout, self.BatHL, self.I2C_SCL, self.I2C_SDA, self.I2C_V)
        print("\n" + " SETUP ".center(80, '*'), "\nAllumer alimentation 24V et 5V, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.tests[self.test_setup - 1] = 1
        self.tests[self.test_connexion - 1] = 1
        self.tests[self.test_alimentation - 1] = 1
        return True
        
    def reveil(self):
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.LED_R, self.LED_G, self.LED_B)
        self.fermer_relais(self.Rout, self.BatHL, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Jack)
        print("\n" + " REVEIL ".center(80, '*'), "\nAppuyer sur le bouton réveil, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 0.5:
            self.tests[self.test_reveil_vout - 1] = 1
        else:
            print("\n" + " ERREUR REVEIL ".center(80, '#'), "\nVout (voltmètre) nul mesuré au réveil " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True

    def liberer_leds(self):
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Rout)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B)
        print("\n" + " LEDS ".center(80, '*'), "\nRétroéclairage de l'interface USB après appui sur réveil ?", "\n".ljust(80, '*'), "\n")
        print("0. Oui".ljust(0,' '), "1. Non".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            print("\n" + " ERREUR LEDS ".center(80, '#'), "\nPas de rétroéclairage des LEDS", "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        else:
            self.tests[self.test_leds - 1] = 1
        return True

    def switch_18(self): 
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Rout)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B)
        print("\n" + " DIP SWITCH 18V ".center(80, '*'), "\nMettre tout à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 18-18*0.05 and self.voltmetre.value[0] < 18+18*0.05:
            self.tests[self.test_18_vout - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 18V ".center(80, '#'), "\nVout (voltmètre) incorrect mesuré avec tout en OFF : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        courant = self.bms.hdq.read_current()
        if courant > -141-141*0.1 and courant < -141+141*0.1:
            self.tests[self.test_18_a - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 18V ".center(80, '#'), "\nIbat (ampèremètre) incorrect mesuré avec tout en OFF : " + courant, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True
        
    def switch_5(self): 
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Rout)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B)
        print("\n" + " DIP SWITCH 5V ".center(80, '*'), "\nMettre 1 à ON et le reste à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 5-5*0.05 and self.voltmetre.value[0] < 5+5*0.05:
            self.tests[self.test_5_vout - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 5V ".center(80, '#'), "\nVout (voltmètre) incorrect mesuré avec 1 à ON et reste à OFF : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        courant = self.bms.hdq.read_current()
        if courant > -9-9*0.1 and courant < -9+9*0.1:
            self.tests[self.test_5_a - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 5V ".center(80, '#'), "\nCourant incorrect mesuré avec 1 à ON et reste à OFF : " + courant, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True

    def switch_12(self): 
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Rout)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B)
        print("\n" + " DIP SWITCH 12V ".center(80, '*'), "\nMettre 3 à ON et le reste à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 12-12*0.05 and self.voltmetre.value[0] < 12+12*0.05:
            self.tests[self.test_12_vout - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 12V ".center(80, '#'), "\nVout (voltmètre) incorrect mesuré avec 3 à ON et reste à OFF : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        courant = self.bms.hdq.read_current()
        if courant > -53-53*0.1 and courant < -53+53*0.1:
            self.tests[self.test_12_a - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 12V ".center(80, '#'), "\nCourant incorrect mesuré avec 3 à ON et reste à OFF : " + courant, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True

    def switch_9(self): 
        self.ouvrir_relais(self.USB, self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.Rout)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B)
        print("\n" + " DIP SWITCH 9V ".center(80, '*'), "\nMettre 2 à ON et le reste à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 9-9*0.05 and self.voltmetre.value[0] < 9+9*0.05:
            self.tests[self.test_9_vout - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 9V ".center(80, '#'), "\nVout (voltmètre) incorrect mesuré avec 2 à ON et reste à OFF : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        courant = self.bms.hdq.read_current()
        if courant > -28-28*0.1 and courant < -28+28*0.1:
            self.tests[self.test_9_a - 1] = 1
        else:
            print("\n" + " ERREUR DIP SWITCH 9V ".center(80, '#'), "\nCourant incorrect mesuré avec 2 à ON et reste à OFF : " + courant, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True
            
    def charge_rapide(self):
        self.ouvrir_relais(self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B, self.USB, self.Rout)
        print("\n" + " CHARGE RAPIDE ".center(80, '*'), "\nMettre 2 et 4 à ON et le reste à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        print("\n" + " LEDS CHARGE RAPIDE ".center(80, '*'), "\nRétroéclairage bleu de l'interface USB ?", "\n".ljust(80, '*'), "\n")
        print("0. Oui".ljust(0,' '), "1. Non".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            print("\n" + " ERREUR LED BLEUE ".center(80, '#'), "\nPas de rétroéclairage bleu des LEDS", "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        else:
            self.tests[self.test_led_bleue - 1] = 1
        courant = self.bms.hdq.read_current()
        if courant > 667-667*0.1 and courant < -667+667*0.1:
            self.tests[self.test_charge_rapide_a - 1] = 1
        else:
            print("\n" + " ERREUR CHARGE RAPIDE ".center(80, '#'), "\nCourant incorrect mesuré avec USB-5V allumé, 2 et 4 à ON et reste à OFF : " + str(courant), "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True

    def charge_normale(self):
        self.ouvrir_relais(self.Ibat, self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL)
        self.fermer_relais(self.BatHL, self.Jack, self.LED_R, self.LED_G, self.LED_B, self.USB, self.Rout)
        print("\n" + " CHARGE NORMALE ".center(80, '*'), "\nMettre 2 à ON et le reste à OFF sur le DIP-SWITCH, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        courant = self.bms.hdq.read_current()
        if courant > 500-500*0.1 and courant < -500+500*0.1:
            self.tests[self.test_charge_normale_a - 1] = 1
        else:
            print("\n" + " ERREUR CHARGE NORMALE ".center(80, '#'), "\nCourant incorrect mesuré avec USB-5V allumé, 2 à ON et reste à OFF : " + courant, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True

    def batterie_faible(self):
        self.ouvrir_relais(self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.USB, self.BatHL)
        self.fermer_relais(self.Jack, self.LED_R, self.LED_G, self.LED_B, self.Rout, self.Ibat)
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 0-0.05 and self.voltmetre.value[0] < 0+0.05:
            self.tests[self.test_batterie_faible_vout - 1] = 1
        else:
            print("\n" + " ERREUR COUPURE BATTERIE FAIBLE ".center(80, '#'), "\n Vout (voltmètre) incorrect mesuré avec Bat_Low : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        self.amperemetre.read_multimeter_values()
        self.amperemetre.find_value()
        if self.amperemetre.value[0] == 0:
            self.tests[self.test_batterie_faible_ibat - 1] = 1
        else:
            print("\n" + " ERREUR COUPURE BATTERIE FAIBLE ".center(80, '#'), "\nIbat (ampèremètre) incorrect mesuré avec Bat_Low : " + str(self.amperemetre.value[0]) + self.amperemetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True
                
    def batterie_min(self):
        self.ouvrir_relais(self.BatVH, self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.USB, self.BatHL, self.Ibat)
        self.fermer_relais(self.Jack, self.LED_R, self.LED_G, self.LED_B, self.Rout)
        print("\n" + " BATTERIE MINI ".center(80, '*'), "\nMaintenir le bouton réveil, OK ?", "\n".ljust(80, '*'), "\n")
        print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            return False
        print("\n" + " LEDS BATTERIE MINI ".center(80, '*'), "\nRétroéclairage rouge de l'interface USB ?", "\n".ljust(80, '*'), "\n")
        print("0. Oui".ljust(0,' '), "1. Non".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            print("\n" + " ERREUR LED ROUGE ".center(80, '#'), "\nPas de rétroéclairage rouge des LEDS" + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        else:
            self.tests[self.test_led_rouge - 1] = 1
        tension = self.bms.hdq.read_voltage()
        if tension > 2500-2500*0.05 and tension < -2500+2500*0.05:
            self.tests[self.test_batterie_min_v - 1] = 1
        else:
            print("\n" + " ERREUR BATTERIE MINI".center(80, '#'), "\nTension incorrecte mesurée avec Bat_Low allumé : " + tension, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True
    
    def batterie_max(self):
        self.ouvrir_relais(self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.USB, self.Ibat)
        self.fermer_relais(self.Jack, self.LED_R, self.LED_G, self.LED_B, self.Rout, self.BatHL, self.BatVH)
        print("\n" + " LEDS BATTERIE MAXI ".center(80, '*'), "\nRétroéclairage turquoise de l'interface USB ?", "\n".ljust(80, '*'), "\n")
        print("0. Oui".ljust(0,' '), "1. Non".rjust(70,' '))
        if int(input(" >>  ")) == 1:
            print("\n" + " ERREUR LEDS BLEUE et VERTE ".center(80, '#'), "\nPas de rétroéclairage turquoise des LEDS", "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        else:
            self.tests[self.test_leds_turquoise - 1] = 1
        tension = self.bms.hdq.read_voltage()
        if tension > 3700-3700*0.05 and tension < -3700+3700*0.05:
            self.tests[self.test_batterie_max_v - 1] = 1
        else:
            print("\n" + " ERREUR BATTERIE MAXI".center(80, '#'), "\nTension incorrecte mesurée avec Bat_VeryHigh allumé : " + tension, "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 9-9*0.05 and self.voltmetre.value[0] < 9+9*0.05:
            self.tests[self.test_batterie_max_vout - 1] = 1
        else:
            print("\n" + " ERREUR BATTERIE MAXI ".center(80, '#'), "\nVout (voltmètre) incorrect mesuré avec Bat_VeryHigh : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True
    
    def jack_debranche(self):
        self.ouvrir_relais(self.I2C_V, self.I2C_SDA, self.I2C_SCL, self.USB, self.BatVH)
        self.fermer_relais(self.Jack, self.LED_R, self.LED_G, self.LED_B, self.Rout, self.BatHL, self.Ibat)
        self.voltmetre.read_multimeter_values()
        self.voltmetre.find_value()
        if self.voltmetre.value[0] > 0-0.05 and self.voltmetre.value[0] < 0+0.05:
            self.tests[self.test_jack_debranche_vout - 1] = 1
        else:
            print("\n" + " ERREUR JACK DÉBRANCHÉ ".center(80, '#'), "\nVout (voltmètre) non nul mesuré avec jack débranché : " + str(self.voltmetre.value[0]) + self.voltmetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        self.amperemetre.read_multimeter_values()
        self.amperemetre.find_value()
        if self.amperemetre.value[0] == 0:
            self.tests[self.test_jack_debranche_ibat - 1] = 1
        else:
            print("\n" + " ERREUR JACK DÉBRANCHÉ ".center(80, '#'), "\nIbat (ampèremètre) incorrect mesuré avec jack débranché : " + str(self.amperemetre.value[0]) + self.amperemetre.value[1], "\n".ljust(80, '#'), "\n")
            print("0. Continuer...".ljust(0,' '), "1. Quitter.".rjust(70,' '))
            if int(input(" >>  ")) == 1:
                return False
        return True