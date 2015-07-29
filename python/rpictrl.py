import json
import configparser
import socket
import threading
import os
import sys
import traceback
#from peripherals import LocalPeripherals
#from iseclogger import Logger
from threading import Thread
#from peripherals import PeripheralObject
import time
import datetime
import pdb

GOTGPIO = True;
try:
    import RPi.GPIO as GPIO
except ImportError:
    GOTGPIO = False;
    print("GPIO module note found");
    
#sudo apt-get install python3-pifacedigital-emulator
GOTPIFACE = True;
try:
    import pifacedigitalio
except ImportError:
    print("PIFACE module not found");
    GOTPIFACE = False;

import time


GPIO_SETTED = False;
def setupGPIO():
    global GPIO_SETTED;
    global GOTGPIO;
    if((GPIO_SETTED == False) and (GOTGPIO == True)):
        GPIO.setmode(GPIO.BCM)
        GPIO_SETTED = True;

def addGPIOEvent(pgpio, fcallback):
    setupGPIO();
    #print("fake: adding GPIO event for: "+ pgpio)
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(int(pgpio), GPIO.BOTH, callback=fcallback, bouncetime=300);


def getGPIOInput(pgpio):
    onoff = -1;
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.IN, pull_up_down = GPIO.PUD_UP)
        onoff = GPIO.input(int(pgpio));

    return str(onoff);

class RPIFaceDigitalController:
    p = None;
    
    def __init__(self):
        self.start()

    def getPortStatus(self, portid):
        retval = False;
        if(portid == 0 or portid == 1): # fail safe
            retval = self.isOn(portid)
        return retval
            
    def turnOnOutput(self, portid):
        if(portid == 0 or portid == 1): # fail safe
            self.open(portid)

    def turnOffOutput(self, portid):
        if(portid == 0 or portid == 1): # fail safe
            self.close(portid)

    def isOn(self, relay):

        intval = self.p.relays[relay].value;
 
        retval = False;
        if(intval == 1):
            retval = True;
		
        return retval;

    def open(self, relay):
        if(self.p != None):
            self.p.relays[relay].value = 1;

    def close( self, relay ):
        if(self.p != None):
            self.p.relays[relay].value = 0; 

    def turnalloff(self):
        self.close(0)
        self.close(1)

    def start(self):
        if(GOTPIFACE):
            self.p = pifacedigitalio.PiFaceDigital()
            self.turnalloff()

    def stop(self):
        if(self.p != None):
            self.p.deinit_board();
            self.p = None;
        
