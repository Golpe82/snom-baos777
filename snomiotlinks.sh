#!/bin/bash

echo "Creating symlinks for IoT GUI..."
ln -s -f /usr/local/gateway/iot/knx/media/knx.xml /usr/local/gateway/iot/knx/templates/knx/minibrowser.xml
ln -s -f /usr/local/gateway/iot/knx/media/knx.xml /var/www/html/knx.xml
ln -s -f /usr/local/gateway/iot/knx/media/ga.csv /usr/local/gateway/ga.csv

