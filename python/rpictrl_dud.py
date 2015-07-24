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


import time
relay1 = False;
relay2 = False;

class RPIController:
    
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
        retval = False;
        global relay1;
        global relay2;
        if(relay == 0):
            retval =  relay1;
        elif(relay == 1):
            retval = relay2;
        
        return retval;
        

    def open(self, relay):
        global relay1;
        global relay2;
        if(relay == 0):
            relay1 = True;
        elif(relay == 1):
            relay2 = True;
        
        
    def close( self, relay ):
        global relay1;
        global relay2;
        if(relay == 0):
            relay1 = False;
        elif(relay == 1):
            relay2 = False;
        
    

    def turnalloff(self):
      self.close(0)
      self.close(1)

    def start(self):
      #pass p.init()
      self.turnalloff()

    def stop(self):
         self.turnalloff()
        
