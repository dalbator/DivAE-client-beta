import json
import configparser
import socket
import threading
from threading import Timer
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
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    onoff = -1;
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.IN, pull_up_down = GPIO.PUD_UP)
        onoff = GPIO.input(int(pgpio));

    return str(onoff);

def getGPIOOutputStatus(pgpio):
    #is gpioout on or off
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    onoff = -1;
    #print("getGPIOOutputstatus");
    #print(pgpio);
    if(GOTGPIO == True):
        try:
            onoff = GPIO.input(int(pgpio));
        except:
            print("GPIO exception (it is setup?)");

    return str(onoff);

def getGPIOOutputStatusVerbose(pgpio):
    #is gpioout on or off
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    onoff = "-1";
    #print("getGPIOOutputstatus");
    #print(pgpio);
    if(GOTGPIO == True):
        try:
            onoff = GPIO.input(int(pgpio));
            if(onoff ==  0):
                onoff = "True"
            else:
                onoff = "False"
        except:
            print("GPIO exception (it is setup?)");

    return onoff;

def initOutputGPIO(pgpio):
    if(GPIO_SETTED == False):
        setupGPIO();
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.OUT)
        #print("gpio is")
        #print(pgpio)
        # 1 is off
        GPIO.output(int(pgpio), 1)

def setGPIOOutput(pgpio, value):
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.OUT)
        GPIO.output(pgpio, value)

def setGPIOHigh(pgpio):
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    if(GOTGPIO == True):
        print("setting gpio HIGH");
        print(pgpio)
        print(int(pgpio));
        GPIO.setup(int(pgpio), GPIO.OUT)
        GPIO.output(int(pgpio), GPIO.HIGH);

def setGPIOLow(pgpio):
    global GPIO_SETTED;
    global GOTGPIO;
    if(GPIO_SETTED == False):
        setupGPIO();
    if(GOTGPIO == True):
        GPIO.setup(int(pgpio), GPIO.OUT)
        GPIO.output(int(pgpio), GPIO.LOW);


class OSCommands:
    @staticmethod
    def rebootDevice():
        reboottimer = Timer(10,OSCommands.doReboot,args=["WOW"])
        reboottimer.start()
   


    @staticmethod
    def doReboot(message):
        os.system("sudo reboot");

