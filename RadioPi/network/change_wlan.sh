#!/bin/bash
CONF=/etc/wpa_supplicant/wpa_supplicant.conf

echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" > ${CONF}
echo "update_config=1" >> ${CONF}
echo "country=DE" >> ${CONF}
echo "" >> ${CONF}
echo "network={" >> ${CONF}
echo "    ssid=\"$1\"" >> ${CONF}
echo "    psk=\"$2\"" >> ${CONF}
echo "}" >> ${CONF}

wpa_cli -i wlan0 reconfigure
