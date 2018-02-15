import json
import configparser
import socket
import threading
import os
import sys
import traceback
sys.path.append( "lib" )
from iseclogger import Logger
from threading import Thread
    


class LocalConfiguration:
    serverport = None
    serveraddress = None
    clientname = None
    clientid = None
    clientversion = None
    password = None

    logger = None
    
    SECTION_MAIN = "main"
    
    SERVER_PORT = "serverport"
    SERVER_ADDRESS = "serveraddress"
    CLIENT_ID = "deviceid"
    CLIENT_VERSION = "version"
    PASSWORD = "password"
    CONNECT_FREQ = "connectfreq"

    
    filename = "../cfg/config.cfg"
    
    
    def __init__(self, logger):
        self.logger = logger
    def load(self):
        try:
            # open configuration page
            config = configparser.ConfigParser()
            config.read(self.filename)
            dict1 = {}

            if config.has_section(self.SECTION_MAIN) == False:
                self.logger("localconfig", "section not found")
                return
            secitems = dict(config.items(self.SECTION_MAIN))
             
            self.serverport = secitems[self.SERVER_PORT];
            self.serveraddress = secitems[self.SERVER_ADDRESS];
            self.clientid = secitems[self.CLIENT_ID];
            self.clientversion = secitems[self.CLIENT_VERSION];
            self.password = secitems[self.PASSWORD];
            self.connectfreq = secitems[self.CONNECT_FREQ];
             
             
        except:
            #traceback = sys.exc_info()
            e_type, e_value, e_tb = sys.exc_info()
            #traceback.print_exc()
            str_trace = repr(traceback.format_exception(e_type, e_value, e_tb))
            self.logger.write("localconfig","error reading:" +
                              self.filename + str_trace)
            #sys.exc_clear()


