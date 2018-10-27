import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.YamahaRemoteFactory import YamahaRemoteFactory
from eglantinews.services.EglantineService import EglantineService


class EglantineRoomService(EglantineService):

    __yamahaRemoteFactory = YamahaRemoteFactory()

    def _isCurrentMultiroom(self, context: ExecutionContext):
        return context.getSession().getAttribute('musiccast.multiroom', False)

    def _setCurrentMultiroom(self, context: ExecutionContext, currentMultiroom):
        context.getSession().setAttribute('multicast.multiroom', currentMultiroom)

    def _getCurrentRoom(self, context: ExecutionContext):
        return context.getSession().getAttribute('musiccast.multiroom', self._getDefaultRoom())

    def _setCurrentRoom(self, context: ExecutionContext, currentRoom: str):
        return context.getSession().setAttribute('musiccast.multiroom', currentRoom)

    def _setCurrentDefaultRoom(self, context):
        self._setCurrentRoom(context, self._getDefaultRoom())

    def _getRooms(self):
        return self.__yamahaRemoteFactory.getRooms()

    def _getDefaultRoom(self):
        return self.__yamahaRemoteFactory.getDefaultRoom()

    def _getRoom(self, context: ExecutionContext):
        return context.getSlot('room', self._getCurrentRoom(context))

    def _getCurrentRoomName(self, context: ExecutionContext) -> str:
        return self.__yamahaRemoteFactory.getRoomName(self._getCurrentRoom(context))

    def _getRoomName(self, room:str) -> str:
        return self.__yamahaRemoteFactory.getRoomName(room)

    def _isMultiroom(self, context: ExecutionContext):
        return context.getSlot('multiroom', False) or (
                self._isCurrentMultiroom(context) and context.getSlot('room') == None)

    def _setMultiRoomStatus(self, context:ExecutionContext, multiroom:bool):

        if multiroom:
            serverRoom = self._getRoom(context)
            self.__yamahaRemoteFactory.enableMultiroom(serverRoom);
        else:
            self.__yamahaRemoteFactory.disableMultiroom()

        self._setCurrentMultiroom(context, multiroom)


    def _processRooms(self, context: ExecutionContext):

        room = self._getRoom(context)

        multiRoom = self._isMultiroom(context)

        self._setCurrentMultiroom(context, multiRoom)

        if multiRoom:
            self.__yamahaRemoteFactory.enableMultiroom(room)
        else:
            self.__yamahaRemoteFactory.disableMultiroom()

        self._setCurrentRoom(context, room)

    def _remoteByRoom(self, room):
        return self.__yamahaRemoteFactory.remote(room)

    def _defaultRemote(self):
        return self._remoteByRoom(self._getDefaultRoom())

    def _currentRemote(self):
        return self._remoteByRoom(self._getCurrentRoom())

    def _changeVolume(self, context: ExecutionContext):

        volume = context.getSlot('volume')

        if volume == '?':
            return EglantineServiceResult(None)

        volume = int(volume)

        if volume < 0 or volume > 100:
            return 'Le volume maximum est de 100'

        multiroom = self._isMultiroom(context) and context.getSlot('room') == None

        room = self._getRoom(context)

        if multiroom:
            for room in self.__yamahaRemoteFactory.getRooms():
                remote = self._remoteByRoom(room);
                remote.turnOn()
                logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
                remote.setVolume(volume)

            return 'Modification du volume à %s' % (volume)
        else:
            remote = self._remoteByRoom(room);
            remote.turnOn()
            logging.info('CHANGE VOLUME TO %s (%s)' % (volume, room))
            remote.setVolume(volume)

            return 'Modification du volume à %s dans %s' % (volume, self._getRoomName(room))
