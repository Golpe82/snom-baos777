#!/bin/bash

echo "System rebooted, KNX launcher running..."
stty -F /dev/ttyAMA0 19200 cs8 parenb -parodd -icrnl -opost -isig -icanon -echo

echo "serial ttyAMAO configured, this are the new settings:"
stty -F /dev/ttyAMA0 -a
