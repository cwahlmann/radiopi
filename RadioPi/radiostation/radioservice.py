class RadioService:

    def __init__(self, client):
        self.client = client
        
    def find_stations_by_id(self, search_string):
        return self.client.find_stations_by("id", search_string)

    def find_stations_by_name(self, search_string):
        return self.client.find_stations_by("name", search_string)

    def find_stations_by_codec(self, search_string):
        return self.client.find_stations_by("codec", search_string)

    def find_stations_by_codecexact(self, search_string):
        return self.client.find_stations_by("codecexact", search_string)

    def find_stations_by_country(self, search_string):
        return self.client.find_stations_by("country", search_string)

    def find_stations_by_countryexact(self, search_string):
        return self.client.find_stations_by("countryexact", search_string)

    def find_stations_by_language(self, search_string):
        return self.client.find_stations_by("language", search_string)

    def find_stations_by_tag(self, search_string):
        return self.client.find_stations_by("tag", search_string)

    def find_stations_by_tagexact(self, search_string):
        return self.client.find_stations_by("tagexact", search_string)

    def find_stations_by_topvote(self, rows):
        return self.client.find_stations_by_topvote(rows)

    def get_playable_url(self, station_id):
        return self.client.get_playable_url(station_id)
    
    def get_countries(self, filter_string):
        return self.client.get_list_of_item("countries", filter_string)
    