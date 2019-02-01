from time import sleep
from random import randint

class WlanItem:
    def __init__(self, ssid, level, level_max):
        self.ssid = ssid
        self.level = level
        self.level_max = level_max

DUMMY_WLAN = [WlanItem("eins1234jojo999", 15, 100), WlanItem("zwei", 20, 100), WlanItem("drei", 75,100), WlanItem("vier", 200, 200)]

class NetworkService:
    
    def __init__(self):
        pass
    
    def refresh_ips(self):
        print ("refresh ips")
        sleep(1)
        return {"lan": "192.168.%d.%d" % (randint(0, 255), randint(0, 255)), "wlan": "192.168.%d.%d" % (randint(0, 255), randint(0, 255))}

    def refresh_wlan_list(self):
        print ("simulate refresh wlan list")
        sleep(2)
        return DUMMY_WLAN
    
    def get_wlan_config(self):
        print ("simulate get wlan config")
        sleep(1)
        return {"ssid": DUMMY_WLAN[randint(0, len(DUMMY_WLAN)-1)].ssid, "pw" : "12345"}
    
    def change_wlan_config(self, ssid, pw):
        print ("simulate change wlan config to ssid: %s, pw: %s" % (ssid, pw))
        sleep(2)
