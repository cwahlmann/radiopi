from configparser import ConfigParser
from threading import Thread

from audiofile.audiofileservice import AudiofileService
from clock.clock import AlarmClock, Time
from controller.threads import InterruptableThread, TimerThread
from view.radio_view import KeyboardComponent


class Controller:
    MAX_STATIONLIST_SIZE = 10000
    
    def __init__(self, play_view, select_view, select_music_view, setup_view, setup_clock_view, radio_service, player, network_service, audiofile_service):
        self.favourites = {}
        
        self.play_view = play_view
        self.select_view = select_view
        self.select_music_view = select_music_view
        self.setup_view = setup_view
        self.setup_clock_view = setup_clock_view
        self.radio_service = radio_service
        self.player = player
        self.network_service = network_service
        self.clock = AlarmClock()
        self.clock.on_tick(self.on_tick)
        self.clock.on_sleep(self.on_sleep)
        self.clock.on_wake(self.on_wake)
        self.audiofile_service = audiofile_service
                
        self.station = None
        self.filter = ""
        self.stations = []
        self.filtered_stations = []
        self.filter_thread = None
        self.favourite = False
        self.load_station_list_thread = None

        self.root_path = "D:\medien"
        self.file = None
        self.filter_file = ""
        self.files = []
        self.filtered_files = []
        self.filter_file_thread = None
        self.favourite_files = []
        self.load_file_list_thread = None

        self.known_wlan_list = {}

        self.load_config()

        self.bind_play_view()
        self.bind_select_view()
        self.bind_select_music_view()
        self.bind_setup_view()
        self.bind_setup_clock_view()
        
        self.leave_play_view()
        self.leave_setup_view()
        self.enter_select_view()
        self.leave_select_music_view()
        self.leave_setup_clock_view()

    def save_config(self):
        config = ConfigParser()
        config["stations"] = {"favourites" : ",".join(self.favourites)}
        config["wlan"] = {"known_wlan_list" : ","
                          .join("\"%s\":\"%s\"" % (key, value) for (key, value) in self.known_wlan_list.items())}
        
        config["clock"] = {
            "wake_enabled" : self.setup_clock_view.wake_time_field.time_enabled,
            "wake_time" : self.setup_clock_view.wake_time_field.get_time().serialize(),
            "sleep_enabled" : self.setup_clock_view.sleep_time_field.time_enabled,
            "sleep_time" : self.setup_clock_view.sleep_time_field.get_time().serialize(),
            "time_offset" : self.setup_clock_view.time_field.get_time().serialize()
            }
        
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
        if (config.has_section("clock")):
            self.setup_clock_view.wake_time_field.time_enabled = bool(config.get("clock", "wake_enabled")) 
            self.setup_clock_view.wake_time_field.set_time(Time().deserialize(config.get("clock", "wake_time"))) 
            self.setup_clock_view.sleep_time_field.time_enabled = bool(config.get("clock", "sleep_enabled")) 
            self.setup_clock_view.sleep_time_field.set_time(Time().deserialize(config.get("clock", "sleep_time"))) 
            self.setup_clock_view.time_field.set_time(Time().deserialize(config.get("clock", "time_offset"))) 
            
# ------ clock event handler --

    def on_tick(self, t):
        self.play_view.clock.with_time(t)
        self.select_view.clock.with_time(t)
        self.setup_view.clock.with_time(t)
        self.setup_clock_view.clock.with_time(t)
        
        if self.clock.sleep_enabled:
            self.play_view.clock.with_sleep_time(self.clock.get_sleep())
            self.select_view.clock.with_sleep_time(self.clock.get_sleep())
            self.setup_view.clock.with_sleep_time(self.clock.get_sleep())
            self.setup_clock_view.clock.with_sleep_time(self.clock.get_sleep())
        else:
            self.play_view.clock.disable_sleep()
            self.select_view.clock.disable_sleep()
            self.setup_view.clock.disable_sleep()
            self.setup_clock_view.clock.disable_sleep()
            
        if self.clock.wake_enabled:
            self.play_view.clock.with_wake_time(self.clock.get_wake())
            self.select_view.clock.with_wake_time(self.clock.get_wake())
            self.setup_view.clock.with_wake_time(self.clock.get_wake())
            self.setup_clock_view.clock.with_wake_time(self.clock.get_wake())
        else:
            self.play_view.clock.disable_wake()
            self.select_view.clock.disable_wake()
            self.setup_view.clock.disable_wake()
            self.setup_clock_view.clock.disable_wake()
        
        self.setup_clock_view.time_field.set_offset(t.sub(self.clock.get_offset()))
        
    def on_sleep(self, t):
        self.play_view.show_start_button = False
        self.play_view.handle_start_stop()

    def on_wake(self, t):
        self.leave_select_view()
        self.leave_setup_view()
        self.leave_setup_clock_view()
        self.enter_play_view()

        self.play_view.show_start_button = True
        self.play_view.handle_start_stop()
        
# ------ play view ------

    def bind_play_view(self):
        self.play_view.handle_volume_down = self.handle_volume_down
        self.play_view.handle_volume_up = self.handle_volume_up
        self.play_view.handle_start = self.handle_start
        self.play_view.handle_stop = self.handle_stop
        self.play_view.handle_select_music = self.handle_select_music
        self.play_view.handle_select_station = self.handle_select_station 
        self.play_view.handle_favourite = self.handle_favourite
        self.play_view.handle_push_clock = self.handle_select_setup_clock
        self.play_view.handle_setup = self.handle_setup

    def enter_play_view(self):
        self.play_view.show()

    def leave_play_view(self):
        self.play_view.hide()

    def handle_select_station(self):
        self.leave_play_view()
        self.enter_select_view()
        return True

    def handle_select_music(self):
        self.leave_play_view()
        self.enter_select_music_view()
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

    def handle_setup(self):
        self.leave_play_view()
        self.enter_setup_view()
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
        self.select_view.handle_push_clock = self.handle_select_setup_clock

    def enter_select_view(self):
        self.select_view.show()
        self.start_load_station_list()

    def leave_select_view(self):
        self.select_view.hide()

    def handle_select_setup_clock(self):
        self.leave_play_view()
        self.leave_select_view()
        self.leave_setup_view()
        self.enter_setup_clock_view()
        return True

    def handle_play_station(self, station):
        self.leave_select_view()
        self.enter_play_view()
        self.play_station(station)
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

    def handle_push_clock(self):
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

# -------- select music view --
    def bind_select_music_view(self):
        self.select_music_view.handle_select_up = self.handle_select_up
        self.select_music_view.handle_select_down = self.handle_select_down
        self.select_music_view.handle_select_music_key = self.handle_select_music_key
        self.select_music_view.handle_play_file = self.handle_play_file
        self.select_music_view.handle_push_clock = self.handle_select_setup_clock

    def enter_select_music_view(self):
        self.select_music_view.show()
        self.start_load_file_list()

    def leave_select_music_view(self):
        self.select_music_view.hide()

    def handle_select_music_setup_clock(self):
        self.leave_play_view()
        self.leave_select_music_view()
        self.leave_setup_view()
        self.enter_setup_clock_view()
        return True

    def handle_play_file(self, file):
        self.leave_select_music_view()
        self.enter_play_view()
#        self.play_file(station)
        return True
        
    def handle_select_music_up(self):
        self.select_music_view.file_list_view.select_prev()
        return True

    def handle_select_music_down(self):
        self.select_music_view.file_list_view.select_next()
        return True

    def handle_select_music_return(self):
        self.play_view.show()
        self.select_music_view.hide()
        return True

    def handle_select_music_push_clock(self):
        self.play_view.show()
        self.select_music_view.hide()
        return True

    def handle_select_music_key(self, keycode):
        if keycode == 12:
            self.filter_file = self.filter_file[0:-1]
        elif keycode == 13:
            self.filter_file = ""
        elif keycode == 0x2d:
            return self.handle_select_music_return()
        elif keycode == 0x2e:
            self.favourite = True
        elif keycode == 0x2f:
            self.favourite = False
        else:
            self.filter_file = self.filter_file + KeyboardComponent.CHARSET[keycode]
        self.filter_files()
        return True

    def start_load_file_list(self):
        if len(self.files) > 0:
            print("file list already filled")
            return
        if self.load_file_list_thread:
            self.load_file_list_thread.interrupt()
        self.load_file_list_thread = InterruptableThread().with_runnable(self.load_file_list)
        self.load_file_list_thread.start()

    def load_file_list(self):
        self.select_music_view.set_files([], "")
        self.select_music_view.file_list_view.set_empty_message("_LOADING FILE LIST...^")
        self.select_music_view.file_list_view.set_items([])
        self.files = self.audiofile_service.read_files(self.root_path)
        if self.load_file_list_thread.is_interrupted():
            return
        for file in self.files:
            if file.tags[AudiofileService.TAG_PATH] in self.favourite_files:
                file.set_favourite(True)            
        self.filtered_files = self.files
        self.select_music_view.set_files(self.files, "")

    def filter_files(self):
        if self.filter_thread != None:
            self.filter_thread.interrupt()
        self.filter_thread = FilterFiles(self.select_music_view, self, self.filter, self.favourite)
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
        self.setup_view.handle_push_clock = self.handle_select_setup_clock
        
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
        self.enter_play_view()
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

# -------- setup clock --

    def bind_setup_clock_view(self):
        self.setup_clock_view.key_enter_handler = self.handle_confirm
        self.setup_clock_view.key_back_handler = self.handle_back

    def enter_setup_clock_view(self):
        self.setup_clock_view.show()

    def leave_setup_clock_view(self):
        self.setup_clock_view.hide()

    def handle_confirm(self):
        wake_enabled = self.setup_clock_view.wake_time_field.time_enabled
        wake_time = self.setup_clock_view.wake_time_field.get_time()

        sleep_enabled = self.setup_clock_view.sleep_time_field.time_enabled
        sleep_time = self.setup_clock_view.sleep_time_field.get_time()

        time_offset = self.setup_clock_view.time_field.get_time()

        self.clock.with_offset(time_offset)

        if wake_enabled:
            self.clock.with_wake(wake_time)
        else:
            self.clock.with_no_wake()

        if sleep_enabled:
            self.clock.with_sleep(sleep_time)
        else:
            self.clock.with_no_sleep()

        self.save_config()
                
        self.leave_setup_clock_view()
        self.enter_select_view()
            
    def handle_back(self):
        if self.clock.wake_enabled:        
            self.setup_clock_view.wake_time_field.set_time(self.clock.get_wake())
        else:
            self.setup_clock_view.wake_time_field.clear()

        if self.clock.sleep_enabled:        
            self.setup_clock_view.sleep_time_field.set_time(self.clock.get_sleep())
        else:
            self.setup_clock_view.sleep_time_field.clear()

        self.setup_clock_view.time_field.set_time(self.clock.get_offset())
        
        self.leave_setup_clock_view()
        self.enter_select_view()

# -------- util --

# -------- threads -
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

class FilterFiles(Thread):

    def __init__(self, select_music_view, controller, pattern, favourite):
        Thread.__init__(self)
        self.select_music_view = select_music_view
        self.controller = controller
        self.pattern = pattern
        self.favourite = favourite
        self.interrupted = False

    def interrupt(self):
        self.interrupted = True
        
    def run(self):
        files = self.controller.files
        selected_files = []
        f = self.pattern.upper().split()        
        i = 0
        while i < len(files) and len(selected_files) < 100:
            files= files[i]
            if (self.interrupted):
                return
            info = ("%s %s %s %s" % (
                files.get_name(),
                files.get_location(),
                " ".join(files.get_tags()),
                files.get_codec(),
                )).upper()
            matches = (not self.favourite) or (self.favourite and files.get_favourite())
            for w in f:
                if info.find(w) < 0:
                    matches = False
            if matches: 
                selected_files.append(files)
            i = i + 1
        self.controller.filtered_files= selected_files
        self.select_music_view.set_files(selected_files, self.pattern)
