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
            return "dans %s" % self._getCurrentRoomName(context)

    def __turnOff(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);

        logging.info('TURN ON (%s)' % room)

        remote.turnOff()

        self._setCurrentDefaultRoom(context)

        return 'Arrêt de %s' % self._getRoomName(room)

    def __turnOn(self, context: ExecutionContext):

        room = self._getRoom(context)

        remote = self._remoteByRoom(room);

        logging.info('TURN ON (%s)' % self._getRoomName(room))

        remote.turnOn()

        self._setCurrentRoom(context, room)

        return 'Allumage de %s' % self._getRoomName(room)

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

    def __currentTitle(self, context: ExecutionContext):

        playInfo = self._currentRemote(context).getPlayInfo(True)

        if playInfo['track'] == '':
            return 'Aucun titre en cours'
        elif playInfo['album'] == '':
            return "Nous écoutons actuellement le titre %s de %s" % (playInfo['track'], playInfo['artist'])
        else:
            return "Nous écoutons actuellement le titre %s de %s dans l'album %s" % (
                playInfo['track'], playInfo['artist'], playInfo['album'])

    def __currentVolume(self, context: ExecutionContext):

        if not self._isCurrentMultiroom(context):
            room = self._getRoom(context)
            volume = self._remoteByRoom(room).getVolume()
            return 'Le volume est à %i dans %s.' % (volume, self._getRoomName(room))

        else:
            result = ''
            for room in self._getRooms():
                volume = self._remoteByRoom(room).getVolume()
                result = result + 'Le volume est à %i dans %s. ' % (volume, self._getRoomName(room))
            return result

    def __listenRadio(self, context: ExecutionContext):

        room = self._getRoom(context)
        remote = self._remoteByRoom(room);
        radio = self.normalizeSearch(context.getSlot('radio'))

        logging.info('LISTEN RADIO %s in %s' % (radio, room))

        self._processRooms(context)

        resultSearch = remote.playRadio(radio)

        if (resultSearch != None):
            return "Ok, je mets %s %s" % (resultSearch, self.__getMusicLocation(context))
        else:
            return "Je n'ai pas trouvé la radio %s %s" % (radio, self.__getMusicLocation(context))

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
            'TurnOff': {
                'function': self.__turnOff,
                'expected-slots': {
                    'room': self._getRooms()
                }
            },
            'TurnOn': {
                'function': self.__turnOn,
                'expected-slots': {
                    'room': self._getRooms()
                }
            },
            'AMAZON.StopIntent': {
                'function': self.__stop
            },
            'Next': {
                'function': self.__next
            },
            'NextTitle': {
                'function': self.__next
            },
            'Previous': {
                'function': self.__previous
            },
            'PreviousTitle': {
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
            'CurrentTitle': {
                'function': self.__currentTitle
            },
            'CurrentVolume': {
                'function': self.__currentVolume
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
                    'room': 'LIVING',
                    'multiroom': True
                }
            },
            'ListenAlbumDesktop': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                },
                'complete-slots': {
                    'room': 'DESKTOP',
                }
            },
            'ListenAlbumLiving': {
                'function': self.__listenAlbum,
                'expected-slots': {
                    'album': None
                },
                'complete-slots': {
                    'room': 'LIVING',
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
                    'room': 'DESKTOP',
                    'multiroom': True
                }
            },
            'ListenArtistDesktop': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
                'complete-slots': {
                    'room': 'DESKTOP'
                }
            },
            'ListenArtistLiving': {
                'function': self.__listenArtist,
                'expected-slots': {
                    'artist': None
                },
                'complete-slots': {
                    'room': 'DESKTOP'
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
                    'room': 'LIVING',
                    'multiroom': True
                }
            },
            'ListenTrackDesktop': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
                'complete-slots': {
                    'room': 'DESKTOP'
                }
            },
            'ListenTrackLiving': {
                'function': self.__listenTrack,
                'expected-slots': {
                    'track': None
                },
                'complete-slots': {
                    'room': 'LIVING'
                }
            },
            'ListenRadio': {
                'function': self.__listenRadio,
                'expected-slots': {
                    'radio': None
                }
            },
            'ListenRadioAll': {
                'function': self.__listenRadio,
                'expected-slots': {
                    'radio': None
                },
                'complete-slots': {
                    'room': 'LIVING',
                    'multiroom': True
                }
            },
            'ListenRadioDesktop': {
                'function': self.__listenRadio,
                'expected-slots': {
                    'radio': None
                },
                'complete-slots': {
                    'room': 'DESKTOP'
                }
            },
            'ListenRadioLiving': {
                'function': self.__listenRadio,
                'expected-slots': {
                    'radio': None
                },
                'complete-slots': {
                    'room': 'LIVING'
                }
            },

        }
