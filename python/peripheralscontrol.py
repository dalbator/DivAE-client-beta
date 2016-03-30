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
from peripherals import LocalPeripherals
import time
from datetime import datetime, timedelta
import pdb

#remove _dud for production
from piface_ctrl import RPIFaceDigitalController
from rpictrl import getGPIOInput
#from rpictrl import setGPIOOutput
from rpictrl import setGPIOHigh
from rpictrl import setGPIOLow

from schedules import Schedules
from schedules import ScheduleObject
from schedules import PeripheralSchedulesObject

from commandprocessor import SharedInstances;


class PeripheralTimerObject:
    peripheral = None
    timestarted = None
    minutes = None

    peripheralSchedules = [] # array of PeriperalSchedulesObject
    
    def __init__(self, peripheral, minutes):
        self.peripheral = peripheral
        self.minutes = minutes
        self.timestarted = datetime.now();

    def isExpired(self):
        retval = False
        now = datetime.now();
        duration = now - self.timestarted;
 #       pdb.set_trace()
        
        if((duration.seconds/60) > self.minutes):
            retval = True
        return retval

    def getDeviceID(self):
        return self.peripheral.devid;

    def getPeripheralSerialID(self):
        return self.peripheral.serialid;

    def getPeripheralType(self):
        return self.peripheral.ptype;

    def getPeripheralGPIO(self):
        return self.peripheral.pgpio;

    def useGPIO(self):
        retval = False;
        if(self.peripheral.pgpio != -1):
            retval = True;
        return retval;


def switch_callback(bcmchanel):
    # Send change to the server immediatelly
    print("switch callback called")
    print("change: " + str(bcmchanel));
    value = getGPIOInput(bcmchanel);
    print(value);
    SharedInstances.static_commandProcessor.beginPostSwitchEvent(str(bcmchanel),value);
    
    

class PeripheralController:
    exitThread = False
    tlock = None
    log = None
    MOD_NAME = "PERCON"
    dbgcounter = 0;
    piFaceController = None
    
    peripheralThread = None

    loadSchedule = False
    localPeripherals = None


    p_timers = []
    p_pschedules = []  #PeripheralSchedulesObject

    
    def __init__(self):
        self.log = Logger("logs/controllerlog","txt", True)
        self.piFaceController = RPIFaceDigitalController()
        self.tlock = threading.Lock()




    def join(self):
        if(self.peripheralThread != None):
            self.peripheralThread.join()
        
    def threaded_function(self):
        self.localPeripherals = LocalPeripherals(self.log)
        self.localPeripherals.load()
        self.localPeripherals.initSwitchPeripherals(switch_callback);
        self.setLoadSchedules()
        self.exitThread  = False
        self.log.write(self.MOD_NAME, "starting timer thread loop for peripheral controls")
        while self.exitThread == False:
            self.checkSchedules()
            # timer override the schedules in case it is on
            self.checkTimers()
            if(self.dbgcounter == 2):
                self.dbgcounter = 0
                message = ""
                if(self.p_timers == None):
                    message = message + "No timer"
                else:
                    count = len(self.p_timers)
                    message = message + str(count) + " timer(s)"
                    
                self.log.write(self.MOD_NAME, "loop: "+ message)
            self.dbgcounter+= 1 
            time.sleep(5)
        self.log.write(self.MOD_NAME, "exiting thread loop")

 #       self.testCallback();


    def testCallback(self):
        switch_callback(4);

    
    def getPeripheralStatus(self, port):
        retval = "off"
        if(self.piFaceController.getPortStatus(int(port))):
            retval = "on"
        return retval;
    
    def getSummaryVerbose(self):
        text = "";
        port1 = self.piFaceController.getPortStatus(0);
        port2 = self.piFaceController.getPortStatus(1);
        if(port1):
            text = "Valve 1 is on.";
        else:
            text = "Valve 1 is off.";

        if(port2):
            text += " Valve 2 is on.";
        else:
            text += " Valve 2 is off.";

        return text;

    def turnOffPeripheral(self, peripheralObject):
        # remove all timers associate to this peripheral
        self.tlock.acquire()
        if(self.p_timers != None):
            try:
                self.log.write(self.MOD_NAME, "turn off peripheral");
                count = len(self.p_timers);
                for i in range(count-1,-1,-1):
                    pto = self.p_timers[i];
                    portid = pto.getPeripheralSerialID();
#                    self.log.write(self.MOD_NAME, "here");
                    self.log.write(self.MOD_NAME,type(pto.peripheral));
                    self.log.write(self.MOD_NAME,type(peripheralObject));
                    if(peripheralObject.devid == pto.peripheral.devid):
                        #delete
                        self.log.write(self.MOD_NAME, "turn off (deleting)");
                        self.turnPeripheralOff(pto.peripheral);
 #                       if(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_RELAY):
#                            setGPIOLow(self.pto.getPeripheralGPIO());
#                        elif(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_PIFACE_RELAY):
#                            self.piFaceController.turnOffOutput(int(portid))
                        del self.p_timers[i]
            except:
                self.log.write(self.MOD_NAME, "turn off peripheral. exception");
                
        self.tlock.release()


    def addOneTimer(self, peripheralObject, duration):
        pto = PeripheralTimerObject(peripheralObject, duration)
        self.log.write(self.MOD_NAME, "init relay timer for: "+ str(duration));
        self.tlock.acquire()
        self.p_timers.append(pto)
 #       pdb.set_trace()
        self.tlock.release()


    def checkTimers(self):
 #       pdb.set_trace()
        self.tlock.acquire()
        if(self.p_timers != None):
 #           self.log.write(self.MOD_NAME, "got timer");
            count = len(self.p_timers);
            for i in range(count-1,-1,-1):
                pto = self.p_timers[i];
                portid = pto.getPeripheralSerialID();
                if(pto.isExpired() == True):
                    #delete
                    self.log.write(self.MOD_NAME, "Turning off (expired)");
                    self.turnPeripheralOff(pto.peripheral);
                   # if(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_RELAY):
#                        setGPIOLow(pto.getPeripheralGPIO());
#                    elif(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_PIFACE_RELAY):
#                        self.piFaceController.turnOffOutput(int(portid))
#                    else:
#                        self.log.write(self.MOD_NAME, "Not action (A) for peipheral type:" + pto.getPeripheralType());
                        
                    del self.p_timers[i]
                else:
                    self.turnPeripheralOn(pto.peripheral);
                    #if(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_RELAY):
#                        self.log.write(self.MOD_NAME, "Turning on GPIO ");
#                        self.log.write(self.MOD_NAME, pto.getPeripheralGPIO());
#                        setGPIOHigh(pto.getPeripheralGPIO());
#                    elif(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_PIFACE_RELAY):
#                        self.log.write(self.MOD_NAME, "Turning on (PIFACE) ");
#                        self.piFaceController.turnOnOutput(int(portid))
#                    else:
#                        self.log.write(self.MOD_NAME, "Not action (B) for peipheral type:" + pto.getPeripheralType());
                    
                    #turn on
        self.tlock.release()

    def setLoadSchedules(self):
        self.tlock.acquire()
        self.loadSchedule = True
        self.tlock.release()


    _schedulesmessagecounter = 0
    
    def checkSchedules(self):
        
        if(self.loadSchedule == True):
            self.loadSchedule = False
            self.loadSchedules()
        self.tlock.acquire()
        for periSched in self.p_pschedules:
 #           pdb.set_trace()
            if(periSched != None):
                periobj = self.localPeripherals.findPeripheral(periSched._peripheralID)
                if(periSched.isItTime() == True):
                    if(self._schedulesmessagecounter == 20):
                        self._schedulesmessagecounter = 0;
                        self.log.write(self.MOD_NAME, "**** schedule to open peripheral ****")
                    self._schedulesmessagecounter = self._schedulesmessagecounter + 1

                    self.log.write(self.MOD_NAME, "schedule turning valve on" +  periobj.serialid)
                    self.turnPeripheralOn(periobj);
#                    self.rpiController.turnOnOutput(int(periobj.serialid)) 
                else:
                    self.turnPeripheralOff(periobj);
#                    self.rpiController.turnOffOutput(int(periobj.serialid))

        self.tlock.release()

    def turnPeripheralOn(self, periobj):
        if(periobj.ptype == LocalPeripherals.PERI_TYPE_OUT_RELAY):
            self.log.write(self.MOD_NAME, "Turning on GPIO ");
            self.log.write(self.MOD_NAME, periobj.pgpio);
            setGPIOHigh(pto.getPeripheralGPIO());
        elif(periobj.ptype == LocalPeripherals.PERI_TYPE_OUT_PIFACE_RELAY):
            self.log.write(self.MOD_NAME, "Turning on (PIFACE relay) ");
            self.piFaceController.turnOnOutput(int(periobj.serialid))
        else:
            self.log.write(self.MOD_NAME, "Not action (B) for peipheral type:" + pto.getPeripheralType());

    def turnPeripheralOff(self, periobj):
        if(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_RELAY):
            self.log.write(self.MOD_NAME, "Turning OFF GPIO ");
            setGPIOLow(periobj.pgpio);
        elif(pto.getPeripheralType() == LocalPeripherals.PERI_TYPE_OUT_PIFACE_RELAY):
            self.log.write(self.MOD_NAME, "Turning OFF (PIFACE relay) ");
            self.piFaceController.turnOffOutput(int(periobj.serialid))
        else:
            self.log.write(self.MOD_NAME, "Not action (A) for peipheral type:" + pto.getPeripheralType());

    def loadSchedules(self):
        self.tlock.acquire()
        self.p_pschedules = []
        self.log.write(self.MOD_NAME, "----  load schedules")
        peripherals = self.localPeripherals.getPeripherals()
        sce = Schedules(self.log)
        for periObj in peripherals:
            schedules = sce.loadSchedulesForPeripheral(periObj.devid)
            self.p_pschedules.append(schedules)
            
            
            

        self.tlock.release()
            

    def startThread(self):
        if(self.peripheralThread == None):
            self.peripheralThread = Thread(target = self.threaded_function, args = [])
            self.peripheralThread.start()
            
    def stopThread(self):
        self.piFaceController.stop();
        if(self.peripheralThread != None):
            with self.tlock:
                self.exitThread  = True
        
     
  


