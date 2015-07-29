#perimeter commnd factory
# commands pass between permeter server and perimeters
import json
import pdb
import threading
import socket
import datetime
from threading import Thread

from iseclogger import Logger
import urllib.request
from peripherals import LocalPeripherals
from schedules import ScheduleObject
from schedules import Schedules

class SharedInstances:
    static_commandProcessor = None;
    


class CommandProcessor:
    ST_CMD_NONE = "0"
    ST_CMD_UPDATE_PERIPHERALS_STATUS = "20"
    ST_CMD_GET_PERIPHERALS = "30"
    ST_CMD_UPDATE_COMMAND_STATUS = "50"
    
    ST_CMD_SET_PERIPHERALS = "200"
    ST_CMD_SET_TIMER = "230"

    ST_CLIENT_ID = "cid"
    ST_CLIENT_PASSWORD = "psw"
    ST_CMDC = "cmdc"
    ST_CMDCS = "cmds"
    ST_STI = "sti" #status id
    ST_STM = "stm" #status message
    ST_DATA = "data"
    ST_CMD_REF = "ref"

    ST_SUMMARY = "summary"

    STATUS_CODE_OK = "10"
    STATUS_MESSAGE_OK = "Ok"
    
    STATUS_CODE_UNKNOWN_COMMAND = "20"
    STATUS_MESSAGE_UNKNOWN_COMMAND = "Unknown command"

    STATUS_CODE_PERIPHERAL_NOT_FOUND = "30"
    STATUS_CODE_PERIPHERAL_NOT_FOUND_MESSAGE = "Peripheral not found"

    STATUS_CODE_DATA_NOT_FOUND = "40"
    STATUS_CODE_DATA_NOT_FOUND_MESSAGE = "Data section not found"

    STATUS_CODE_ERROR_SAVE_SCHEDULES = "50"
    STATUS_CODE_ERROR_SAVE_SCHEDULES_MSG = "Unable to save schedules"

    TIMER_MINUTES = "minutes"
    TIMER_DEVICE_ID = "peripheral_id"

    PERIPHERALS = "peri"
    
    

    MODULE_NAME = "CMDPROCESSOR"

    TIMEOUT15 = 15


    ST_DATA_PERIPHERAL = "peripherals"

    log = None
    peripheralcontroller = None
    localConfig = None
    peri = None;

    pendingreplies = []; # there are the statuses awaiting to be sent to the server

    def __init__(self, log, peripheralcontroller, localConfig):
        SharedInstances.static_commandProcessor = self;
        self.log = log
        self.peripheralcontroller = peripheralcontroller
        self.localConfig = localConfig;
        self.peri = LocalPeripherals(self.log);
        self.peri.load();

    def beginPostSwitchEvent(self,bcmchanel, newvalue):
        self.log.write("beginPostSwitchEvent", "readytopost");
        self.posterth = Thread(target = self.posterSwitchEventThread, args = (bcmchanel, newvalue,))
        self.posterth.start()

    FIELD_EVENT_PERIPHERAL_ID = "pid";
    FIELD_EVENT_PERIPHERAL_TYPE = "ptype"
    FIELD_EVENT_TIME = "etime"
    FIELD_EVENT_PERIPHERAL_VALUE = "nvalue"

    def posterSwitchEventThread(self,bcmchanel,newvalue):
        lock = threading.RLock()
        with lock:
            peripheral = self.peri.findPeripheralByTypeAndGpio(LocalPeripherals.PERI_TYPE_SWITCH, bcmchanel);
            if(peripheral != None):

                payload = self.constructPostHeader();
                date = str(datetime.datetime.now());
                eventdata = { ''+self.FIELD_EVENT_PERIPHERAL_ID+'':'' + peripheral.devid
                + '',''+self.FIELD_EVENT_PERIPHERAL_TYPE + '':'' + peripheral.ptype
                + '',''+self.FIELD_EVENT_TIME + '':'' + date
                + '',''+self.FIELD_EVENT_PERIPHERAL_VALUE+ '':'' + newvalue+''}
                
                payload["event"] = eventdata;

                url = self.localConfig.serveraddress +":"+self.localConfig.serverport +"/diversityclient";
                req = urllib.request.Request(url)
                req.add_header('Content-Type', 'application/json')
                self.log.write("POSTING the following: ", payload);
                data = json.dumps(payload)
                databytes = data.encode('utf-8')
     
                req.add_header('Content-Length', len(databytes))
                
                try:
                    response = urllib.request.urlopen(req, databytes, self.TIMEOUT15);

                    self.pendingreplies = [];
                   
                    data = response.read()
                    self.processCommands(data);
                    self.connected_time += 1;
                except urllib.error.HTTPError as e:
                    self.log.write("post", "HTTP Error: %d"% e.code)
                    self.connection_issues += 1;
                except urllib.error.URLError as e:
                    self.log.write("post", "URL Error: %s"% e.args)
                    self.connection_issues += 1;
                except socket.timeout as e:
                    self.log.write("post", "timeout")
                    self.connection_issues += 1;
            else:
                self.log.write("beginPostSwitchEvent", "Peripheral not found");
            #find the id of the peripheral
            


    def beginPost(self,postdata):
        self.posterth = Thread(target = self.posterThread, args = (postdata, ))
        self.posterth.start()

    def addPendingReplies(self, postdata):
        if len(self.pendingreplies) > 0:
            postdata["tasks"] = self.pendingreplies;
        else:
            self.log.write("addpending tasks", "No pending tasks");

        return postdata;
            

    def posterThread(self,postdata):
        lock = threading.RLock()
        with lock:
            postdata = self.addPendingReplies(postdata);
            postdata = self.addPeripheralsStatus(postdata);
            url = self.localConfig.serveraddress +":"+self.localConfig.serverport +"/diversityclient";
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            self.log.write("POSTING the following: ", postdata);
            data = json.dumps(postdata)
            databytes = data.encode('utf-8')
 
            req.add_header('Content-Length', len(databytes))
            
            try:
                response = urllib.request.urlopen(req, databytes, self.TIMEOUT15);

                self.pendingreplies = [];
               
                data = response.read()
                self.processCommands(data);
                self.connected_time += 1;
            except urllib.error.HTTPError as e:
                self.log.write("post", "HTTP Error: %d"% e.code)
                self.connection_issues += 1;
            except urllib.error.URLError as e:
                self.log.write("post", "URL Error: %s"% e.args)
                self.connection_issues += 1;
            except socket.timeout as e:
                self.log.write("post", "timeout")
                self.connection_issues += 1;

    def postAlive(self):
        result = self.constructPostHeader();
        result[self.ST_SUMMARY] = self.constructSummary();

        self.beginPost(result);

    connected_time = 0;
    connection_issues = 0;
    def constructSummary(self):
        summary = "Connecion success: " +str(self.connected_time)+\
        " Failed: "+ str(self.connection_issues);
        return summary;
        #self.peripheralcontroller.getSummaryVerbose();
        #return "test 123"

    def processCommands(self, commands):

#        self.log.write("----- processCommands ------", commands);       
        jcmd = json.loads(commands.decode());
        retvalcommands = [];
        if(self.ST_CMDCS in jcmd):
            cmds = jcmd[self.ST_CMDCS];
            
            if(cmds != None):
                for cmd in cmds:
                    onecmd = self.processCommand(cmd);
                    if(onecmd != None):
                        self.log.write("  Message","Adding command to array");
                        retvalcommands.append(onecmd);
                    else:
                        self.log.write("  Error","command not created");
        else:
            self.log.write("  Error","cmds not found");
                

 #       self.log.write("***** processCommands  end ******",retvalcommands );
                
        self.pendingreplies.append(retvalcommands);
        
        return None;
        
    def processCommand(self, command):
 #       self.log.write("------ processCommand ------", command);
  
        jcmd = command;
        commandid = "-1"
        if(jcmd != None):
            if(self.ST_CLIENT_ID in jcmd):
                commandid = jcmd[self.ST_CLIENT_ID]
            
        result = None;
        if(commandid == self.ST_CMD_GET_PERIPHERALS):
            result = self.cmdGetPeripherals(jcmd)
        elif(commandid == self.ST_CMD_SET_TIMER):
            result =    self.cmdSetTimer(jcmd)
        else:
            self.log.write(self.MODULE_NAME, "unknown command")
            #self.ST_CMD_SET_TIMER, statuscode, statusmessage
            result = self.constructBaseCommand(commandid,
                                               self.STATUS_CODE_UNKNOWN_COMMAND,
                                               self.STATUS_MESSAGE_UNKNOWN_COMMAND);

        return result
            

    def addPeripheralsStatus(self, postdata):

        #peri = LocalPeripherals(self.log)
        #self.peri.load();
        #jval = peri.toJSON();
        postdata["peripherals_stat"] = self.peri.getPeripheralsStatus(self.peripheralcontroller);
        
        return postdata;

  
    def cmdGetPeripherals(self, jcmd):
        self.log.write(self.MODULE_NAME, "***********get peripherals************")
        #peri = LocalPeripherals(self.log)
        #peri.load();
        jval = self.peri.toJSON();
        self.log.write(self.MODULE_NAME, "- Create response")
        retval = self.createResponseSetPeripherals(jcmd[self.ST_CMD_REF], jval);
        return retval

    def createResponseSetPeripherals(self, reference, locper):
        # add aray of peripherals (locper) to response
        response = { ''+self.ST_CMDC +'':'' + self.ST_CMD_SET_PERIPHERALS
        + '',''+self.ST_CMD_REF + '':'' + reference
        + '',''+self.PERIPHERALS + '': locper }

   
        return response; #json.dumps(response)

        
    def cmdSetTimer(self, jcmd):
        self.log.write(self.MODULE_NAME, "*********** Set timer ************")
        datasection = jcmd[self.ST_DATA]
 #       pdb.set_trace()
        minutes = None
        deviceid = None
        statuscode = None
        statusmessage = None
        
        if(datasection != None):
            minutes = datasection[self.TIMER_MINUTES]

            iminutes = 0
            try:
                iminutes = int(minutes)
            except ValueError:
                iminutes = 0
                pass
    
            deviceid = datasection[self.TIMER_DEVICE_ID]

            self.log.write(self.MODULE_NAME, "minutes: " + str(minutes) + " deviceid: " + deviceid);

                 
            #peri = LocalPeripherals(self.log)
            #peri.load();
 #           pdb.set_trace()
            peripheralobject = self.peri.findPeripheral(deviceid)
            if(peripheralobject != None):
                # set timer
                if(iminutes == 0):
                    self.peripheralcontroller.turnOffPeripheral(peripheralobject)
                else:
                    self.peripheralcontroller.addOneTimer(peripheralobject, iminutes)
                statuscode = self.STATUS_CODE_OK
                statusmessage = self.STATUS_MESSAGE_OK                
            else:
                statuscode = self.STATUS_CODE_PERIPHERAL_NOT_FOUND
                statusmessage = self.STATUS_CODE_PERIPHERAL_NOT_FOUND_MESSAGE    
                
                
        else:
            statuscode = self.STATUS_CODE_DATA_NOT_FOUND
            statusmessage = self.STATUS_CODE_DATA_NOT_FOUND_MESSAGE
 
        # create confirmation message
        jbase = self.constructBaseCommand(self.ST_CMD_SET_TIMER, statuscode, statusmessage);
        retval = self.addToData(jbase, self.ST_DATA_PERIPHERAL, deviceid)
        retval = self.createResponseSetTimerStatus(jcmd[self.ST_CMD_REF]);
        
        return retval

    def createResponseSetTimerStatus(self, reference):
        # add aray of peripherals (locper) to response
        response = { ''+self.ST_CMDC +'':'' + self.ST_CMD_UPDATE_COMMAND_STATUS 
        + '',''+self.ST_CMD_REF + '':'' + reference
         }
        return response;
                
    def constructPostHeader(self):
        
        base = { ''+self.ST_CLIENT_ID +'':'' + self.localConfig.clientid
            + '',''+self.ST_CLIENT_PASSWORD + '':'' + self.localConfig.password + ''}
        return base

    def constructBaseCommand(self, commandid, statid, statmsg):
        base = { ''+self.ST_CMDC+'':'' + commandid
            + '',''+self.ST_STI + '':'' + statid
            + '',''+self.ST_STM + '':'' + statmsg+''}
        return json.dumps(base)
        
    def addToData(self, jbase, stkeyname, jdata):
        self.log.write(self.MODULE_NAME, "- addToData")
        basedic = json.loads(jbase)
        
        if(self.ST_DATA not in basedic):
            basedic[self.ST_DATA] = {}
            
        basedic[self.ST_DATA].update({ stkeyname : jdata })


        return json.dumps(basedic)
 
    
        
        
