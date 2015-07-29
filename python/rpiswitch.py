import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

firstinput = False;

def write_status(status):
    if(status == False):
        print("False");
    else:
        print("True");


input_state = GPIO.input(4);
firstinput = input_state;
write_status(firstinput)

while True:
    input_state = GPIO.input(4)


    if input_state !=  firstinput:
        write_status(input_state);
        firstinput = input_state;

    time.sleep(0.2)
