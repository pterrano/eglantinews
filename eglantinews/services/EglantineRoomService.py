import logging

from alexa.Slot import Slot
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.YamahaRemoteFactory import YamahaRemoteFactory
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineService import EglantineService


class EglantineRoomService(EglantineService):
    __yamaha_remote_factory = YamahaRemoteFactory()

    def _is_current_multiroom(self, context: ExecutionContext):
        return context.get_session().get_attribute('musiccast.multiroom', False)

    def _set_current_multiroom(self, context: ExecutionContext, current_multi_room: bool):
        context.get_session().set_attribute('musiccast.multiroom', current_multi_room)

    def _get_current_room(self, context: ExecutionContext):
        return context.get_session().get_attribute('musiccast.room', self._get_default_room())

    def _set_current_room(self, context: ExecutionContext, current_room: str):
        return context.get_session().set_attribute('musiccast.room', current_room)

    def _set_current_default_room(self, context: ExecutionContext):
        self._set_current_room(context, self._get_default_room())

    def _get_rooms(self):
        return self.__yamaha_remote_factory.get_room_ids()

    def _get_rooms_slots(self) -> list:
        return self.__yamaha_remote_factory.get_room_slots()

    def _get_default_room(self):
        return self.__yamaha_remote_factory.get_default_room()

    def _get_room(self, context: ExecutionContext):
        return context.get_slot_id('room', self._get_current_room(context))

    def _get_current_room_name(self, context: ExecutionContext) -> str:
        return self.__yamaha_remote_factory.get_room_name(self._get_current_room(context))

    def _get_room_name(self, room: str) -> str:
        return self.__yamaha_remote_factory.get_room_name(room)

    def _get_room_slot(self, room: str) -> Slot:
        return Slot(room, self._get_room_name(room))

    def _is_multiroom(self, context: ExecutionContext):
        return context.get_slot_id('multiroom', False) or (
                self._is_current_multiroom(context) and context.get_slot_id('room') is None)

    def _set_multi_room_status(self, context: ExecutionContext, multiroom: bool):

        if multiroom:
            server_room = self._get_room(context)
            self.__yamaha_remote_factory.enable_multiroom(server_room)
        else:
            self.__yamaha_remote_factory.disable_multiroom()

        self._set_current_multiroom(context, multiroom)

    def _process_rooms(self, context: ExecutionContext):

        room = self._get_room(context)

        multi_room = self._is_multiroom(context)

        self._set_current_multiroom(context, multi_room)

        if multi_room:
            self.__yamaha_remote_factory.enable_multiroom(room)
        else:
            self.__yamaha_remote_factory.disable_multiroom()

        self._set_current_room(context, room)

    def _remote(self, room: str):
        return self.__yamaha_remote_factory.remote(room)

    def _default_remote(self):
        return self._remote(self._get_default_room())

    def _current_remote(self, context: ExecutionContext):
        return self._remote(self._get_current_room(context))

    def _increase_volume(self, context: ExecutionContext):

        multiroom = self._is_multiroom(context) and context.get_slot_id('room') is None

        room = self._get_room(context)

        if multiroom:
            for room in self.__yamaha_remote_factory.get_room_ids():
                remote = self._remote(room)
                remote.turn_on()
                logging.info('INCREASE VOLUME (%s)' % (room))
                remote.increase_volume()

        else:
            remote = self._remote(room)
            remote.turn_on()
            logging.info('INCREASE VOLUME (%s)' % (room))
            remote.increase_volume()

        return None;

    def _decrease_volume(self, context: ExecutionContext):

        multiroom = self._is_multiroom(context) and context.get_slot_id('room') is None

        room = self._get_room(context)

        if multiroom:
            for room in self.__yamaha_remote_factory.get_room_ids():
                remote = self._remote(room)
                remote.turn_on()
                logging.info('DECREASE VOLUME (%s)' % (room))
                remote.decrease_volume()

        else:
            remote = self._remote(room)
            remote.turn_on()
            logging.info('DECREASE VOLUME (%s)' % (room))
            remote.decrease_volume()

        return None;

    def _change_volume(self, context: ExecutionContext):

        volume = context.get_slot_value('volume')

        if volume == '?':
            return EglantineServiceResult(None)

        volume = int(volume)

        if volume not in range(0, 101):
            return Sentences.VOLUME_RANGE

        multiroom = self._is_multiroom(context) and context.get_slot_id('room') is None

        room = self._get_room(context)

        if multiroom:
            for room in self.__yamaha_remote_factory.get_room_ids():
                remote = self._remote(room)
                remote.turn_on()
                logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
                remote.set_volume(volume)

            return Sentences.VOLUME_MODIFICATION % volume
        else:
            remote = self._remote(room)
            remote.turn_on()
            logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
            remote.set_volume(volume)

            return Sentences.VOLUME_MODIFICATION_WITH_LOCATION % (volume, self._get_room_name(room))

    def _turn_off_all(self, context: ExecutionContext):

        for room in self._get_rooms():
            self._remote(room).turn_off()

        self._set_current_default_room(context)

    def get_intent_configs(self):
        pass
