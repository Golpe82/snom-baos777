# Internet of Things gateway

## KNX app
The KNX app in this project allows you to upload your groupaddresses, create or modify your
KNX Snom XML minibrowser and to control your KNX installation through the URL KNX-Gateway.

### For local development
1. Clone this project in any directory in your local machine
2. Create a symlink from the file `/path/to/project/iot/knx/media/knx.xml` to the file
    `/path/to/project/iot/knx/templates/knx/minibrowser.xml` (as sudo)

### Hardware needed for the KNX URL Gateway
- Raspberry Pi 3B+
- [KNX kBerry module](https://www.weinzierl.de/index.php/en/all-knx/knx-module-en/knx-baos-module-838-en)

### Preparing the hardware
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
6. Type `sudo crontab -e` and append this:  
    `@reboot /usr/local/gateway/launcher.sh >/usr/local/gateway/cronlog 2>&1`
7. Install [NGINX](https://www.nginx.com/) and git

### Installation of the application in the KNX URL-Gateway

1. Go to the directory `/usr/local/` of your KNX URL-Gateway, type `git init` in your terminal and clone this project:  
   `sudo git clone https://gitlab.com/simon.golpe/gateway.git`
2. Type this three commands on your terminal:  
   `sudo chgrp -R pi gateway/`  
   `sudo chown -R pi gateway/`  
   `sudo chmod +x gateway/launcher.sh` 
3. Type `sudo crontab -e` and append this:  
    ```
    # create symlinks for IoT GUI
    @reboot ln -s /usr/local/gateway/iot/knx/media/knx.xml /usr/local/gateway/iot/knx/templates/knx/minibrowser.xml
    @reboot ln -s /usr/local/gateway/iot/knx/media/knx.xml /var/www/html/knx.xml
    @reboot ln -s /usr/local/gateway/iot/knx/media/ga.csv /usr/local/gateway/ga.csv

    # start IoT GUI
    @reboot /usr/bin/python3 /usr/local/gateway/iot/manage.py runserver 0:8000
    ```
4. Save the changes and reboot the system

### Configure and usage
1.  Export the KNX groupaddresses of your KNX project from the [ETS](https://www.knx.org/knx-en/for-professionals/software/ets-5-professional/) tool as .csv file or ask your KNX integrator for it
2. From the webbrowser of a device in the same network as your KNX URL-Gateway call:  
    `http://192.168.178.47:8000/knx/`, where the IP address must be the address of the KNX URL-Gateway.
3. Upload the .csv file with your KNX groupaddresses
   
_Using a Snom deskphone_
1. Configure a function key of your Snom phone as an action-URL and assign it the value `http://192.168.178.47:8000/knx.xml`, where the IP address must be the address of the KNX URL-Gateway.
2. Pressing this function key, you can now control your KNX system
   
_Using a Snom M900 and Snom DECT handsets_
1. Configure in the M900 your central directory as XML minibrowser and set the value `http://192.168.178.47:8000/knx.xml`
2. Update your DECT Basisstation and your handsets
3. Pressing the central directory button of your handsets, you can now control your KNX system


If you want to customize the minibrowser menu, navigate in the GUI to 'Minibrowser', download the XML file and upload it again after customizing it.  

Navigating to 'Start' in the GUI, you can also control your KNX system.
    