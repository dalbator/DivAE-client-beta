#webcommand factory
import json
from iseclogger import Logger

class WebCommandFactory:
    ST_CMD_RESTART = "10"
    ST_CMD_GET_SERVER_INFO = "20"
    ST_CMD_UPDATE_PERIMETER_INFO = "30"
    ST_CMD = "cmd"
    ST_ID = "id"
    ST_ARGS = "args"
    ST_RETURN_VAL = "rv"
    ST_MSG = "msg"
    ST_PROD_SIGN_SECTION = "ps"
    ST_PROD_NAME_ID = "name"
    ST_PROD_NAME = "isecur"
    log = None

    def __init__(self, log):
        self.log = log

    def constructbase(self, cmdid):
        # {"ST_PROD_SIGN_SECTION":{"ST_PRODNAME_ID":"ST_PROD_NAME"},"ST_CMD"{}}
        stcmd = "{{\"{0}\":{{\"{1}\":\"{2}\"}},\"{3}\":{{\"{4}\": {5}}}}}"
        stcmd = stcmd.format(self.ST_PROD_SIGN_SECTION,
                             self.ST_PROD_NAME_ID, self.ST_PROD_NAME, self.ST_CMD, self.ST_ID, cmdid);
        return stcmd

    def restart( self, arg):
        stcmd = self.constructbase(self.ST_CMD_RESTART)
        #self.log.write("restart", stcmd.__class__.__name__)
        #stcmd is a str
        self.log.write("restart",stcmd)
        jobj = json.loads(stcmd)
        #jobj is a dict
        #add argument to command
        jobj['cmd'][self.ST_ARGS]
        jobj['cmd'][self.ST_ARGS].append("a", arg)
        #self.log.write("restart", jobj.__class__.__name__)
        self.log.write("restart",jobj)

    def getServerInfo(self):
        stcmd = self.constructbase(self.TST_CMD_GET_SERVER_INFO)
        

    def exec_getServerInfo(self, jobj, serverport, perimeterport, name):
        # add key "rv" under cmd#
        #serverport:2056
        #perimeterport:38887
        #name: iSecurity at my house
        pass




def test():
    log = Logger("webcmdf","txt",True)
    log.write("main","Start");
    wcf = WebCommandFactory(log);
    wcf.restart("0");

    log.write("main","End");


test()
        
