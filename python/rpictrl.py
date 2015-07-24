import json
import configparser
import socket
import threading
import os
import sys
import traceback
from peripherals import LocalPeripherals
from iseclogger import Logger
from threading import Thread
from peripherals import PeripheralObject
import time
import datetime
import pdb

#import pifacedigitalio as p
import pifacedigitalio

import time


class RPIController:
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
        self.p.relays[relay].value = 1;

    def close( self, relay ):
        self.p.relays[relay].value = 0; 

    def turnalloff(self):
        self.close(0)
        self.close(1)

    def start(self):
        self.p = pifacedigitalio.PiFaceDigital()
        self.turnalloff()

    def stop(self):
        self.p.deinit_board();
        self.p = None;
        
