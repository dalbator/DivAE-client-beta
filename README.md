# DivAE-client-beta
Clients that connect to DivAE server

This Python client use REST API to send peripherals status and receive commands to a from a DivAE server http://divae.meteor.com

How to run:
First you need to create a free account on http://divae.meteor.com and follow the instructions on how to setup a device.
Once the device info is configure on the server you then need to modify the config.cfg to replace the "deviceid" and the "password" that was setted on the server.

MAC OS:
$python3 divae.py

RASPBERRY PI:
in peripheralcontrol.py replace "from rpictrl_dud" to "from rpictrl" if you want to control actual relays.
please note that "rpictrl.py" uses PIFACE Digital.

$sudo python divae.py
