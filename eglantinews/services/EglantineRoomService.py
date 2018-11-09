import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from alexa.Slot import Slot
from eglantinews.YamahaRemoteFactory import YamahaRemoteFactory
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
        return self.__yamaha_remote_factory.getRooms()

    def _get_default_room(self):
        return self.__yamaha_remote_factory.getDefaultRoom()

    def _get_room(self, context: ExecutionContext):
        return context.get_slot_id('room', self._get_current_room(context))

    def _get_current_room_name(self, context: ExecutionContext) -> str:
        return self.__yamaha_remote_factory.getRoomName(self._get_current_room(context))

    def _get_room_name(self, room: str) -> str:
        return self.__yamaha_remote_factory.getRoomName(room)

    def _get_room_slot(self, room: str) -> Slot:
        return Slot(room, self._get_room_name(room))

    def _get_room_slots(self) -> Slot():
        room_slots: Slot() = []
        for room in self._get_rooms():
            room_slots.append(self._get_room_slot(room))

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

    def _remote_by_room(self, room: str):
        return self.__yamaha_remote_factory.remote(room)

    def _default_remote(self):
        return self._remote_by_room(self._get_default_room())

    def _current_remote(self, context: ExecutionContext):
        return self._remote_by_room(self._get_current_room(context))

    def _change_volume(self, context: ExecutionContext):

        volume = context.get_slot_value('volume')

        if volume == '?':
            return EglantineServiceResult(None)

        volume = int(volume)

        if volume < 0 or volume > 100:
            return 'Le volume maximum est de 100'

        multiroom = self._is_multiroom(context) and context.get_slot_id('room') is None

        room = self._get_room(context)

        if multiroom:
            for room in self.__yamaha_remote_factory.getRooms():
                remote = self._remote_by_room(room)
                remote.turn_on()
                logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
                remote.set_volume(volume)

            return 'Modification du volume à %s' % volume
        else:
            remote = self._remote_by_room(room)
            remote.turn_on()
            logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
            remote.set_volume(volume)

            return 'Modification du volume à %s dans %s' % (volume, self._get_room_name(room))

    def _turn_off_all(self, context: ExecutionContext):

        for room in self._get_rooms():
            self._remote_by_room(room).turn_off()

        self._set_current_default_room(context)

        return 'Arrêt de toutes les enceintes'

    def get_intent_configs(self):
        pass
