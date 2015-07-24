import configparser
import socket
import threading
import signal
import os
import sys
import traceback
import base64
import select
import json
from threading import Timer
sys.path.append( "lib" )
from iseclogger import Logger
from commandprocessor import CommandProcessor
from threading import Thread
from configuration import LocalConfiguration
from peripheralscontrol import PeripheralController
import pdb
import urllib.request


#pdb.set_trace()

mainApp = None

class ReporterTimer():
    def __init__(self, delay):
        self.awesum="hh"
        self.timer = Timer(delay,self.say_hello,args=["WOW"])
    def say_hello(self,message):
        self.awesum=messgae
 
#REPORTING_INTERVAL = 15

class DiversityMain:
    port = None
    name = None
    logger = None
    main_thread = None
    listenerSocket = None
    senderSocket = None
    localConfig = None;
    periphController = None
    commandProcessor = None
    
    
    def __init__(self, localConfig, logger):
        self.localConfig = localConfig
        self.logger = logger
        self.periphController = PeripheralController()
	
        self.commandProcessor = CommandProcessor(logger,self.periphController, self.localConfig)
       

    def start(self):
        self.event = threading.Event();
        self.main_thread = Thread(target = self.startMainThread, args = ("test", ))
        self.main_thread.start()
        self.periphController.startThread()
        

    def startMainThread(self, teset):
        self.startReportingTimer()
        self.event.wait();
        self.logger.write("reporttimer","out");
        
    def startReportingTimer(self):
        if(self.event.isSet()):
            self.logger.write("reporttimer","Not restarting")
        else:
            global localConfig;
            freq = int(localConfig.connectfreq)
            self.timer = Timer(freq ,self.doReport,args=["WOW"])
            self.timer.start()
        
            

    def doReport(self, message):
        self.logger.write("main_thread","reporting")
        self.postalive()
        self.startReportingTimer()


    def join(self):
        self.main_thread.join();

    def stop(self):
        self.periphController.stopThread();
        self.timer.cancel();
        self.event.set();

    def postalive(self):
        postdata = {'cid': localConfig.clientid, 'psw' : localConfig.password }
        self.commandProcessor.postAlive()

        
 

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        mainApp.stop();
            

log = Logger("logs/mainlog","txt", True)
log.write("main", "Starting")
localConfig = LocalConfiguration(log)
localConfig.load()
log.write("main", "Starting main thread")
mainApp = DiversityMain(localConfig, log)
mainApp.start()

 
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()
log.write("main", "joining")
mainApp.join()

log.write("main", "completed")
