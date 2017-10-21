import gmusicapi
import os
import sys
import time
import re
from mutagen.id3 import ID3, POPM
print sys.argv

def get_local_info(song_info):
    song_info['rating'] = -1
    song_info['title'] = song_info['filename']
    song_info['artist'] = ''
    if(song_info['type'] == 'mp3'):
        try:
            audio = ID3(song_info['path'])
            rate_temp = audio.getall('POPM')
            if(len(rate_temp) >= 1):
                song_info['rating'] = rate_temp[0].rating
            song_info['title'] = audio.get('TIT2').text[0]
            song_info['artist'] = audio.get('TPE1').text[0]
        except:
            return
    else:
        return

def get_remote_info(google_music_dict, song_info):
    if (song_info['title'], song_info['artist']) in google_music_dict:
        return google_music_dict[(song_info['title'], song_info['artist'])]
    else:
        return {}

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
                    file_info['type'] = 'm4a'
                if('mp4' in phile):
                    file_info['type'] = 'mp4'
                if('mp3' in phile):
                    file_info['type'] = 'mp3'
                get_local_info(file_info)
                self.songs[(file_info['title'], file_info['artist'])] = file_info
                self.size+=1
                if(self.size % 1000 == 0):
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
google_songs_dict = {}
print "Time taken", time.clock()-start

print 'Putting google songs in a dictionary'
for song in google_songs:
    google_songs_dict[(song["title"].encode('ascii', 'ignore'), song["artist"].encode('ascii', 'ignore'))] = song
print google_songs
print "Removing music from google play that does not exist on computer."
delete_songs = []
for song in google_songs:
    if not music_dict.song_exists(song["title"].encode('ascii', 'ignore'), song["artist"].encode('ascii', 'ignore')):
        print "Deleting "+song["title"].encode('ascii', 'ignore')+" by "+song["artist"].encode('ascii', 'ignore')+" remotely"
        #response = raw_input("Do you want to delete this song? (y/n): ")
        response = 'y'
        if(response!="n"):
                delete_songs.append(song["id"])
try:
    google_music.delete_songs(delete_songs)
except Exception as e:
    print e

print "Completed"
