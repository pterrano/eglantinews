import logging

from eglantinews.EglantineConstants import QueryType
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.sentences.SentenceAnalyser import SentenceAnalyser
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineRoomService import EglantineRoomService


class EglantineMusicService(EglantineRoomService):
    _service_name = "Musiccast"

    _sentence_analyser = SentenceAnalyser

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

    def __listen(self, context: ExecutionContext):

        room_slots = self._get_rooms_slots()

        slots = context.get_slots()

        self._sentence_analyser.analyse_and_create_slots(slots, room_slots)

        query_type = slots.get_id('query-type')

        if query_type == QueryType.LISTEN_ARTIST:
            return self.__listen_artist(context)
        elif query_type == QueryType.LISTEN_ALBUM:
            return self.__listen_album(context)
        elif query_type == QueryType.LISTEN_TRACK:
            return self.__listen_track(context)
        elif query_type == QueryType.LISTEN_RADIO:
            return self.__listen_radio(context)

    def __listen_radio(self, context: ExecutionContext):

        room = self._get_room(context)

        radio = context.get_slot_id('radio')

        logging.info('LISTEN RADIO %s in %s' % (radio, room))

        self._process_rooms(context)

        result_search = self._remote(room).play_radio(radio)

        if result_search is not None:
            return Sentences.RADIO_FOUND % (result_search, self.__get_music_location(context))
        else:
            return Sentences.RADIO_NOT_FOUND % (radio, self.__get_music_location(context))

    def __listen_artist(self, context: ExecutionContext):

        room = self._get_room(context)

        query = Sentences.normalize_search(context.get_slot_value('query'))

        logging.info('LISTEN ARTIST %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'artists', 'deezer')

        if result_search is not None:
            return Sentences.ARTIST_FOUND % (result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.ARTIST_NOT_FOUND % query

    def __listen_track(self, context: ExecutionContext):

        room = self._get_room(context)

        query = Sentences.normalize_search(context.get_slot_value('query'))

        logging.info('LISTEN TRACK %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'tracks', 'deezer')

        if result_search is not None:
            return Sentences.TRACK_FOUND % (
                result_search['track'], result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.TRACK_NOT_FOUND % query

    def __listen_album(self, context: ExecutionContext):

        room = self._get_room(context)

        query = Sentences.normalize_search(context.get_slot_value('query'))

        logging.info('LISTEN ALBUM %s in %s' % (query, room))

        self._process_rooms(context)

        result_search = self._remote(room).search_play(query, 'albums', 'deezer')

        if result_search is not None:
            return Sentences.ALBUM_FOUND % (
                result_search['album'], result_search['artist'], self.__get_music_location(context))
        else:
            return Sentences.ALBUM_NOT_FOUND % query

    def __enable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, True)

        return Sentences.ENABLE_MULTIROOM

    def __disable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, False)

        return Sentences.DISABLE_MULTIROOM

    def get_intent_configs(self):

        all_rooms = self._get_room_slots()

        expected_volume = {'volume': None}
        expected_query = {'query': None}
        expected_room = {'room': all_rooms}

        return {
            'ChangeVolume': {
                'function': self._change_volume,
                'expected-slots': expected_volume
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
            'Pause': {
                'function': self.__pause
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
            'Listen': {
                'function': self.__listen,
                'expected-slots': expected_query
            }

        }
