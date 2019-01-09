from configparser import ConfigParser
from threading import Thread
from view.radio_view import KeyboardComponent
from time import sleep


class Controller:
    MAX_STATIONLIST_SIZE = 10000
    
    def __init__(self, play_view, select_view, setup_view, radio_service, player, network_service):
        self.favourites = {}
        
        self.play_view = play_view
        self.select_view = select_view
        self.setup_view = setup_view
        self.radio_service = radio_service
        self.player = player
        self.network_service = network_service
                
        self.station = None
        self.filter = ""
        self.stations = []
        self.filtered_stations = []
        self.filter_thread = None
        self.favourite = False
        self.load_station_list_thread = None

        self.known_wlan_list = {}

        self.load_config()

        self.bind_play_view()
        self.bind_select_view()
        self.bind_setup_view()
        
        self.leave_play_view()
        self.leave_setup_view()
        self.enter_select_view()

    def save_config(self):
        config = ConfigParser()
        config["stations"] = {"favourites" : ",".join(self.favourites)}
        config["wlan"] = {"known_wlan_list" : ","
                          .join("\"%s\":\"%s\"" % (key, value) for (key, value) in self.known_wlan_list.items())}
        with open('radio_pi.config', 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        config = ConfigParser()
        config.read('radio_pi.config')
        if config.has_section("stations"):
            self.favourites = config.get("stations", "favourites").split(",")
        else:
            self.favourites = []
        self.known_wlan_list = {}
        if config.has_section("wlan"):
            for item in config.get("wlan", "known_wlan_list").split(","):
                (key, value) = item.split(":")
                self.known_wlan_list[key[1:-1]] = value[1:-1]
        
# ------ play view ------

    def bind_play_view(self):
        self.play_view.handle_volume_down = self.handle_volume_down
        self.play_view.handle_volume_up = self.handle_volume_up
        self.play_view.handle_start = self.handle_start
        self.play_view.handle_stop = self.handle_stop
        self.play_view.handle_select_station = self.handle_select_station 
        self.play_view.handle_favourite = self.handle_favourite

    def enter_play_view(self):
        self.play_view.show()

    def leave_play_view(self):
        self.play_view.hide()

    def handle_select_station(self):
        self.leave_play_view()
        self.enter_select_view()
        return True

    def play_station(self, station):        
        self.station = station
        self.play_view.set_station(station)
        PlayStationThread(self.player, self.radio_service, station, self.play_view).start()

    def handle_volume_up(self):
        self.player.volume_up(2)
        return True
        
    def handle_volume_down(self):
        self.player.volume_down(2)
        return True
        
    def handle_start(self):
        self.player.start()
        return True

    def handle_stop(self):
        self.player.stop()
        return True

    def handle_favourite(self, favourite):
        self.station.set_favourite(favourite)
        if favourite:
            if not self.station.get_id() in self.favourites:
                self.favourites.append(self.station.get_id())
        else:
            if self.station.get_id() in self.favourites:
                self.favourites.remove(self.station.get_id())
        self.save_config()
        return True

# -------- select view --
    def bind_select_view(self):
        self.select_view.handle_select_up = self.handle_select_up
        self.select_view.handle_select_down = self.handle_select_down
        self.select_view.handle_select_key = self.handle_select_key
        self.select_view.handle_play_station = self.handle_play_station
        self.select_view.handle_setup = self.handle_setup

    def enter_select_view(self):
        self.select_view.show()
        self.start_load_station_list()

    def leave_select_view(self):
        self.select_view.hide()

    def handle_play_station(self, station):
        self.leave_select_view()
        self.enter_play_view()
        self.play_station(station)
        return True
        
    def handle_setup(self):
        self.leave_select_view()
        self.enter_setup_view()
        return True

    def handle_select_up(self):
        self.select_view.station_list_view.select_prev()
        return True

    def handle_select_down(self):
        self.select_view.station_list_view.select_next()
        return True

    def handle_select_return(self):
        self.play_view.show()
        self.select_view.hide()
        return True

    def handle_select_key(self, keycode):
        if keycode == 12:
            self.filter = self.filter[0:-1]
        elif keycode == 13:
            self.filter = ""
        elif keycode == 0x2d:
            return self.handle_select_return()
        elif keycode == 0x2e:
            self.favourite = True
        elif keycode == 0x2f:
            self.favourite = False
        else:
            self.filter = self.filter + KeyboardComponent.CHARSET[keycode]
        self.filterStations()
        return True

    def start_load_station_list(self):
        if len(self.stations) > 0:
            print("station list already filled")
            return
        if self.load_station_list_thread:
            self.load_station_list_thread.interrupt()
        self.load_station_list_thread = InterruptableThread().with_runnable(self.load_station_list)
        self.load_station_list_thread.start()

    def load_station_list(self):
        self.select_view.set_stations([], "")
        self.select_view.station_list_view.set_empty_message("_LOADING STATION LIST...^")
        self.select_view.station_list_view.set_items([])
        self.stations = self.radio_service.find_stations_by_topvote(Controller.MAX_STATIONLIST_SIZE)
        if self.load_station_list_thread.is_interrupted():
            return
        for station in self.stations:
            if station.get_id() in self.favourites:
                station.set_favourite(True)            
        self.filtered_stations = self.stations
        self.select_view.set_stations(self.stations, "")

    def filterStations(self):
        if self.filter_thread != None:
            self.filter_thread.interrupt()
        self.filter_thread = FilterStations(self.select_view, self, self.filter, self.favourite)
        self.filter_thread.start()

# -------- setup view --

    def bind_setup_view(self):
        self.setup_view.handle_select_up = self.handle_wlan_up 
        self.setup_view.handle_select_down = self.handle_wlan_down
        self.setup_view.handle_select_wlan = self.handle_setup_select
        self.setup_view.handle_change_password = self.handle_change_wlan
        self.setup_view.handle_return_key = self.handle_setup_return_key
        self.setup_view.handle_scan_wlan = self.handle_scan_wlan
        InterruptableThread().with_runnable(self.refresh_wlan_config).start()
        InterruptableThread().with_runnable(self.refresh_wlan_list).start()
        self.timer_thread = None
        
    def enter_setup_view(self):
        self.setup_view.show()
        self.timer_thread = TimerThread(3).with_runnable(self.refresh_ips)
        self.timer_thread.start()
        
    def leave_setup_view(self):
        self.setup_view.hide()
        if self.timer_thread:
            self.timer_thread.interrupt()

    def handle_setup_return_key(self):
        self.leave_setup_view()
        self.enter_select_view()
        return True

    def handle_wlan_up(self):
        self.setup_view.wlan_list_view.select_prev()
        return True

    def handle_wlan_down(self):
        self.setup_view.wlan_list_view.select_next()
        return True

    def handle_setup_select(self, item):
        self.setup_view.set_ssid(item.ssid)
        if item.ssid in self.known_wlan_list.keys():
            self.setup_view.set_pw(self.known_wlan_list[item.ssid])
        else:
            self.setup_view.set_pw("")
        return True
        
    def handle_change_wlan(self):
        self.known_wlan_list[self.setup_view.get_ssid()] = self.setup_view.get_pw()
        self.save_config() 
        InterruptableThread().with_runnable(self.change_wlan).start()
        return True

    def handle_scan_wlan(self):
        self.setup_view.set_wlan_list([])
        InterruptableThread().with_runnable(self.refresh_wlan_list).start()        
        
    def change_wlan(self):
        self.network_service.change_wlan_config(self.setup_view.get_ssid(), self.setup_view.get_pw())
        
    def refresh_wlan_list(self):
        self.setup_view.set_wlan_list(self.network_service.refresh_wlan_list())

    def refresh_ips(self):
        ips = self.network_service.refresh_ips()
        self.setup_view.set_ips(ips["lan"], ips["wlan"])

    def refresh_wlan_config(self):
        setting = self.network_service.get_wlan_config()
        self.setup_view.set_ssid(setting["ssid"])
        self.setup_view.set_pw(setting["pw"])
        self.known_wlan_list[setting["ssid"]] = setting["pw"] 
        self.save_config()

# -------- util --

# -------- threads --

class InterruptableThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.runnable = lambda: False
        self.interrupted = False
    
    def interrupt(self):
        self.interrupted = True
        
    def is_interrupted(self):
        return self.interrupted
    
    def with_runnable(self, runnable):
        self.runnable = runnable
        return self

    def get_runnable(self):
        return self.runnable

    def run(self):
        self.runnable()


class TimerThread(InterruptableThread):

    def __init__(self, delay):
        InterruptableThread.__init__(self)
        self.delay = delay
        self.running_thread = None

    def run(self):
        while not self.is_interrupted():
            if self.running_thread:
                self.running_thread.interrupt()                
            self.running_thread = InterruptableThread().with_runnable(self.get_runnable())
            self.running_thread.start()
            sleep(self.delay)
        if self.running_thread:
            self.running_thread.interrupt()

class PlayStationThread(Thread):

    def __init__(self, radio_player, radio_service, station, play_view):
        Thread.__init__(self)
        self.radio_player = radio_player
        self.radio_service = radio_service
        self.station = station
        self.play_view = play_view
    
    def run(self):
        url = self.radio_service.get_playable_url(self.station.get_id())
        if url != None:
            self.radio_player.play_url(url)
        else:
            self.play_view.set_station(None)

            
class FilterStations(Thread):

    def __init__(self, select_view, controller, pattern, favourite):
        Thread.__init__(self)
        self.select_view = select_view
        self.controller = controller
        self.pattern = pattern
        self.favourite = favourite
        self.interrupted = False

    def interrupt(self):
        self.interrupted = True
        
    def run(self):
        stations = self.controller.stations
        selected_stations = []
        f = self.pattern.upper().split()        
        i = 0
        while i < len(stations) and len(selected_stations) < 100:
            station = stations[i]
            if (self.interrupted):
                return
            info = ("%s %s %s %s" % (
                station.get_name(),
                station.get_location(),
                " ".join(station.get_tags()),
                station.get_codec(),
                )).upper()
            matches = (not self.favourite) or (self.favourite and station.get_favourite())
            for w in f:
                if info.find(w) < 0:
                    matches = False
            if matches: 
                selected_stations.append(station)
            i = i + 1
        self.controller.filtered_stations = selected_stations
        self.select_view.set_stations(selected_stations, self.pattern)
