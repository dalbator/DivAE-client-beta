import json
import configparser
import socket
import threading
import os
import sys
import traceback
from digtemp import read_dig_temp
sys.path.append( "../lib" )
from iseclogger import Logger


from rpiinfo import get_temperature

#remove _dud for production
from rpictrl import addGPIOEvent
from rpictrl import getGPIOInput

import pdb


class PeripheralObject:
    serialid = None
    devid = None
    name = None
    description = None
    ptype = None
    pgpio = None
    

class LocalPeripherals:

    CFG_PERI_SECTION_MAIN="main"
    CFG_PERI_SECTION_PERI="peri_{0}"
    CFG_PERI_ID = "id"
    CFG_PERI_ID_SERIAL = "id_serial"
    CFG_PERI_NAME = "name"
    CFG_PERI_DESCRIPTION = "description"
    CFG_PERI_TYPE="type"
    CFG_PERI_COUNT="count"
    CFG_PERI_GPIO="gpio"

    ST_DEV_NAME = "device_name"
    ST_DEV_ID = "device_id"
    ST_PERIPHERAL_ID = "peripheral_id"
    ST_DEV_SERIAL_ID = "device_serial_id"
    ST_DEV_TYPE = "device_type"
    ST_DEV_DESC = "device_desc"

    filename = "cfg/peripherals.cfg";
    
    log = None
    _peripherals = []
    
    def __init__(self, logger):
        self.log = logger
        
    def load(self):
        self._peripherals = []
        
        peri_config = configparser.ConfigParser()
        peri_config.read(self.filename)
        sectionmain = dict(peri_config.items(self.CFG_PERI_SECTION_MAIN))
 #       sectionmain[self.CFG_PERI_COUNT]
        pericount = int(sectionmain[self.CFG_PERI_COUNT]);
        for x in range(0,pericount):
            
            sectionkey = self.CFG_PERI_SECTION_PERI.format(x+1);
            sectionperi = dict(peri_config.items(sectionkey));
 #           self.log.write("locperi",sectionperi);
            pid = sectionperi[self.CFG_PERI_ID]
            pids = sectionperi[self.CFG_PERI_ID_SERIAL]
            pname = sectionperi[self.CFG_PERI_NAME]
            pdesc = sectionperi[self.CFG_PERI_DESCRIPTION]
            ptype = sectionperi[self.CFG_PERI_TYPE]
            
            pGPIO = -1
            if(self.CFG_PERI_GPIO in sectionperi):
                pGPIO = sectionperi[self.CFG_PERI_GPIO];
             
            self.addDevice(pid, pids, pname,pdesc,ptype,pGPIO);
        

    #Output peripherals
    PERI_TYPE_OUT_SAINTSMART_RELAY = "1";
    PERI_TYPE_OUT_SPEAKER = "2";
    PERI_TYPE_OUT_BUZZER = "3";
    PERI_TYPE_OUT_CAMERA_CONTROL = "4";
    PERI_TYPE_OUT_GRADIAN = "5";
    PERI_TYPE_OUT_SERVO = "6";
    PERI_TYPE_OUT_PIFACE_RELAY = "7";
    
    #Input peripherals
    PERI_TYPE_IN_RFI = "200";
    PERI_TYPE_IN_VIDEO_CAMERA = "201";
    PERI_TYPE_IN_BUTTON_SWITCH = "202";
    PERI_TYPE_IN_HYDROMETER = "203";
    PERI_TYPE_IN_THERMOMETER = "204";
    PERI_TYPE_IN_PITHERMOMETER = "205";
    PERI_TYPE_IN_ACCELEROMETER = "206";
    PERI_TYPE_IN_POSITIONING_LOCATION ="207";
    PERI_TYPE_IN_AMBIENT_LIGHT = "208";
    PERI_TYPE_IN_MICROPHONE = "209";
    PERI_TYPE_IN_INFRARED_CAMERA = "210";
    PERI_TYPE_IN_MOTION_SENSOR = "211";
    PERI_TYPE_IN_GEIGER_COUNTER = "212";



    STATUS = "status";

    def initSwitchPeripherals(self,switchcallback):
        # init peripherals that required it
        for po in self._peripherals:
            if(po.ptype == self.PERI_TYPE_IN_BUTTON_SWITCH):
                addGPIOEvent(po.pgpio, switchcallback);
                 
        

    def getPeripheralsStatus(self,peripheralcontroller):
        retval = [];
        for po in self._peripherals:
            if(po.ptype == self.PERI_TYPE_OUT_SAINTSMART_RELAY):
                status = peripheralcontroller.getPeripheralStatus(po.serialid)
                stat = {'' + self.ST_PERIPHERAL_ID + '':'' + po.devid
                + '',''+self.STATUS + '':'' + status+''}
                retval.append(stat)
            if(po.ptype == self.PERI_TYPE_OUT_PIFACE_RELAY):
                status = peripheralcontroller.getPeripheralStatus(po.serialid)
                stat = {'' + self.ST_PERIPHERAL_ID + '':'' + po.devid
                + '',''+self.STATUS + '':'' + status+''}
                retval.append(stat)                
            elif(po.ptype == self.PERI_TYPE_IN_PITHERMOMETER):
                tempc = get_temperature();
                stat = {''+self.ST_PERIPHERAL_ID + '':'' + po.devid
                + '',''+self.STATUS + '':'' + tempc+''}
                retval.append(stat)
            elif(po.ptype == self.PERI_TYPE_IN_BUTTON_SWITCH):
                onoff = getGPIOInput(po.pgpio)
                stat = {''+self.ST_PERIPHERAL_ID + '':'' + po.devid
                + '',''+self.STATUS + '':'' + onoff+''}
                retval.append(stat)
            elif(po.ptype == self.PERI_TYPE_IN_THERMOMETER):
                #onoff = getGPIOInput(po.pgpio)
                self.log.write("Get Peripheral status","digitemp");
                digtemp = read_dig_temp(int(po.serialid));
                stat = {''+self.ST_PERIPHERAL_ID + '':'' + po.devid
                + '',''+self.STATUS + '':'' + digtemp[0]+''}
                self.log.write("Get Peripheral status", stat);
                retval.append(stat)
                
                
                

        return retval;

    def findPeripheral(self, deviceid):
        retval = None
        
        for po in self._peripherals:
            if po.devid == deviceid:
                retval = po
                break
        return retval

    def findPeripheralByTypeAndGpio(self, ptype, pgpio):
        retval = None
        
        for po in self._peripherals:
            if (po.ptype == ptype) and (po.pgpio == pgpio):
                retval = po
                break
        return retval

    def getPeripherals(self):
        return self._peripherals
                

    def addDevice(self, deviceid, serialid, name, description, ptype, pgpio):
        po = PeripheralObject()
        po.devid = deviceid
        po.serialid = serialid
        po.name = name
        po.description = description
        po.ptype = ptype
        po.pgpio = pgpio;
        self._peripherals.append(po)

    def toJSON(self):
        retval = [];
        for po in self._peripherals:
            #po = self._peripherals[i]
            #self.log.write("locperi", po.name + po.devid)
            onePeri = { ''+self.ST_DEV_NAME+'':'' + po.name
                        + '',''+self.ST_DEV_ID + '':'' + po.devid+''
                        + '',''+self.ST_DEV_SERIAL_ID + '':'' + po.serialid+''
                        + '',''+self.ST_DEV_TYPE + '':'' + po.ptype+''
                        + '',''+self.ST_DEV_DESC + '':'' + po.description+''}
 #           self.log.write("locperi", json.dumps(onePeri))
            retval.append(onePeri)
        return retval #json.dumps(retval)
  


