import requests
import json
import random
import socket
import urllib
import urllib.request

from radiostation.model import Station, ListOfItem


class RadioBrowserDeStation(Station):

    def __init__(self, data):
        super().__init__(data)

    def get_id(self):
        return self.stationuuid

    def get_name(self):
        return self.name

    def get_homepage(self):
        return self.homepage

    def get_playable_url(self):
        return self.url_resolved

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
        return 0


class RadioBrowserDeListOfItem(ListOfItem):

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
            "/json/stations/by%s/%s" % (category, name), None,
            self.mapper.as_station)

    def find_stations_by_topvote(self, rows):
        if (not rows):
            return self.request_and_map(
                "/json/stations/topvote", None,
                self.mapper.as_station)
        else:
            return self.request_and_map(
                "/json/stations/topvote/%s" % rows, None,
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
                "/json/%s/%s" % (category, filter_string), None,
                self.mapper.as_list_of_item)
        else:
            return self.request_and_map(
                "/json/%s" % category, None,
                self.mapper.as_list_of_item)

    def request_and_map(self, url, param, map_func):
        stations = self.downloadRadiobrowser(url, param)
        return json.loads(stations, object_hook=map_func)

    def downloadRadiobrowser(self, path, param):
        """
        Download file with relative url from a random api server.
        Retry with other api servers if failed.

        Returns:
        a string result

        """
        servers = self.get_radiobrowser_base_urls()
        random.shuffle(servers)
        i = 0
        for server_base in servers:
            print('Random server: ' + server_base + ' Try: ' + str(i))
            uri = server_base + path

            try:
                data = self.downloadUri(uri, param)
                return data
            except Exception as e:
                print("Unable to download from api url: " + uri, e)
                pass
            i += 1
        return {}

    def get_radiobrowser_base_urls(self):
        """
        Get all base urls of all currently available radiobrowser servers

        Returns:
        list: a list of strings

        """
        hosts = []
        # get all hosts from DNS
        ips = socket.getaddrinfo('all.api.radio-browser.info',
                                 80, 0, 0, socket.IPPROTO_TCP)
        for ip_tupple in ips:
            ip = ip_tupple[4][0]

            # do a reverse lookup on every one of the ips to have a nice name for it
            host_addr = socket.gethostbyaddr(ip)
            # add the name to a list if not already in there
            if host_addr[0] not in hosts:
                hosts.append(host_addr[0])

        # sort list of names
        hosts.sort()
        # add "https://" in front to make it an url
        return list(map(lambda x: "https://" + x, hosts))

    def downloadUri(self, uri, param):
        """
        Download file with the correct headers set

        Returns:
        a string result

        """
        paramEncoded = None
        if param != None:
            paramEncoded = json.dumps(param).encode("UTF-8")
            print('Request to ' + uri + ' Params: ' + ','.join(param))
        else:
            print('Request to ' + uri)

        req = urllib.request.Request(uri, paramEncoded)
        # TODO: change the user agent to name your app and version
        req.add_header('User-Agent', 'MyApp/0.0.1')
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        data = response.read()

        response.close()
        return data
