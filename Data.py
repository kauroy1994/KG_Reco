from random import random,choice
from copy import deepcopy

class Reco_data(object):

    def __init__(self):
        """constructor initializes placeholder
           for 1. context based reco data
           and 2. collaborative reco data
        """

        self.context_data = None
        self.collab_data = None
        self.collab_bk = ['listens(+person,+song)',
                   'listened(-person,+song)']
        self.collab_target = 'listens'
        self.context_bk = ['pop(+artist,#value)',
                           'sungby(+song,+artist)',
                           'listens(+person,+song)']
        #'by(+album,+artist)','in(+song,+album)',
        self.context_target = 'listens'

    def get_artist_and_album(self,artist_albums,album_songs,song):
        """gets artist and album pertaining
           to song
        """

        for artist in artist_albums:
            for album in artist_albums[artist]:
                if song in album_songs[album]:
                    return (artist,album)
        return False

    def get_data(self):
        """creates synthetic recommendation data
        """

        facts,pos,neg = [],[],[]
        n_artists = 5
        artists = [('ar'+str(i)) for i in range(n_artists)]
        artist_albums = {}
        albums = []
        for artist in artists:
            artist_albums[artist] = [(artist+'al'+str(i)) for i in range(5)]
            albums += artist_albums[artist]
        album_songs = {}
        songs = []
        for album in albums:
            album_songs[album] = [(album+'s'+str(i)) for i in range(10)]
            songs += album_songs[album]
        popular = [int(random() > 0.5) for i in range(n_artists)]
        p_types = [('fan'+str(i)) for i in range(n_artists)]
        p_types += ['art_pop','song_pop']
        n_persons = 10
        persons = [('p'+str(i)) for i in range(n_persons)]
        person_types = [choice(p_types) for i in range(n_persons)]
        print ("Person type: ",person_types[0])
        #print (person_types)
        #print (popular)
        n_songs = len(songs)
        for artist in artist_albums:
            if popular[artists.index(artist)]:
                if 'pop('+artist+','+(str(bool(popular[artists.index(artist)]))).lower()+').' not in facts:
                    facts.append('pop('+artist+','+(str(bool(popular[artists.index(artist)]))).lower()+').')
            for album in artist_albums[artist]:
                if 'by('+album+','+artist+').' not in facts:
                    facts.append('by('+album+','+artist+').')
                for song in album_songs[album]:
                    if 'sungby('+song+','+artist+').' not in facts:
                        facts.append('sungby('+song+','+artist+').')
                    if 'in('+song+','+album+').' not in facts:
                        facts.append('in('+song+','+album+').')

        for i in range(n_persons):
            person = persons[i]
            person_type = person_types[i]
            for j in range(n_songs):
                song = songs[j]
                artist_and_album = self.get_artist_and_album(artist_albums,album_songs,song)
                artist = artist_and_album[0]
                album = artist_and_album[1]
                if person_type == 'fan'+artist.split('r')[1]:
                    r = random()
                    if r < 0.8:
                        pos.append('listens('+person+','+song+').')
                    else:
                        neg.append('listens('+person+','+song+').')
                elif person_type == 'art_pop':
                    r = random()
                    if r < 0.8:
                        if popular[artists.index(artist)]:
                            pos.append('listens('+person+','+song+').')
                    else:
                        neg.append('listens('+person+','+song+').')
            self.context_data = (facts,pos,neg)
            
        listened_copy = deepcopy(pos+neg)
        facts,pos,neg = [],[],[]
        for ex in listened_copy:
            if 'listened('+ex.split('(')[1] not in facts:
                facts.append('listened('+ex.split('(')[1])
        for i in range(n_persons):
            person = persons[i]
            person_type = person_types[i]
            for j in range(n_songs):
                song = songs[j]
                if person_type == 'song_pop':
                    r = random()
                    if r < 0.8:
                        """
                        u_persons = list(set([item.split('(')[1].split(',')[0] for item in listened_copy if item.split('(')[1].split(',')[0] != person]))
                        persons_who_listen_to_song = [item.split('(')[1].split(',')[0] for item in listened_copy if (item.split('(')[1].split(',')[0] != person and item.split('(')[1].split(',')[1][:-2] == song)]
                        u_persons_who_listen_to_song = list(set(persons_who_listen_to_song))
                        """
                        
                        for item in listened_copy:
                            if item.split('(')[1].split(',')[0] == person:
                                continue
                            else:
                                if item.split('(')[1].split(',')[1][:-2] == song:
                                    pos.append('listens('+person+','+song+').')
                                    break
                    else:
                        neg.append('listens('+person+','+song+').')

        self.collab_data = (facts,pos,neg)

            
#====================TEST CASE================================
"""
def main():
    #main method creates recommendation data object
    #and populates context based and collaborative data
    
    data = Reco_data()
    data.get_data()

if __name__ == '__main__':
    main()
                    
"""                
