import os
import glob
import time
import subprocess
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'

 
def read_dig_temp_raw(atIndex):
    device_folder = glob.glob(base_dir + '28*')
    line = [];
    if(len(device_folder) < 1):
        line.append("thermometer not found");
    elif(atIndex > len(device_folder)-1):
        line.append("thermometer not found at specified index");
    else:
        device_folder = device_folder[atIndex];
        device_file = device_folder + '/w1_slave'
        catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = catdata.communicate()
        out_decode = out.decode('utf-8')
        line = out_decode.split('\n')
    return line
 
def read_dig_temp(atIndex):
    count = 5;
    lines = read_dig_temp_raw(atIndex)
    while lines[0].strip()[-3:] != 'YES':
        if(count == 0):
            break;
        time.sleep(0.2)
        lines = read_dig_temp_raw(atIndex)
        count-=1;
    if(len(lines)>1):
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return str(temp_c), str(temp_f)
        else:
            return lines[0];
    else:
        return lines[0];

#print(read_dig_temp());

    
#while True:
#	print(read_dig_temp(0))
#	print(read_dig_temp(1))	
#	time.sleep(1)
