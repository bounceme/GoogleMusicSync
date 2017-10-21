import gmusicapi
import os
import sys
import time
import re
from mutagen.id3 import ID3, POPM
from mutagen.mp4 import MP4

def mfor(path):
    inf = MP4(path).tags
    ti = inf['\xa9nam'][0]
    ar = inf['\xa9ART'][0]
    return [ti,ar]


def build_dict():
    t = MusicDict()
    t.add_folder(os.path.expandvars("$HOME/Music/"))
    #t.add_folder("C:\\Users\\Random\\Desktop")
    #t.add_folder("C:\\Users\\Random\\Downloads")
    #t.add_folder("C:\\Users\\Random\\Music")
    return t


# songs: (title, artist) = [rating, path, title, artist]
class MusicDict():
    def __init__(self):
        self.songs = {}
        self.size= 0
        
    def find_song(self, title, artist=''):
        if (title, artist) in self.songs:
            return self.songs[(title, artist)]
        return {}
        
    def add_folder(self, path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        for phile in files:
            if(len(re.findall(".*(mp3|mp4|m4a)+", phile)) != 0):
                file_info = {'path': os.path.join(path, phile), 'filename': phile}
                if('m4a' in phile):
                    va = mfor(file_info['path'])
                    self.songs[(va[0],va[1])] = va
                elif('mp4' in phile):
                    va = mfor(file_info['path'])
                    self.songs[(va[0],va[1])] = va
                elif('mp3' in phile):
                    audio = ID3(file_info['path'])
                    file_info['title'] = audio.get('TIT2').text[0]
                    file_info['artist'] = audio.get('TPE1').text[0]
                    self.songs[(file_info['title'], file_info['artist'])] = file_info
                self.size+=1
                if(self.size % 100 == 0):
                    print self.size, " songs found"
        for folder in folders:
            self.add_folder(os.path.join(path, folder))
            
    def song_exists(self, title, artist=''):
        return (title, artist) in self.songs


print "Beginning program"

print "Building dictionary of songs on computer"
start = time.clock()
music_dict = build_dict()
print "Done building"
print "Time taken", time.clock()-start
print "Songs found: ", music_dict.size

start = time.clock()
print "Getting music from google"
google_music = gmusicapi.Mobileclient()
google_music.login(sys.argv[1],sys.argv[2],google_music.FROM_MAC_ADDRESS)
google_songs = google_music.get_all_songs()
print "Time taken", time.clock()-start

delete_songs = []
print 'Putting google songs in a dictionary'
print "Removing music from google play that does not exist on computer."
for song in google_songs:
    if not music_dict.song_exists(song["title"], song["artist"]):
        print "Deleting "+song["title"]+" by "+song["artist"]+" remotely"
        #response = raw_input("Do you want to delete this song? (y/n): ")
        response = 'y'
        if(response!="n"):
                delete_songs.append(song["id"])
try:
    print delete_songs
    # google_music.delete_songs(delete_songs)
except Exception as e:
    print e

print "Completed"
