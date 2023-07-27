# **Snom KNX gateway BAOS 777 based**

The snom KNX gateway allows you to control your KNX system in an easy way.  
You just need a device that sends HTTP-Requests like a webbrowser, an IP phone, a DECT basis station, an IP camera, an IP intercom, etc.  
You can also build your own application that sends the HTTP-requests.  

That means you can change the functionality of the buttons or sensors of your IP device in order to control your KNX system on your own.

For example, using a [Snom IP phone](https://www.snom.com/en/), you can assign at each time, to each button in each room a new functionality.  
You can also trigger an action in a KNX device, e.g., when a call comes in.

You only need to set up HTTP-Requests with patterns like this:  
`http://ip.of.the.gateway:8000/knx/write/group/addr/ess/switch/on` (will switch on the groupaddress),  
`http://ip.of.the.gateway:8000/knx/write/group/addr/ess/dimming/increase` (will dimm the groupaddress up)   
`http://ip.of.the.gateway:8000/knx/write/group/addr/ess/value_temp/23,7` (will set the temperature of the groupaddress to 23,7°C)  
`http://ip.of.the.gateway:8000/knx/read/group/addr/ess/`(will read the current value of the groupaddress)  

See the full [API](#snom-knx-api) below

## **Services**
The Snom KNX gateway software has 3 services

### **Snom IoT WUI**
Web User Interface for setting up the interoperability betwen Snom devices and KNX devices.  
Serves the Snom XML minibrowser.  
The KNX devices can be controlled from here.
This service starts when the device is booted.
The other two services can be started or stopped from the WUI.

### **KNX monitor**
It can be started/stopped from the Snom IoT WUI.
This service is needed for the Function keys relations functionality.
It monitors the traffic in the KNX installation updating Snom function keys subscriptions.  
_E.g.: LED color of function key changes if incoming KNX bus event happens_

### **Snom syslog KNX**
It can be started/stopped from the Snom IoT WUI.
This service is needed for the Ambientlight relations and the Temperature relations functionalities.
Handles incoming syslog messages from a Snom device triggering events in the KNX devices.  
_E.g.: sends temperature or light sensor values to the KNX bus_

## **Hardware needed**
- [Weinzierl BAOS 777](https://weinzierl.de/en/products/knx-ip-baos-777/?gclid=EAIaIQobChMIq5Kg-oCQ_wIVhdDVCh2ozQqgEAAYASAAEgKotPD_BwE)
- Linux device (e.g. Raspberry Pi) or Snom I100KNX

## **Configuring the BAOS 777**
1. With the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool, integrate the BAOS 777 in your KNX system. 
2. Only he parametrized sending groupaddresses will be writable/readable with the Snom KNX gateway
3. Export all the KNX groupaddresses of your KNX project from the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool as .csv file or ask your KNX integrator for it

## **Installation of the Snom KNX gateway software in a Linux device**
1. Open a terminal in your systemd linux device
2. Make sure [Python 3.10](https://realpython.com/installing-python/#how-to-build-python-from-source-code) is installed and [is the default version](https://www.baeldung.com/linux/default-python3) for the command `python3`
3. Make sure pip and git are installed
4. Go to the folder `/usr/local` and clone this repository:  

    `sudo git clone https://gitlab.com/simon.golpe/snom_baos_777`
5. Install the python [requirements.txt](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/requirements.txt)  

    `sudo pip3 install -r snom_baos_777/requirements.txt`
7. Type `sudo crontab -e`, add and save this line at the end of the file:

    `@reboot /usr/bin/python3 /usr/local/snom_baos_777/iot/manage.py runserver 0:8000 > /usr/local/snom_baos_777/cronlogRunserver 2>&1`  
    `@reboot sleep 10 && /usr/bin/python3 /usr/local/snom_baos_777/iot/manage.py restart_subprocesses > /usr/local/snom_baos_777/cronlogSubprocesses 2>&1` 
8. Reboot the device

## **Usage**
1. From the webbrowser of a device in the same network as your I100KNX or Linux machine, call:  
    `http://ip.of.the.gateway:8000/knx/`, where `ip.of.the.gateway` is the ip address of your I100KNX or of the Linux device where the Snom KNX software was installed
2. Click on "Change" for setting the BAOS IP address. You can find the ip in the display of your BAOS 777.  
The default credentials for the administration are:  
User = admin, Password = admin
3. Navigate to KNX->Upload and upload the .csv file with your KNX groupaddresses exported from the ETS  

Under KNX->Groupaddresses you can see now the groupaddresses you can control with the Snom phones (BAOS sending groupaddresses) and the rest of the groupaddresses available in the knx installation.  
If you want to control a new groupaddress with the Snom phone, you must set via ETS a new datapoint in the BAOS 777 for this groupaddress, export the groupaddresses as csv again and upload the new .csv file in the Snom IoT WUI.
   
### **Using a Snom Deskphone**
Ways for control/monitoring the KNX installation:

#### **_Snom minibrowser_**
1. [Configure a function key](https://service.snom.com/display/wiki/Function+keys) of your Snom phone as an action-URL and assign it the value `http://ip.of.the.gateway:8000/knx/`
2. Pressing this function key, you can now read/write the sending groupaddresses of the BAOS 777 device  

#### **_Function keys_**
You can assign to each phone function key a KNX groupaddress for controlling it.  
This way each function key can be used as KNX switch.  

1. Navigate to `http://ip.address.of.phone`
2. Navigate to `function keys` -> `Line Keys`
3. Set up one line key as `action url`
4. Set the url for controlling the KNX groupaddress.  
_E.g. `http://ip.of.the.gateway:8000/knx/write/2/1/21/scaling/phone_input`_
5. Set a label for the line key and save.  
_E.g. `Ceiling light %`_

If you press now in the configured line key, you will be asked for typing a value between 0...100% for dimming the groupaddress.  
If you assign a groupaddress of boolean datapoint type, you have the possibility to signalize the status of the groupaddress through the line key LED color.  
You can setup this functionality with a [function key led bool relation](#function-keys-led-bool-relations).

#### **_Function keys led bool relations_**  
It generates the url for the function key and subscribes the led of the function key for showing the current status of a KNX groupaddress.  
For this functionality, the service knx monitor must be started in the Snom IoT WUI.  
After configuring the relation, pressing the function key will control the groupaddress.  
The color of the function key LED will change showing the status of the status KNX groupaddress if its value is changed from any phone or from any KNX device.

1. Navigate to `http://ip.of.the.gateway:8000/admin/` and login (default user/password: admin/admin)
2. Click on `Function key led bool relations` 
3. Click on the top right `Add function key led subscriptions`
4. Fill in the needed information
5. Click "Save and continue editing"
6. Copy the url displayed in `Knx toggle url:` and configure it as action url for the chosen function key over the phone WUI (paste the copied values)

Now you can toggle the groupaddress with the configured function key.  
The LED will change the color depending on the status of the configured status groupaddress.  
If another device changes the value of the groupaddress, the LEDs will update its status. 

#### **_Setting a code/PIN to allow controlling a specific KNX groupaddress_**
On some cases, you don´t want that anyone controls a groupaddress (e.g. open/close a door or switch on/off an alarm system).  
In this case you can set up this groupaddress with a code/PIN, so that the user is asked to type it on the phone keyboard.
   
The groupaddress will only switch if the typed code/PIN is correct.
1. Navigate to `http://ip.of.the.gateway:8000/admin/` and login (default user/password: admin/admin)
2. Click on `Groupaddresss`
3. Click on the groupaddress you want to safe with a code
4. Fill in the code and save

Now if you try to control this groupaddress over a function key or minibrowser, you will be asked for the code.

#### **_Ambient light sensor_**  
With Snom D735 phones and its built-in ambientlight sensor, you can control your KNX dimm actuators or send the measured value to the KNX bus.  
For this, you can define in which Lux range the brightness of your workplace must be.  

You can also configure the ambientlight relation so that the measured Lux value is sent to the KNX bus if the configured Lux delta is exceeded.  
You can use this value as input for other KNX devices.

For this functionality, the service "syslog" must be started in the Snom IoT WUI.

1. Navigate to `http://ip.of.the.gateway:8000/admin/` and login (default user/password: admin/admin)
2. Click on `Ambient light relations`
3. Click on the top right `Add ambient light relation`
4. Fill in the needed information
5. Save and click in the new created LED subscription
6. Navigate to `http://ip.address.of.phone`
7. Navigate to `Advanced` -> `Debug`
8. Set as syslog server IP address `ip.of.the.gateway:515` 

Now the phone will keep the brightness of the workplace in the configured Lux range (e.g. 100...500 Lux).  
The sensor of the phone will also send the current measured Lux value to the KNX  if the configured Lux delta is exceeded.

#### **_Temperature sensor_**  
With any Snom deskphone and [an usb temperature sensor](https://www.tindie.com/products/kel/usb-thermometer/) plugged in it, you can send the current temperature of your workplace to the KNX bus.  
This way you can , e.g., control the KNX heating actuators or open/close windows automatically depending on the current temperature.

For this functionality, the service "syslog" must be started in the Snom IoT WUI.

1. Navigate to `http://ip.of.the.gateway:8000/admin/` and login (default user/password: admin/admin)
2. Click on `Temperature relations`
3. Click on the top right `Add temperature relation`
4. Fill in the needed information and save
6. Navigate to `http://ip.address.of.phone`
7. Navigate to `Advanced` -> `Debug`
8. Set as syslog server IP address `ip.of.the.gateway:515` 

Now the phone will send the measured temperature to the KNX bus if the configured Celsius delta is exceeded.
   
### **Using the SNOM DECT solutions**
(TBD)

## **Developing the Internet of Things gateway in your local machine**
(TBD)

## **Snom KNX API**
`http://ip.of.the.gateway:8000/` is the url base, where  `ip.of.the.gateway` is the IP address of the I100KNX or the Linux machine where the Snom KNX software runs.  
Below is used the groupaddress 1/2/3 as example.  

| URL path | Function |
|:-------------|:-------------|
| `knx/minibrowser/` | opens the Snom KNX minibrowser |
| `knx/read/1/2/3/` | reads the groupaddress status |
| `knx/write/1/2/3/switch/on` | switches on a DPT1 groupaddress |
| `knx/write/1/2/3/switch/off` | switches off a DPT1 groupaddress |
| `knx/write/1/2/3/switch/toggle` | toggles a DPT1 groupaddress |
| `knx/write/1/2/3/dimming/increase` | dimms up a DPT3 groupaddress (step code=5) |
| `knx/write/1/2/3/dimming/decrease` | dimms down a DPT3 groupaddress (step code=5) |
| `knx/write/1/2/3/scaling/50` | sets a DPT5 groupaddress to the given value in % (50% in this example) |
| `knx/write/1/2/3/scaling/phone_input` | sets a DPT5 groupaddress to the typed value in the phone keyboard (0...100%) |
| `knx/write/1/2/3/value_temp/23,7` | sets a DPT9 groupaddress to the given float value in °C (23,7°C in this example)|
| `knx/1/2/3/start_blink/3/2` | the given DPT1 groupaddress starts blinking (3 seconds for on and 2 seconds for off in this example)  |
| `knx/1/2/3/stop_blink` | the given DPT1 groupaddress stops blinking |
| `knx/subprocesses/start/monitor` | starts the knx monitor |
| `knx/subprocesses/stop/monitor` | stops the knx monitor subprocess|
| `knx/subprocesses/start/syslog` | starts the knx syslog subprocess|
| `knx/subprocesses/stop/syslog` | stops the knx syslog subprocess |

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
