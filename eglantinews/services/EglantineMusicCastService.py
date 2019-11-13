import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineRoomService import EglantineRoomService
from utils.SearchUtils import simplify_accronym


class EglantineMusicService(EglantineRoomService):
    _service_name = "Musiccast"

    # Sub-sentence to specify where music will be played
    def __get_music_location(self, context: ExecutionContext):
        if self._is_current_multiroom(context):
            return Sentences.MUSIC_LOCATION_MULTIROOM
        else:
            return Sentences.MUSIC_LOCATION % self._get_current_room_name(context)

    def __turn_off(self, context: ExecutionContext):

        room = self._get_room(context)

        logging.info('TURN ON (%s)' % room)

        self._remote(room).turn_off()

        self._set_current_default_room(context)

        return Sentences.TURN_OFF % self._get_room_name(room)

    def __turn_on(self, context: ExecutionContext):

        room = self._get_room(context)

        logging.info('TURN ON (%s)' % self._get_room_name(room))

        self._remote(room).turn_on()

        self._set_current_room(context, room)

        return Sentences.TURN_ON % self._get_room_name(room)

    def __next(self, context: ExecutionContext):

        room = self._get_room(context)

        self._remote(room).next_song()

        self._set_current_room(context, room)

        return EglantineServiceResult(None, False)

    def __previous(self, context: ExecutionContext):

        room = self._get_room(context)

        remote = self._remote(room)
        remote.previous_song()
        remote.previous_song()

        self._set_current_room(context, room)

        return EglantineServiceResult(None, False)

    def __resume(self, context: ExecutionContext):

        room = self._get_room(context)

        self._remote(room).play()

        self._set_current_room(context, room)

        return EglantineServiceResult(Sentences.RESUME_MUSIC % self.__get_music_location(context))

    def __stop(self, context: ExecutionContext):

        room = self._get_room(context)

        self._remote(room).stop()

        self._set_current_room(context, room)

        return EglantineServiceResult(Sentences.STOP_MUSIC % self.__get_music_location(context))

    def __pause(self, context: ExecutionContext):

        room = self._get_room(context)

        self._remote(room).pause()

        self._set_current_room(context, room)

        return EglantineServiceResult(Sentences.PAUSE_MUSIC % self.__get_music_location(context))

    def __current_title(self, context: ExecutionContext):

        play_info = self._current_remote(context).get_play_info(True)

        if play_info['track'] == '':
            return Sentences.NO_CURRENT_TRACK
        elif play_info['album'] == '':
            return Sentences.CURRENT_TRACK % (play_info['track'], play_info['artist'])
        else:
            return Sentences.CURRENT_TRACK_WITH_ALBUM % (
                play_info['track'], play_info['artist'], play_info['album'])

    def __current_volume(self, context: ExecutionContext):

        if not self._is_current_multiroom(context):
            room = self._get_room(context)
            volume = self._remote(room).get_volume()
            return Sentences.CURRENT_VOLUME % (volume, self._get_room_name(room))

        else:
            result = ''
            for room in self._get_rooms():
                volume = self._remote(room).get_volume()
                result = result + Sentences.CURRENT_VOLUME_WITH_LOCATION % (volume, self._get_room_name(room))
            return result

    def __listen_radio(self, context: ExecutionContext):

        room = self._get_room(context)

        query = simplify_accronym(context.get_slot_value('queryRadio'))

        logging.info('LISTEN RADIO %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).play_radio(query)

        if result_search is not None:
            return Sentences.RADIO_FOUND % (result_search, self.__get_music_location(context))
        else:
            return Sentences.RADIO_NOT_FOUND % (query, self.__get_music_location(context))

    def __listen_artist(self, context: ExecutionContext):

        room = self._get_room(context)

        query = context.get_slot_value('queryArtist')

        logging.info('LISTEN ARTIST %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'artists', 'deezer')

        if result_search is not None:
            return Sentences.ARTIST_FOUND % (result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.ARTIST_NOT_FOUND % query

    def __listen_track(self, context: ExecutionContext):

        room = self._get_room(context)

        query_track = context.get_slot_value('queryTrack')

        query_artist = context.get_slot_value('queryArtist')

        if query_artist is None:
            query = query_track
        else:
            query = query_track + " " + query_artist

        logging.info('LISTEN TRACK %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'tracks', 'deezer')

        if result_search is not None:
            return Sentences.TRACK_FOUND % (
                result_search['track'], result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.TRACK_NOT_FOUND % query_track

    def __listen_album(self, context: ExecutionContext):

        room = self._get_room(context)

        query_album = context.get_slot_value('queryAlbum')

        query_artist = context.get_slot_value('queryArtist')

        if query_artist is None:
            query = query_album
        else:
            query = query_album + " " + query_artist

        logging.info('LISTEN ALBUM %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'albums', 'deezer')

        if result_search is not None:
            return Sentences.ALBUM_FOUND % (
                result_search['album'], result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.ALBUM_NOT_FOUND % query_album

    def __enable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, True)

        return Sentences.ENABLE_MULTIROOM

    def __disable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, False)

        return Sentences.DISABLE_MULTIROOM

    def get_intent_configs(self):

        all_rooms = self._get_rooms_slots()

        expected_volume = {'volume': None}
        expected_room = {'room': all_rooms}

        return {
            'ChangeVolume': {
                'function': self._change_volume,
                'expected-slots': expected_volume
            },
            'IncreaseVolume': {
                'function': self._increase_volume,
            },
            'DecreaseVolume': {
                'function': self._decrease_volume,
            },
            'TurnOff': {
                'function': self.__turn_off,
                'expected-slots': expected_room
            },
            'TurnOn': {
                'function': self.__turn_on,
                'expected-slots': expected_room
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
            'ResumeRoom': {
                'function': self.__resume,
                'expected-slots': expected_room
            },
            'Pause': {
                'function': self.__pause
            },
            'PauseRoom': {
                'function': self.__pause,
                'expected-slots': expected_room
            },
            'EnableMultiroom': {
                'function': self.__enable_multiroom
            },
            'DisableMultiroom': {
                'function': self.__disable_multiroom
            },
            'CurrentTitle': {
                'function': self.__current_title
            },
            'CurrentVolume': {
                'function': self.__current_volume
            },
            'ListenArtist': {
                'function': self.__listen_artist,
                'expected-slots': {'queryArtist': None}
            },
            'ListenAlbum': {
                'function': self.__listen_album,
                'expected-slots': {'queryAlbum': None}
            },
            'ListenTrack': {
                'function': self.__listen_track,
                'expected-slots': {'queryTrack': None}
            },
            'ListenRadio': {
                'function': self.__listen_radio,
                'expected-slots': {'queryRadio': None}
            }

        }
