cp vlcrc .config/vlc:
----
# Fake TTY (boolean)
rc-fake-tty=1

# UNIX socket command input (string)
rc-unix=tmp/vlc.sock
----

sudo iwlist wlan0 scan | grep -Eo "(ESSID:\".+\")|(level=[0-9]+/[0-9]+)|(Quality=[0-9]+/[0-9]+)"

/etc/wpa_supplicant/wpa_supplicant.conf
----
network={
    ssid="testing"
    psk="testingPassword"
}
----
wpa_cli -i wlan0 reconfigure
