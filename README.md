# Snom KNX gateway BAOS 777 based

The snom KNX gateway allows you to control your KNX system in a easy way.  
You just need a device that sends HTTP-Requests like a webbrowser, an IP phone, a DECT basis station, an IP camera, an IP intercom, etc.  
You can also build your own application that sends the HTTP-requests.  

That means you can change the functionality of the buttons or sensors of your IP device in order to control your KNX system on your own.

For example, using a [Snom IP phone](https://www.snom.com/en/), you can assign at each time, to each button in each room a new functionality.

You only need to set up HTTP-Requests with patterns like this:  
`http://ip.of.the.gateway/knx/write/group/addr/ess/switch/on` (will switch on the groupaddress),  
`http://ip.of.the.gateway/knx/write/group/addr/ess/dimming/increase` (will dimm the groupaddress up)   
`http://ip.of.the.gateway/knx/read/group/addr/ess/value_temp/23,7` (will set the temperature of the groupaddress to 23,7°C)  
`http://ip.of.the.gateway/knx/read/group/addr/ess/`(will read the value of the groupaddress)  


The KNX app allows you to upload your KNX groupaddresses for controlling your KNX installation.

## Hardware needed
- [Weinzierl BAOS 777](https://weinzierl.de/en/products/knx-ip-baos-777/?gclid=EAIaIQobChMIq5Kg-oCQ_wIVhdDVCh2ozQqgEAAYASAAEgKotPD_BwE)
- Linux system with systemd (e.g. Raspberry Pi)

## Configuring the BAOS 777


## Installation of the Snom KNX gateway software
1. Open a terminal in your systemd linux system
2. Make sure Python 3.10, pip and git is installed
3. Go to the folder `/usr/local` and clone this repository:  

    `git clone https://gitlab.com/simon.golpe/snom_baos_777`
4. Install the python [requirements.txt](https://gitlab.com/simon.golpe/snom_baos_777/-/blob/master/requirements.txt)  

    `sudo pip3 install -r requirements.txt`
5. Type `sudo crontab -e`, add and save this line at the end of the file:

    `@reboot /usr/bin/python3 /usr/local/snom_baos_777/runner.py > /usr/local/snom_baos_777/cronlog 2>&1` 
6. Reboot the device

Afterwords, your systemd system has 3 new services running:
- snomiotgui.service
- knxmonitor.service
- snomsyslog.service

## Usage
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

# Services

## KNX monitor
It reads the KNX bus traffic and safe in a .csv file the last status of the KNX Groupaddresses

## Snom syslog KNX

It reads the value of the ambientlight sensor of a Snom D735 in order to dimm the light constantly.

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
