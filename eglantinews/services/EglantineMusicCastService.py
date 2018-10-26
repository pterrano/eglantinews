import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineRoomService import EglantineRoomService


class EglantineMusicService(EglantineRoomService):

    _serviceName = "Musiccast"

    NORMALISE_WORDS = [
        'de', 'des', 'le', 'la', 'les', 'du', 'au', 'aux', 'à'
    ]

    def normalizeSearch(self, searchPattern: str):
        searchPattern = ' ' + searchPattern + ' '
        for word in self.NORMALISE_WORDS:
            searchPattern = searchPattern.replace(' ' + word + ' ', ' ')
        return searchPattern.strip(' ')

    # Sub-sentence to specify where music will be played
    def __getMusicLocation(self, context: ExecutionContext):
        if self._isCurrentMultiroom(context):
            return "de partout"
        else:
            return "dans %s" % self._getCurrentRoom(context)

    def __turnOffAll(self, context: ExecutionContext):

        for room in self._getRoomNames():
            self._remoteByRoom(room).turnOff()

        self._setCurrentDefaultRoom(context)

        return 'Arrêt de toutes les enceintes'

    def __turnOff(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        logging.info('TURN ON (%s)' % room)

        remote.turnOff()

        self._setCurrentDefaultRoom(context)

        return 'Arrêt de %s' % room

    def __turnOn(self, context: ExecutionContext):

        room = self._getRoom(context)

        remote = self._remoteByRoom(room);

        logging.info('TURN ON (%s)' % room)

        remote.turnOn()

        self._setCurrentRoom(context, room)

        return 'Allumage du %s' % room

    def __next(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        remote.nextSong()

        self._setCurrentRoom(context, room)

        return EglantineServiceResult(None, False)

    def __previous(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        remote.previousSong()
        remote.previousSong()

        self._setCurrentRoom(context, room)

        return EglantineServiceResult(None, False)

    def __resume(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        remote.play()

        self._setCurrentRoom(context, room)

        return EglantineServiceResult('Reprise de la musique %s' % self.__getMusicLocation(context))

    def __stop(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        remote.stop()

        self._setCurrentRoom(context, room)

        return EglantineServiceResult('Arrêt de la musique %s' % self.__getMusicLocation(context))

    def __pause(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        remote.pause()

        self._setCurrentRoom(context, room)

        return EglantineServiceResult('Pause de la musique %s' % self.__getMusicLocation(context))

    def __listenArtist(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);
        artist = self.normalizeSearch(context.getSlot('artist'))

        logging.info('LISTEN ARTIST %s in %s' % (artist, room))

        self._processRooms(context)

        resultSearch = remote.searchPlay(artist, 'artists', 'deezer')

        if (resultSearch != None):
            return "Ok, je mets les titres de %s %s" % (resultSearch['artist'], self.__getMusicLocation(context))
        else:
            return "Je n'ai pas trouvé de titre pour %s" % artist

    def __listenTrack(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);
        track = self.normalizeSearch(context.getSlot('track'))

        logging.info('LISTEN TRACK %s in %s' % (track, room))

        self._processRooms(context)

        resultSearch = remote.searchPlay(track, 'tracks', 'deezer')

        if (resultSearch != None):
            return "Ecoutons %s de %s %s" % (
                resultSearch['track'], resultSearch['artist'], self.__getMusicLocation(context))
        else:
            return "Je n'ai pas trouvé le titre %s" % track

    def __listenAlbum(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);
        album = self.normalizeSearch(context.getSlot('album'))

        logging.info('LISTEN ALBUM %s in %s' % (album, room))

        self._processRooms(context)

        resultSearch = remote.searchPlay(album, 'albums', 'deezer')

        if (resultSearch != None):
            return "Ok, je mets l'album %s de %s %s" % (
                resultSearch['album'], resultSearch['artist'], self.__getMusicLocation(context))
        else:
            return "Je n'ai pas trouvé d'album %s" % album

    def __enableMultiroom(self, context: ExecutionContext):

        self._setMultiRoomStatus(context, True)

        return "Activation du multiroom"

    def __disableMultiroom(self, context: ExecutionContext):

        self._setMultiRoomStatus(context, False)

        return "Désactivation du multiroom"

    def getIntentConfigs(self):
        return {
            'ChangeVolume': {
                'function': self._changeVolume,
                'expected-slots': {
                    'volume': None
                }
            },
            'TurnOffAll': {
                'function': self.__turnOffAll,
            },
            'TurnOff': {
                'function': self.__turnOff,
                'expected-slots': {
                    'room': self._getRoomNames()
                }
            },
            'TurnOn': {
                'function': self.__turnOn,
                'expected-slots': {
                    'room': self._getRoomNames()
                }
            },
            'AMAZON.StopIntent': {
                'function': self.__stop
            },
            'Next': {
                'function': self.__next
            },
            'Previous': {
                'function': self.__previous
            },
            'Resume': {
                'function': self.__resume
            },
            'Pause': {
                'function': self.__pause
            },
            'EnableMultiroom': {
                'function': self.__enableMultiroom
            },
            'DisableMultiroom': {
                'function': self.__disableMultiroom
            },
            'ListenAlbum': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                }
            },
            'ListenAlbumAll': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                },
                'complete-slots': {
                    'room': 'le salon',
                    'multiroom': True
                }
            },
            'ListenAlbumDesktop': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                },
                'complete-slots': {
                    'room': 'le bureau',
                }
            },
            'ListenAlbumLiving': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                },
                'complete-slots': {
                    'room': 'le salon',
                }
            },
            'ListenArtist': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
            },
            'ListenArtistAll': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
                'complete-slots': {
                    'room': 'le salon',
                    'multiroom': True
                }
            },
            'ListenArtistDesktop': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
                'complete-slots': {
                    'room': 'le bureau'
                }
            },
            'ListenArtistLiving': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
                'complete-slots': {
                    'room': 'le salon'
                }
            },
            'ListenTrack': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
            },
            'ListenTrackAll': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
                'complete-slots': {
                    'room': 'le salon',
                    'multiroom': True
                }
            },
            'ListenTrackDesktop': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
                'complete-slots': {
                    'room': 'le bureau'
                }
            },
            'ListenTrackLiving': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
                'complete-slots': {
                    'room': 'le salon'
                }
            }

        }
