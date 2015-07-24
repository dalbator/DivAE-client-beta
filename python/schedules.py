import json
import pdb
import os.path
import sys
sys.path.append( "../lib" )
from iseclogger import Logger
from datetime import datetime, timedelta
import pdb



class ScheduleObject:
    
    _sid= ""
    _hour = ""
    _duration = ""
    _minute = ""
    _everyXDay = ""

class PeripheralSchedulesObject:
    _peripheraID = ""
    schedules = [] #array of SchedulesObject
    
    def __init__(self, periID):
        self._peripheralID = periID

    def addSchedule(self, sced):
        self.schedules.append(sced)

    def isItTime(self):
        itis = False
        now = datetime.now()
 
        for so in self.schedules:
            date = datetime.now()
            shour = int(so._hour)
            sminute = int(so._minute)
            schedulestart = date.replace(hour=shour, minute=sminute)

            iduration = int(so._duration)
            duration = timedelta(minutes=iduration)
            scheduleenddelta = schedulestart+duration
            
            if(now >= schedulestart and now <= scheduleenddelta):
                itis = True
 #               pdb.set_trace()
                break
            
        return itis
        

class Schedules:
    PERIPH_MODULE = "SCHED_MOD"
    PERIPH_NAME_SID = "sid"
    PERIPH_NAME_DURATION = "duration"
    PERIPH_NAME_HOUR = "time_hour"
    PERIPH_NAME_MINUTES = "time_minute"
    PERIPH_NAME_EVERY_DAY = "every_x_day"

    PERIPH_DATA_PERIPH_ID = "peripheral_id"
    PERIPH_SECTION_SECHEDULES = "schedules"

    log = None

    def __init__(self, log):
        self.log = log

    def getPeripheralID(self, datajson):
        return  datajson[self.PERIPH_DATA_PERIPH_ID]
        
    def saveSchedulesFromServer(self, datajson):
        retval = False
        peripheralid = datajson[self.PERIPH_DATA_PERIPH_ID]
        schedules = datajson[self.PERIPH_SECTION_SECHEDULES]

        if(peripheralid != None and schedules != None):
            # evaluate the schedules
            # schedules can be save as is            
            for schedule in schedules:
                sid = schedule[self.PERIPH_NAME_SID];
                sduration = schedule[self.PERIPH_NAME_DURATION]
                shour = schedule[self.PERIPH_NAME_HOUR]
                sminute = schedule[self.PERIPH_NAME_MINUTES]
                sxday = schedule[self.PERIPH_NAME_EVERY_DAY]
                msg = "schedule: sid: %s, duration %s, shour %s, sminute %s, sxday %s" %(
                      sid, sduration, shour, sminute, sxday)
                self.log.write(self.PERIPH_MODULE,msg)
            self.saveStringToFile(peripheralid, schedules)
            retval = True
                
        else:
            self.log.write(self.PERIPH_MODULE, "invalid json")

        return retval

    def getPeripheralID(self, datajson):
            peripheralid = datajson[self.PERIPH_DATA_PERIPH_ID]
            
            return peripheralid

    def getSchedulesForServer(self, peripheralid):
        schedules = None

        pid = int(peripheralid)
        schedules = self.loadJSonSchedulesForPeripheral(peripheralid)

        

        return schedules


    def saveStringToFile(self, fileid, jdata):
        filename = "sc%s.txt" %(fileid)
        text_file = open(filename, "w")
        json.dump(jdata, text_file)
        text_file.close()

    def getfilename(self, peri):
        filename = "sc%s.txt" %(peri)
        return filename

    def loadJSonSchedulesForPeripheral(self, peri):
        filename = self.getfilename(peri)
        text_file = open(filename, "r")
        sched = json.load(text_file);
        text_file.close()
        return sched

    def loadSchedulesForPeripheral(self,peri):
        
        filename = self.getfilename(peri)
        pso = None
        if(os.path.exists(filename) == True and os.path.isfile(filename) == True):
            text_file = open(filename, "r")
            sched = json.load(text_file);
            text_file.close()
            if(len(sched) > 0):
                pso = PeripheralSchedulesObject(peri)
 #               schedules = json.loads(sched)
                for schedule in sched:
                    
                    scedObj = ScheduleObject()
                    scedObj._sid = schedule[self.PERIPH_NAME_SID];
                    scedObj._hour = schedule[self.PERIPH_NAME_HOUR]
                    scedObj._duration = schedule[self.PERIPH_NAME_DURATION]
                    scedObj._minute = schedule[self.PERIPH_NAME_MINUTES]
                    scedObj._everyXDay = schedule[self.PERIPH_NAME_EVERY_DAY]
                    pso.addSchedule(scedObj)
                
        return pso

    
    
    
