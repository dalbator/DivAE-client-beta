# DivAE-client-beta
Raspberry PI Clients that connect to ActionKata server

This Python client use the REST API to send peripherals status and receive commands to and from actionKATA server http://actionKATA.com

####How to setup
1. First you need to create a free account on http://actionKATA.com
2. follow the instructions on how to setup a device.
3. Back to de client edit the config.cfg to replace the "deviceid" and the "password" that were setted on the server.
4. Make sure that the "server" and "port" are set to: http://actionKATA.com on port 80.

####Ho to run
#####MAC OSX
For demonstration purpose you can run the client on MAC OSX.
$python3 divae.py

#####Windows
Also for demonstration purpose you can run the client on Windows.
You first need to install Python3 from Python's website
[https://www.python.org/downloads/windows/]

#####RASPBERRY PI
1. Copy the entire Python client files to a Folder in Raspberry PI. Default folder name is "divea"
2. in peripheralcontrol.py replace "from rpictrl_dud" to "from rpictrl" if you want to control actual relays.
please note that "rpictrl.py" uses PIFACE Digital.
3. run divae client
$sudo python divae.py

######To run the client everytime the device reboot
1. sudo crontab -e
2. Append the following: @reboot sh /home/pi/divea/start.sh >/home/pi/logs/cronlog 2>&1
3. Save the file
3. Replace the "divea" folder to match your divea directory
4. Check the start.sh file and make sure it is set to the correct folder.
5. Reboot the device "sudo reboot"

