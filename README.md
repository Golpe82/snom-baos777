# Internet of Things gateway

The purpose of this project is to implement differents IoT systems/services.  
The first implemented service under development is the comunication with the [KNX system](https://www.knx.org/knx-en/for-professionals/index.php) over HTTP protocol.  
Further services like the [DECT-Messaging](https://github.com/snom-project/DECTMessagingDemonstrator) / Bluetooth beacons app are also in progress.

## KNX app
The KNX URL-Gateway allows you to control your KNX system in a easy way.  
You just need a device that sends HTTP-Requests like a webbrowser, an IP phone, a DECT basis station, an IP camera, an IP intercom, etc.  
You can also build your own application that sends the requests.  

That means you can change the functionality of the buttons of your IP device in order to control your KNX system without the need of hiring a KNX integrator.

For example, using a [Snom IP phone](https://www.snom.com/en/), you can assign at each time, to each button in each room a new functionality without paying for this change.

You only need to send an HTTP-Request with one of this patterns:  
`http://ip.of.the.gateway:1234/knx/group/address-an` (will switch on your groupaddress),  
`http://ip.of.the.gateway:1234/knx/group/address-aus` (will switch off your groupaddress)  
`http://ip.of.the.gateway:1234/knx/group/address-plus` (will dimm your groupaddress up)  
`http://ip.of.the.gateway:1234/knx/group/address-minus` (will dimm your groupaddress down)  

The KNX app allows you to upload your KNX groupaddresses and create or modify your
KNX [Snom XML minibrowser](https://service.snom.com/display/wiki/XML+Minibrowser) for controlling your KNX installation.

At this moment the KNX URL Gateway can only control DPT1 (datapoint type 1. On/off) and DPT3 (dimm relative) in one way (send).  
That means reading values from the KNX Bus (e.g. to visualize stati) is still not possible. 

### Hardware needed for the KNX URL Gateway
- Raspberry Pi 3B+
- [KNX kBerry module](https://www.weinzierl.de/index.php/en/all-knx/knx-module-en/knx-baos-module-838-en)

### Preparing the KNX URL-Gateway
1. Flash the Raspberry Pi with the Raspberry OS
1. Assemble the kBerry with the Raspberry Pi and connect it to your LAN network and to your KNX-Bus.
2. Add this in the `/boot/config.txt` of the raspberry pi:
   ```bash
	dtoverlay=pi3-miniuart-bt
	enable_uart=1
	force_turbo=1
    ```
3. Delete this in the file `/boot/cmdline.txt`:  
    `console=serial0,115200`
4. Adjust the group of the device with:  
    `chgrp dialout /dev/ttyAMA0`
5. Add the user in the group with:  
    `usermod -a -G dialout pi`
6. Type `sudo crontab -e`, append this and save the changes:  
    `@reboot /usr/local/gateway/launcher.sh >/usr/local/gateway/cronlog 2>&1`
7. Install [NGINX](https://www.nginx.com/) and git
8. Install Python3 and pip:  
`sudo apt install python3 python3-pip`  
and Django:  
`sudo python3 -m pip install django`

### Installation of the application in the KNX URL-Gateway

1. Go to the directory `/usr/local/` of your KNX URL-Gateway, type `sudo git init` in your terminal and clone this project:  
   `sudo git clone https://gitlab.com/simon.golpe/gateway.git`
2. Type this three commands on your terminal:  
   `sudo chgrp -R pi gateway/`  
   `sudo chown -R pi gateway/`  
   `sudo chmod +x gateway/launcher.sh` 
3. Reboot the system

### Configure and usage
1. With the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool, integrate the KNX URL-Gateway in your system applying to it a KNX physical address
1.  Export the KNX groupaddresses of your KNX project from the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool as .csv file or ask your KNX integrator for it
2. From the webbrowser of a device in the same network as your KNX URL-Gateway call:  
    `http://192.168.178.47:8000/knx/`, where the IP address must be the address of the KNX URL-Gateway.
3. Upload the .csv file with your KNX groupaddresses (for development purposes you can use [this example](https://gitlab.com/simon.golpe/gateway/-/blob/master/groupaddresses.example.csv))
   
_Using a Snom deskphone_
1. Configure a function key of your Snom phone as an action-URL and assign it the value `http://192.168.178.47:8000/knx/minibrowser`, where the IP address must be the address of the KNX URL-Gateway.
2. Pressing this function key, you can now control your KNX system
   
_Using a Snom M900 and Snom DECT handsets_
1. Configure in the M900 your central directory as XML minibrowser and set the value `http://192.168.178.47:8000/knx/minibrowser`  
2. Update your DECT Basisstation and your handsets  
3. Pressing the central directory button of your handsets, you can now control your KNX system  


If you want to customize the minibrowser menu, navigate in the GUI to 'Minibrowser', download the XML file and upload it again after customizing it.  

Navigating to 'Start' in the GUI, you can also control your KNX system.

## Developing the Internet of Things gateway in your local machine
1. Install Python3 and pip:  
`sudo apt install python3 python3-pip`  
and Django:  
`sudo python3 -m pip install django`  
2. Clone this project in any directory in your local machine  
3. Navigate to the project´s root folder `iot` and start the application from terminal with `python3 manage.py runserver`  
3. From the webbrowser of a device in the same network as your KNX URL-Gateway call:  
    `http://192.168.178.47:8000/knx/`, where the IP address must be the address of the KNX URL-Gateway.
4. Upload the .csv file with your KNX groupaddresses (for development purposes you can use [this example](https://gitlab.com/simon.golpe/gateway/-/blob/master/groupaddresses.example.csv))


Mantainer: Golpe Varela, Simón

2018 - current 