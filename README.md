# **Snom KNX gateway BAOS 777 based**

The snom KNX gateway allows you to control your KNX system in an easy way.  
You just need a device that sends HTTP-Requests like a webbrowser, an IP phone, a DECT basis station, an IP camera, an IP intercom, etc.  
You can also build your own application that sends the HTTP-requests.  

That means you can change the functionality of the buttons or sensors of your IP device in order to control your KNX system on your own.

For example, using a [Snom IP phone](https://www.snom.com/en/), you can assign at each time, to each button in each room a new functionality.  
You can also trigger an action in a KNX device, e.g., when a call comes in.

You only need to set up HTTP-Requests with patterns like this:  
`http://ip.of.the.gateway/knx/write/group/addr/ess/switch/on` (will switch on the groupaddress),  
`http://ip.of.the.gateway/knx/write/group/addr/ess/dimming/increase` (will dimm the groupaddress up)   
`http://ip.of.the.gateway/knx/read/group/addr/ess/value_temp/23,7` (will set the temperature of the groupaddress to 23,7°C)  
`http://ip.of.the.gateway/knx/read/group/addr/ess/`(will read the value of the groupaddress)  

## **Services**
The Snom KNX gateway software has 3 services

### **Snom IoT GUI**
User interface for setting up the interoperability betwen Snom devices and KNX devices.  
Serves the Snom XML minibrowser.  
Has a Web User Interface for controlling the KNX devices.

### **KNX monitor**
Monitors the traffic in the KNX installation updating Snom function keys subscriptions.  
_E.g.: LED color of function key changes if incoming KNX bus event happens_

### **Snom syslog KNX**
Handles incoming syslog messages from a Snom device triggering events in the KNX devices.  
_E.g.: sends temperature or light sensor values to the KNX bus_

## **Hardware needed**
- [Weinzierl BAOS 777](https://weinzierl.de/en/products/knx-ip-baos-777/?gclid=EAIaIQobChMIq5Kg-oCQ_wIVhdDVCh2ozQqgEAAYASAAEgKotPD_BwE)
- Linux device with [systemd](https://en.wikipedia.org/wiki/Systemd) (e.g. Raspberry Pi)

## **Configuring the BAOS 777**
(WIP)
1. With the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool, integrate the BAOS 777 in your KNX system. 
2. Only he parametrized sending groupaddresses will be writable/readable with the Snom KNX gateway
3. Export the KNX groupaddresses of your KNX project from the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool as .csv file or ask your KNX integrator for it

## **Installation of the Snom KNX gateway software**
1. Open a terminal in your systemd linux device
2. Make sure [Python 3.10](https://realpython.com/installing-python/#how-to-build-python-from-source-code) is installed and [is the default version](https://www.baeldung.com/linux/default-python3) for the command `python3`
3. Make sure pip and git are installed
4. Go to the folder `/usr/local` and clone this repository:  

    `sudo git clone https://gitlab.com/simon.golpe/snom_baos_777`
5. Install the python [requirements.txt](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/requirements.txt)  

    `sudo pip3 install -r snom_baos_777/requirements.txt`
6. Create a `.env` file like in this [example](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/.env.example) adjusting the ip address of the Weinzierl BAOS 777 device and of your Linux systemd device (KNX_GATEWAY)
7. Type `sudo crontab -e`, add and save this line at the end of the file:

    `@reboot /usr/bin/python3 /usr/local/snom_baos_777/runner.py > /usr/local/snom_baos_777/cronlog 2>&1` 
8. Reboot the device

After the reboot, your systemd system has 3 new [services](#services):
- [snomiotgui.service](#snom-iot-gui)
- [knxmonitor.service](#knx-monitor)
- [snomsyslog.service](#snom-syslog-knx)

Check that all 3 are running executing:  
`sudo systemctl status snomiotgui.service knxmonitor.service snomsyslog.service`

## **Usage**
1. From the webbrowser of a device in the same network, call:  
    `http://ip.of.the.gateway/knx/`
2. Upload the .csv file with your KNX groupaddresses
   
### **Using a Snom Deskphone**
Ways for control/monitoring the KNX installation:

#### **_Snom minibrowser_**
1. [Configure a function key](https://service.snom.com/display/wiki/Function+keys) of your Snom phone as an action-URL and assign it the value `http://ip.of.the.gateway/knx/`
2. Pressing this function key, you can now read/write the sending groupaddresses of the BAOS 777 device  

#### **_Function keys_**
You can assign to each phone function key a KNX groupaddress for controlling it.  
This way each function key can be used as KNX switch.  

1. Navigate to `http://ip.address.of.phone`
2. Navigate to `function keys` -> `Line Keys`
3. Set up one line key as `action url`
4. Set the url for controlling the KNX groupaddress.  
_E.g. `http://ip.of.the.gateway/knx/write/2/1/21/scaling/phone_input`_
5. Set a label for the line key and save.  
_E.g. `Ceiling light %`_

If you press now in the configured line key, you will be asked for typing a value between 0...100% for dimming the groupaddress.  
If you assign a groupaddress of boolean datapoint type, you have the possibility to signalize the status of the groupaddress through the line key LED color.  
You can setup this functionality with a [function key subscription](#function-keys-subscriptions).

#### **_Function keys subscriptions_**  
It subscribes a phone function key to a KNX groupaddress.  
After configuring the subscription, pressing the function key will control the groupaddress (only boolean KNX datapoint types).  
The color of the function key LED will change showing the status of the KNX groupaddress if the groupaddress value is changed from any phone or from any KNX device.

1. Navigate to `http://ip.of.the.gateway/admin/` and login (default user/password: admin/admin)
2. Click on `Function key led subscriptionss` 
3. Click on the top right `Add function key led subscriptions`
4. Fill in the needed information
5. Save and click in the new created LED subscription
6. Copy the urls of `Knx write url for on:` and `Knx write url for off:` and configure the to the LED corresponding function keys as action url over the phone WUI (paste the copied values)

Now you can switch on the subscripted groupaddress with one function key and switch off with the other one.  
The LEDs will light on or off depending on the current groupaddress value.  
If another device changes the value of the groupaddress, the LEDs will update its status.

You can configure so much subscriptions like you want. 

#### **_Setting a code to allow controlling a specific KNX groupaddress_**
On some cases, you don´t want that anyone controls a groupaddress (e.g. open/close a door or switch on/off an alarm system).  
In this case you can set up this groupaddress with a code, so that the user is asked to type it on the phone keyboard.
   
The groupaddress will only switch if the typed code is correct.
1. Navigate to `http://ip.of.the.gateway/admin/` and login (default user/password: admin/admin)
2. Click on `Groupaddresss`
3. Click on the groupaddress you want to safe with a code
4. Fill in the code and save

Now if you try to control this groupaddress over a function key or minibrowser, you will be asked for the code.

#### **_Ambient light sensor_**  
With Snom D735 phones and its built-in ambientlight sensor, you can control your KNX dimm actuators.  
For this, you can define between which Lux range the brightness of your workplace must be.  

You can also configure the ambientlight relation so that the measured Lux value is sent to the KNX bus if the configured Lux delta is exceeded.  
You can use this value as input for other KNX devices.

1. Navigate to `http://ip.of.the.gateway/admin/` and login (default user/password: admin/admin)
2. Click on `Ambient light relations`
3. Click on the top right `Add ambient light relation`
4. Fill in the needed information
5. Save and click in the new created LED subscription
6. Navigate to `http://ip.address.of.phone`
7. Navigate to `Advanced` -> `Debug`
8. Set as syslog server IP address `ip.of.the.gateway:514` 

Now the phone will keep the brightness of the workplace in the configured Lux range (e.g. 100...500 Lux).  
The sensor of the phone will also send the current measured Lux value to the KNX  if the configured Lux delta is exceeded.

#### **_Temperature sensor_**  
With any Snom deskphone and [an usb temperature sensor](https://www.tindie.com/products/kel/usb-thermometer/) plugged in it, you can send the current temperature of your workplace to the KNX bus.  
This way you can , e.g., control the KNX heating actuators or open/close windows automatically depending on the current temperature.  

1. Navigate to `http://ip.of.the.gateway/admin/` and login (default user/password: admin/admin)
2. Click on `Temperature relations`
3. Click on the top right `Add temperature relation`
4. Fill in the needed information and save
6. Navigate to `http://ip.address.of.phone`
7. Navigate to `Advanced` -> `Debug`
8. Set as syslog server IP address `ip.of.the.gateway:514` 

Now the phone will send the measured temperature to the KNX bus if the configured Celsius delta is exceeded.
   
### **Using the SNOM DECT solutions**
(TBD)

## **Developing the Internet of Things gateway in your local machine**
(TBD)

---

**HINT**  
For developing remote on the raspberry pi with vscode in your local machine with root permissions:  
1. install vscode extension ssh-remote
2. on the remote machine (raspberry) add this at the end of `/etc/ssh/sshd_conf`:  
```
# Allow root login only for localhost
Match Address 127.0.0.1
        PermitRootLogin yes
```
3. Type this in the raspi terminal `sudo systemctl restart sshd.service`  
4. Go to the ssh-remote extension tab in the vscode of your local machine and start a connection to the remote raspberry pi
5. Go to the extensions tab in vscode. Now you can install your local vscode extensions in your remote machine



Mantainer: Golpe Varela, Simón

2018 - 2023 
