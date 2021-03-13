class Station:

    def __init__(self, data):
        self.__dict__.update(data)
        self.favourite = False
        
    def get_id(self):
        return "undef"

    def get_favourite(self):
        return self.favourite

    def set_favourite(self, favourite):
        self.favourite = favourite

    def get_name(self):
        return "undef"
    
    def get_homepage(self):
        return "undef"

    def get_playable_url(self):
        return "undef"

    def get_tags(self):
        return ["undef"]

    def get_location(self):
        return "undef"
    
    def get_codec(self):
        return "undef"
    
    def get_icon(self):    
        return "undef"

    def get_votes(self):
        return 0
    
    def get_negative_votes(self):
        return 0
    
    def get_info(self):
        return "-------- %s (%s/%s) --\n%s\n%s\n%s - %s\n" % (self.get_name(), self.get_votes(), self.get_negative_votes(), self.get_tags(), self.get_location(), self.get_codec(), self.get_homepage())

class ListOfItem:
    def __init__(self, data):
        self.__dict__.update(data)

    def get_name(self):
        return ""
    
    def get_count(self):
        return 0

    def get_info(self):
        return "%s (%s)" % (self.get_name(), self.get_count())
    