import os
#import mutagen

class AudiofileService:

    TAG_PATH = "path"
    TAG_TITLE = "title"
    TAG_ALBUM = "album"
    TAG_AUTHOR = "author"
    TAG_TRACK = "track"
    TAG_ALBUM_NO = "album_no"
    TAG_GENRE = "genre"
    TAG_DATE = "date"

    def __init__(self):
        self.x = ""
        
    def read_files(self, path):
        files = []
        for r, d, f in os.walk(path):
            for file in f:
                (dummy, extension) = os.path.splitext(file)
                if extension in ('.mp3', '.MP3'):
                    files.append(Mp3file(os.path.join(r, file)))
                elif extension in ('.ogg', '.OGG'):
                    files.append(Oggfile(os.path.join(r, file)))
        return files

    def read_paths(self, path):
        paths = []
        for r, d, f in os.walk(path):
            for dd in d:
                paths.append(os.path.join(r, dd))
        return paths

#MP3
#TALB        Name des Albums
#TPE1        Interpret/-in/-en ("Artist")
#TPE2        Album-Interpret/-in/-en ("Album Artist")
#TPE3    K    Dirigent
#TIT1    K    Name des Werks, etwa Sinfonie Nr. oder My Fair Lady
#TIT2    P    Name des Musikstücks
#        K    Satzbezeichnung oder Titel
#TIT3    K    Titelzusatz
#TCOM    K    Komponist ("composer")
#TRCK        Stücknummer/Anzahl Stücke ("Track Number")
#TPOS        CD-Nummer/Anzahl CDs ("Disk Number")
#TCON        Genre (freier Text oder numerisch)
#COMM        Kommentar ("comment")
#TORY        "original year"
#TDRC        "year"
#APIC        Hier sind Bilder enthalten, als .jpg oder .png
#MVNM    K    Satzbezeichnung (Apple-proprietär)
#MVIN    K    Satznummer/Anzahl Sätze (Apple-proprietär)
#GRP1    K    Gruppierung (Apple-proprietär)
# K=Klassik; P=Pop

class Mp3file:
    def __init__(self, path):
#        mp3 = mutagen.File(path)
        tags = {}
#mp3.tags

        self.favourite = False
        self.tags = {}
        self.tags[AudiofileService.TAG_PATH] = path
        self.tags[AudiofileService.TAG_TITLE] = self.get(tags, "TIT2")
        self.tags[AudiofileService.TAG_ALBUM] = self.get(tags, "TALB")
        self.tags[AudiofileService.TAG_AUTHOR] = self.get(tags, "TPE1")
        self.tags[AudiofileService.TAG_TRACK] = self.get(tags, "TRCK")
        self.tags[AudiofileService.TAG_ALBUM_NO] = self.get(tags, "TPOS")
        self.tags[AudiofileService.TAG_GENRE] = self.get(tags, "TCON")
        self.tags[AudiofileService.TAG_DATE] = self.get(tags, "TDRC")
        
    def get(self, t, key):
        if t == None:
            return ""
        if key in t:
            return t[key].text[0]
        return ""

    def get_favourite(self):
        return self.favourite;
    
    def set_favourite(self, favourite):
        self.favourite = favourite;
    
#OGG
#TITLE    Titel    
#VERSION    Version    Das Versionsfeld kann benutzt werden, um mehrere Versionen des gleichen Titels in einer einzelnen Ansammlung zu unterscheiden (z. B. remix-Informationen).
#ALBUM    Album    Der Name des Albums, zu dem der Titel gehört
#TRACKNUMBER    St�cknummer    Die Position des Titels auf dem Album
#ARTIST    K�nstler    In der Popmusik ist dies normalerweise die Band oder der S�nger. F�r klassische Musik wäre es der Komponist. F�r ein Audiobuch wäre es der Autor des ursprünglichen Textes.
#PERFORMER    Interpret    Die Künstler, die die Arbeit durchf�hrten. In der klassischen Musik w�re das der Dirigent, das Orchester und die Solisten. In einem Audiobuch w�re es der Vorleser. In der Popmusik ist dies gew�hnlich der gleiche Eintrag wie im Feld ARTIST und wird ausgelassen.
#COPYRIGHT    Urheberrecht    Copyrightzuerkennung z. B.: �2001 Nobody's Band� oder �1999 Jack Moffitt�.
#LICENSE    Lizenzinformationen    z. B. �Alle Rechte vorbehalten� oder eine URL zu einer Lizenz wie Creative Commons license.
#ORGANISATION    Organisation    Name der Organisation, die den Titel produziert hat (d. h. das Plattenlabel)
#DESCRIPTION    Beschreibung    Eine Kurztextbeschreibung des Inhalts
#GENRE    Genre    Das Musikgenre des Titels
#DATE    Datum    Das Aufnahmedatum des Titels
#LOCATION    Ort    Der Ort, an dem der Titel produziert wurde
#CONTACT    Kontaktinformationen    Dieses k�nnte z. B. eine URL oder ein E-Mail-Adresse sein.
#ISRC    ISRC-Code    Der International Standard Recording Code ist eine zw�lfstellige digitale Kennung f�r einen CD-Titel.

class Oggfile:
    def __init__(self, path):
        #ogg = mutagen.File(path)
        tags = {} #ogg.tags.as_dict()
        
        self.favourite = False
        self.tags = {}
        self.tags[AudiofileService.TAG_PATH] = path
        self.tags[AudiofileService.TAG_TITLE] = self.get(tags, "TITLE")
        self.tags[AudiofileService.TAG_ALBUM] = self.get(tags, "ALBUM")
        self.tags[AudiofileService.TAG_AUTHOR] = self.get(tags, "ARTIST")
        self.tags[AudiofileService.TAG_TRACK] = self.get(tags, "TRACKNUMBER")
        self.tags[AudiofileService.TAG_ALBUM_NO] = self.get(tags, "")
        self.tags[AudiofileService.TAG_GENRE] = self.get(tags, "GENRE")
        self.tags[AudiofileService.TAG_DATE] = self.get(tags, "DATE")
        
    def get(self, t, key):
        if t == None:
            return ""
        if key in t:
            return t[key].text[0]
        return ""

    def get_favourite(self):
        return self.favourite;
    
    def set_favourite(self, favourite):
        self.favourite = favourite;

#files = s.read_files("D:\\")
#for f in files:
#    print(f.tags)

