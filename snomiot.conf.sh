#!/bin/bash
# sleep 15

# echo "Setting enviroment variables..."
# export PYTHONPATH="/usr/local/gateway/iot:/usr/local/gateway/knxmonitor:/usr/local/gateway/snomsyslogknx"

echo "System rebooted, KNX launcher running..."
stty -F /dev/ttyAMA0 19200 cs8 parenb -parodd -icrnl -opost -isig -icanon -echo

echo "serial ttyAMAO configured, this are the new settings:"
stty -F /dev/ttyAMA0 -a

# echo "Starting KNX URL-gateway..."
# /usr/local/gateway/KnxHttpGateway > /usr/local/gateway/logs/KnxGateway.log 2>&1 &

# echo "Starting KNX monitor..."
# /usr/bin/python3 /usr/local/gateway/knxmonitor/main.py > /usr/local/gateway/logs/KnxMonitor.log 2>&1 &

# echo "Starting ambient light sensor syslog parser..."
# /usr/bin/python3 /usr/local/gateway/snomsyslogknx/main.py > /usr/local/gateway/logs/AlsSensor.log 2>&1 &

#echo "Creating symlinks for IoT GUI..."
#ln -s /usr/local/gateway/iot/knx/media/knx.xml /usr/local/gateway/iot/knx/templates/knx/minibrowser.xml
#ln -s /usr/local/gateway/iot/knx/media/knx.xml /var/www/html/knx.xml
#ln -s /usr/local/gateway/iot/knx/media/ga.csv /usr/local/gateway/ga.csv

# echo "Starting IoT GUI..."
# /usr/bin/python3 /usr/local/gateway/iot/manage.py runserver 0:8000 > /usr/local/gateway/logs/django_gui.log 2>&1 &
