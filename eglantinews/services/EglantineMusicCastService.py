import logging

from alexa.Slot import Slot
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineRoomService import EglantineRoomService


class EglantineMusicService(EglantineRoomService):
    _service_name = "Musiccast"

    NORMALISE_WORDS = [
        'de', 'des', 'le', 'la', 'les', 'du', 'au', 'aux', 'à'
    ]

    def normalize_search(self, search_pattern: str):
        search_pattern = ' ' + search_pattern + ' '
        for word in self.NORMALISE_WORDS:
            search_pattern = search_pattern.replace(' ' + word + ' ', ' ')
        return search_pattern.strip(' ')

    # Sub-sentence to specify where music will be played
    def __get_music_location(self, context: ExecutionContext):
        if self._is_current_multiroom(context):
            return "de partout"
        else:
            return "dans %s" % self._get_current_room_name(context)

    def __turn_off(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        logging.info('TURN ON (%s)' % room)

        remote.turn_off()

        self._set_current_default_room(context)

        return 'Arrêt de %s' % self._get_room_name(room)

    def __turn_on(self, context: ExecutionContext):

        room = self._get_room(context)

        remote = self._remote_by_room(room)

        logging.info('TURN ON (%s)' % self._get_room_name(room))

        remote.turn_on()

        self._set_current_room(context, room)

        return 'Allumage de %s' % self._get_room_name(room)

    def __next(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        remote.next_song()

        self._set_current_room(context, room)

        return EglantineServiceResult(None, False)

    def __previous(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        remote.previous_song()
        remote.previous_song()

        self._set_current_room(context, room)

        return EglantineServiceResult(None, False)

    def __resume(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        remote.play()

        self._set_current_room(context, room)

        return EglantineServiceResult('Reprise de la musique %s' % self.__get_music_location(context))

    def __stop(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        remote.stop()

        self._set_current_room(context, room)

        return EglantineServiceResult('Arrêt de la musique %s' % self.__get_music_location(context))

    def __pause(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)

        remote.pause()

        self._set_current_room(context, room)

        return EglantineServiceResult('Pause de la musique %s' % self.__get_music_location(context))

    def __current_title(self, context: ExecutionContext):

        play_info = self._current_remote(context).get_play_info(True)

        if play_info['track'] == '':
            return 'Aucun titre en cours'
        elif play_info['album'] == '':
            return "Nous écoutons actuellement le titre %s de %s" % (play_info['track'], play_info['artist'])
        else:
            return "Nous écoutons actuellement le titre %s de %s dans l'album %s" % (
                play_info['track'], play_info['artist'], play_info['album'])

    def __current_volume(self, context: ExecutionContext):

        if not self._is_current_multiroom(context):
            room = self._get_room(context)
            volume = self._remote_by_room(room).get_volume()
            return 'Le volume est à %i dans %s.' % (volume, self._get_room_name(room))

        else:
            result = ''
            for room in self._get_rooms():
                volume = self._remote_by_room(room).get_volume()
                result = result + 'Le volume est à %i dans %s. ' % (volume, self._get_room_name(room))
            return result

    def __listen_radio(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)
        radio = context.get_slot_id('radio')

        logging.info('LISTEN RADIO %s in %s' % (radio, room))

        self._process_rooms(context)

        result_search = remote.play_radio(radio)

        if result_search is not None:
            return "Ok, je mets %s %s" % (result_search, self.__get_music_location(context))
        else:
            return "Je n'ai pas trouvé la radio %s %s" % (radio, self.__get_music_location(context))

    def __listen_artist(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)
        artist = self.normalize_search(context.get_slot_value('artist'))

        logging.info('LISTEN ARTIST %s in %s' % (artist, room))

        self._process_rooms(context)

        result_search = remote.search_play(artist, 'artists', 'deezer')

        if result_search is not None:
            return "Ok, je mets les titres de %s %s" % (result_search['artist'], self.__get_music_location(context))
        else:
            return "Je n'ai pas trouvé de titre pour %s" % artist

    def __listen_track(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)
        track = self.normalize_search(context.get_slot_value('track'))

        logging.info('LISTEN TRACK %s in %s' % (track, room))

        self._process_rooms(context)

        result_search = remote.search_play(track, 'tracks', 'deezer')

        if result_search is not None:
            return "Ecoutons %s de %s %s" % (
                result_search['track'], result_search['artist'], self.__get_music_location(context))
        else:
            return "Je n'ai pas trouvé le titre %s" % track

    def __listen_album(self, context: ExecutionContext):

        room = self._get_room(context)
        remote = self._remote_by_room(room)
        album = self.normalize_search(context.get_slot_value('album'))

        logging.info('LISTEN ALBUM %s in %s' % (album, room))

        self._process_rooms(context)

        result_search = remote.search_play(album, 'albums', 'deezer')

        if result_search is not None:
            return "Ok, je mets l'album %s de %s %s" % (
                result_search['album'], result_search['artist'], self.__get_music_location(context))
        else:
            return "Je n'ai pas trouvé d'album %s" % album

    def __enable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, True)

        return "Activation du multiroom"

    def __disable_multiroom(self, context: ExecutionContext):

        self._set_multi_room_status(context, False)

        return "Désactivation du multiroom"

    def get_intent_configs(self):

        living_room = self._get_room_slot('LIVING')
        desktop_room = self._get_room_slot('DESKTOP')
        all_rooms = self._get_room_slots()

        complete_multiroom = {'room': living_room, 'multiroom': Slot(True)}
        complete_living = {'room': living_room}
        complete_desktop = {'room': desktop_room}

        expected_volume = {'volume': None}
        expected_album = {'album': None}
        expected_track = {'track': None}
        expected_radio = {'radio': None}
        expected_artist = {'artist': None}
        expected_all_rooms = {'room': all_rooms}

        return {
            'ChangeVolume': {
                'function': self._change_volume,
                'expected-slots': expected_volume
            },
            'TurnOff': {
                'function': self.__turn_off,
                'expected-slots': expected_all_rooms
            },
            'TurnOn': {
                'function': self.__turn_on,
                'expected-slots': expected_all_rooms
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
            'ListenAlbum': {
                'function': self.__listen_album,
                'expected-slots': expected_album
            },
            'ListenAlbumAll': {
                'function': self.__listen_album,
                'expected-slots': expected_album,
                'complete-slots': complete_multiroom
            },
            'ListenAlbumDesktop': {
                'function': self.__listen_album,
                'expected-slots': expected_album,
                'complete-slots': complete_desktop
            },
            'ListenAlbumLiving': {
                'function': self.__listen_album,
                'expected-slots': expected_album,
                'complete-slots': complete_living
            },
            'ListenArtist': {
                'function': self.__listen_artist,
                'expected-slots': expected_artist,
            },
            'ListenArtistAll': {
                'function': self.__listen_artist,
                'expected-slots': expected_artist,
                'complete-slots': complete_multiroom
            },
            'ListenArtistDesktop': {
                'function': self.__listen_artist,
                'expected-slots': expected_artist,
                'complete-slots': complete_desktop
            },
            'ListenArtistLiving': {
                'function': self.__listen_artist,
                'expected-slots': expected_artist,
                'complete-slots': complete_living
            },
            'ListenTrack': {
                'function': self.__listen_track,
                'expected-slots': expected_track,
            },
            'ListenTrackAll': {
                'function': self.__listen_track,
                'expected-slots': expected_track,
                'complete-slots': complete_multiroom
            },
            'ListenTrackDesktop': {
                'function': self.__listen_track,
                'expected-slots': expected_track,
                'complete-slots': complete_desktop
            },
            'ListenTrackLiving': {
                'function': self.__listen_track,
                'expected-slots': expected_track,
                'complete-slots': complete_living
            },
            'ListenRadio': {
                'function': self.__listen_radio,
                'expected-slots': expected_radio
            },
            'ListenRadioAll': {
                'function': self.__listen_radio,
                'expected-slots': expected_radio,
                'complete-slots': complete_multiroom
            },
            'ListenRadioDesktop': {
                'function': self.__listen_radio,
                'expected-slots': expected_radio,
                'complete-slots': complete_desktop
            },
            'ListenRadioLiving': {
                'function': self.__listen_radio,
                'expected-slots': expected_radio,
                'complete-slots': complete_living
            },

        }
