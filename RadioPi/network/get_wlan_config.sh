#!/bin/bash
cat /etc/wpa_supplicant/wpa_supplicant.conf | grep -Eo "(ssid=\".*\")|(psk=\".*\")"
