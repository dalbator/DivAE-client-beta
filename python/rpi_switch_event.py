#event driven input switch

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)


def switchChange(chanel):
    print("change: " + str(chanel));
    res = GPIO.input(chanel);
    print(res);



GPIO.add_event_detect(4, GPIO.BOTH, callback=switchChange, bouncetime=300);


while True:
    time.sleep(0.2);
