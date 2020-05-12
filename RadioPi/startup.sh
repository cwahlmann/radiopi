#!/bin/bash
# add to /etc/rc.local: "/home/pi/Radio/startup.sh"
amixer cset numid=3 1
amixer set Master -- 95%
cd /home/pi/RadioPi
sudo chmod 755 log/radio_pi.log
mkdir tmp
touch tmp/vlc.sock
sudo -u pi cvlc --config config/vlcrc &
sudo python3 radio_pi.py > log/radio_pi.log
