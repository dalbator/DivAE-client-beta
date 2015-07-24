
import threading
from datetime import datetime

class Logger:
    # this should work on is own thread
    logfile = None
    extension = None
    toconsole = False
    def __init__(self, filename, extension, toconsole):
        self.logfile = filename;
        self.toconsole = toconsole;
        self.extension = extension;
        
    def write(self, category, text):
        lock = threading.RLock()
        with lock:
          strdatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          text = "\"{0}\",\"{1}\",\"{2}\"".format(category, text, strdatetime)

          strdate = datetime.now().strftime('%Y-%m-%d')
          strfname = "{0}-{1}.{2}".format(self.logfile,strdate,self.extension)
          file = open(strfname, "a")
          try:
              file.write(text)
              file.write('\n')
          finally:
              file.close

          if self.toconsole == True:
            print(text)


def testLogger():
    print("Starting test")
    log = Logger("test1","txt", False)
    for x in range(0, 100):
        str = "Test: {0}".format(x)
        log.write("phase 1", str)
    for x in range(0, 100):
        str = "Test: {0}".format(x)
        log.write("phase 2", str)

    log = Logger("test2","txt", True)
    for x in range(0, 100):
        str = "Test: {0}".format(x)
        log.write("phase 2", str)

    print("Test completed");
#testLogger();



    
