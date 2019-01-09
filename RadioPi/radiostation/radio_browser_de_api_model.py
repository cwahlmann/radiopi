import requests
import json
from radiostation.model import Station, ListOfItem


class RadioBrowserDeStation (Station):

    def __init__(self, data):
        super().__init__(data)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    
    def get_homepage(self):
        return self.homepage

    def get_tags(self):
        return self.tags.split(",")

    def get_location(self):
        if (not self.state):
            return "%s - %s" % (self.country, self.language)
        return "%s (%s) - %s" % (self.country, self.state, self.language)
    
    def get_codec(self):
        return "%s (%s)" % (self.codec, self.bitrate)
    
    def get_icon(self):    
        return self.favicon

    def get_votes(self):
        return self.votes
    
    def get_negative_votes(self):
        return self.negativevotes


class RadioBrowserDeListOfItem (ListOfItem):

    def __init__(self, data):
        super().__init__(data)

    def get_name(self):
        return self.value
    
    def get_count(self):
        return self.stationcount

    
class RadioBrowserDeMapper:    

    def as_station(self, data):
        return RadioBrowserDeStation(data)

    def as_list_of_item(self, data):
        return RadioBrowserDeListOfItem(data)


class RadioBrowserDeClient:

    def __init__(self):
        self.mapper = RadioBrowserDeMapper()

    def find_stations_by_id(self, search_string):
        return self.find_stations_by("id", search_string)

    def find_stations_by_name(self, search_string):
        return self.find_stations_by("name", search_string)

    def find_stations_by_codec(self, search_string):
        return self.find_stations_by("codec", search_string)

    def find_stations_by_codecexact(self, search_string):
        return self.find_stations_by("codecexact", search_string)

    def find_stations_by_country(self, search_string):
        return self.find_stations_by("country", search_string)

    def find_stations_by_countryexact(self, search_string):
        return self.find_stations_by("countryexact", search_string)

    def find_stations_by_language(self, search_string):
        return self.find_stations_by("language", search_string)

    def find_stations_by_tag(self, search_string):
        return self.find_stations_by("tag", search_string)

    def find_stations_by_tagexact(self, search_string):
        return self.find_stations_by("tagexact", search_string)

    def find_stations_by(self, category, name):
        return self.request_and_map(
            "http://www.radio-browser.info/webservice/json/stations/by%s/%s" % (category, name), 
            self.mapper.as_station)

    def find_stations_by_topvote(self, rows):
        if (not rows):            
            return self.request_and_map(
                "http://www.radio-browser.info/webservice/json/stations/topvote", 
                self.mapper.as_station)
        else:
            return self.request_and_map(
                "http://www.radio-browser.info/webservice/json/stations/topvote/%s" % rows, 
                self.mapper.as_station)

    def get_countries(self, filter_string):
        return self.get_list_of_item("countries", filter_string)

    def get_codecs(self, filter_string):
        return self.get_list_of_item("codecs", filter_string)

    def get_languages(self, filter_string):
        return self.get_list_of_item("languages", filter_string)

    def get_tags(self, filter_string):
        return self.get_list_of_item("tags", filter_string)
        
    def get_list_of_item(self, category, filter_string): 
        if (filter_string):
            return self.request_and_map(
                "http://www.radio-browser.info/webservice/json/%s/%s" % (category, filter_string),
                self.mapper.as_list_of_item)
        else:
            return self.request_and_map(
                "http://www.radio-browser.info/webservice/json/%s" % category,
                self.mapper.as_list_of_item)

    def get_playable_url(self, station_id):
        try:
            response = requests.get("http://www.radio-browser.info/webservice/json/url/%s" % station_id)
            source = response.text
            return json.loads(source)[0]["url"]
        except Exception:
            return None

    def request_and_map(self, url, map_func):
        response = requests.get(url)
        source = response.text
        return json.loads(source, object_hook=map_func)
    
