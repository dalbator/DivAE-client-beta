

#sudo apt-get install python3-pifacedigital-emulator
GOTPIFACE = True;
try:
    import pifacedigitalio
except ImportError:
    print("PIFACE module not found");
    GOTPIFACE = False;

class RPIFaceDigitalController:
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
        retval = False;
        if(GOTPIFACE):
            if(self.p != None):
                intval = self.p.relays[relay].value;
                if(intval == 1):
                    retval = True;		
        return retval;

    def open(self, relay):
        if(self.p != None):
            self.p.relays[relay].value = 1;

    def close( self, relay ):
        if(self.p != None):
            self.p.relays[relay].value = 0; 

    def turnalloff(self):
        self.close(0)
        self.close(1)

    def start(self):
        if(GOTPIFACE):
            self.p = pifacedigitalio.PiFaceDigital()
            self.turnalloff()

    def stop(self):
        if(self.p != None):
            self.p.deinit_board();
            self.p = None;
        
