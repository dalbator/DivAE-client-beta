import os

def get_temperature():
#    “Returns the temperature in degrees C”
    try:
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))
    except:
        return "Failed to get Temperature"

