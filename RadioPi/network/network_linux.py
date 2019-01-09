from network.network import NetworkService, WlanItem
import subprocess

class LinuxNetworkService (NetworkService):
    def __init__(self):
        NetworkService.__init__(self)
        
    def refresh_ips(self):
        p = subprocess.Popen(['./network/ip.sh', 'eth0'], stdout=subprocess.PIPE)
        ip_lan = p.stdout.read().decode("utf-8").strip()

        p = subprocess.Popen(['./network/ip.sh', 'wlan0'], stdout=subprocess.PIPE)
        ip_wlan = p.stdout.read().decode("utf-8").strip()

        return {"lan": ip_lan, "wlan": ip_wlan}
    
    def refresh_wlan_list(self):
        p = subprocess.Popen(['./network/scan_wlan.sh'], stdout=subprocess.PIPE)
        source = p.stdout.read().decode("utf-8").strip()
        item = None
        result = []
        ssids = []
        for line in source.split("\n"):
            if line[0:6] == "ESSID:":
                ssid = line[7:-1]
                if not ssid in ssids:
                    ssids.append(ssid)
                    item = WlanItem(ssid, 0, 1)
            elif line[0:6] == "level=" and item != None:
                (level, level_max) = line[6:].split("/")
                item.level = int(level)
                item.level_max = int(level_max)
                result.append(item)
                item = None
        return result
        
    def get_wlan_config(self):
        p = subprocess.Popen(['./network/get_wlan_config.sh'], stdout=subprocess.PIPE)
        source = p.stdout.read().decode("utf-8").strip()
        config = {}
        for line in source.split("\n"):
            (key, value) = line.split("=")
            if key == "psk":
                key = "pw"
            config[key] = value[1:-1]
        return config
    
    def change_wlan_config(self, ssid, pw):
        p = subprocess.Popen(['./network/change_wlan.sh', ssid, pw], stdout=subprocess.PIPE)
        p.stdout.read().decode("utf-8").strip()
        
        p = subprocess.Popen(['/sbin/wpa_cli', '-i', 'wlan0',  'reconfigure'], stdout=subprocess.PIPE)
        print(p.stdout.read().decode("utf-8").strip())
