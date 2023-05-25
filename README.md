# Snom KNX gateway BAOS 777 based

The snom KNX gateway allows you to control your KNX system in a easy way.  
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

## Hardware needed
- [Weinzierl BAOS 777](https://weinzierl.de/en/products/knx-ip-baos-777/?gclid=EAIaIQobChMIq5Kg-oCQ_wIVhdDVCh2ozQqgEAAYASAAEgKotPD_BwE)
- Linux device with [systemd](https://en.wikipedia.org/wiki/Systemd) (e.g. Raspberry Pi)

## Configuring the BAOS 777
(WIP)
1. With the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool, integrate the BAOS 777 in your KNX system. 
2. Only he parametrized sending groupaddresses will be writable/readable with the Snom KNX gateway
3. Export the KNX groupaddresses of your KNX project from the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool as .csv file or ask your KNX integrator for it

## Installation of the Snom KNX gateway software
1. Open a terminal in your systemd linux device
2. Make sure Python 3.10, pip and git is installed
3. Go to the folder `/usr/local` and clone this repository:  

    `sudo git clone https://gitlab.com/simon.golpe/snom_baos_777`
4. Install the python [requirements.txt](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/requirements.txt)  

    `sudo pip3 install -r snom_baos_777/requirements.txt`
5. Create a `.env` file like in this [example](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/.env.example) adjusting the ip address of the Weinzierl BAOS 777 device and of your Linux systemd device (KNX_GATEWAY)
6. Type `sudo crontab -e`, add and save this line at the end of the file:

    `@reboot /usr/bin/python3 /usr/local/snom_baos_777/runner.py > /usr/local/snom_baos_777/cronlog 2>&1` 
7. Reboot the device

After the reboot, your systemd system has 3 new services:
- snomiotgui.service
- knxmonitor.service
- snomsyslog.service

Check that all 3 are running executing:  
`sudo systemctl status snomiotgui.service knxmonitor.service snomsyslog.service`

## Usage
1. From the webbrowser of a device in the same network, call:  
    `http://ip.of.the.gateway/knx/`
2. Upload the .csv file with your KNX groupaddresses
   
### Using a Snom Deskphone
Ways for control/monitoring the KNX installation:

_Snom minibrowser_
1. Configure a function key of your Snom phone as an action-URL and assign it the value `http://ip.of.the.gateway/knx/`
2. Pressing this function key, you can now read/write the sending groupaddresses of the BAOS 777 device  

_Function keys subscriptions_
(TBD)

_Ambient light sensor_
Currently only Snom D735
(TBD)

_Temperature sensor_
(TBD)
   
### Using the SNOM DECT solutions
(TBD)

## Developing the Internet of Things gateway in your local machine
(TBD)

# Services

## Snom IoT GUI
User interface for setting up the interoperability betwen Snom devices and KNX devices.  
Serves the Snom XML minibrowser

## KNX monitor
Monitors the traffic in the KNX installation updating Snom function keys subscriptions.  
_E.g.: LED color of function key changes if incoming KNX bus event happens_

## Snom syslog KNX
Handles incoming syslog messages from a Snom device triggering events in the KNX devices.  
_E.g.: sends temperature or light sensor values to the KNX bus_

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

2018 - current 
