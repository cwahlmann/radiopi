from subprocess import call

class Player:
    def play_url(self, url):
        print("play url '%s'" % url)
    
    def volume_up(self, amount):
        print("volume up '%d'" % amount)
    
    def volume_down(self, amount):
        print("volume down '%d'" % amount)
    
    def stop(self):
        print("stop")
    
    def start(self):
        print("start")

class VlcPlayer(Player):
    def __init__(self, remote):
        self.remote = remote

    def play_url(self, url):
        self.do("clear")
        self.do("add %s" % url)
        
    def volume_up(self, amount):
        self.do("volup %d" % amount)

    def volume_down(self, amount):
        self.do("voldown %d" % amount)

    def stop(self):
        self.do("stop")

    def start(self):
        self.do("play")

    def do(self, command):
        call([self.remote, command])
