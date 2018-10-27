import logging
import time

from musiccast.YamahaRemote import YamahaRemote


class YamahaRemoteFactory:
    LINK_GROUP_ID = "d9ded9c3eea94ba8b137a805dc6d8942"

    LINK_GROUP = 'EglantineGroup'

    DEFAUT_ROOM = 'LIVING'

    __remoteByRooms = {
        'LIVING': YamahaRemote('amplifier', "le salon", 60, 120),
        'DESKTOP': YamahaRemote('wx051', "le bureau", 50)
    }

    def getDefaultRoom(self):
        return self.DEFAUT_ROOM

    def getRooms(self):
        return self.__remoteByRooms.keys()

    def getRoomName(self, room: str):

        remote = self.remote(room)

        if remote == None:
            return None

        return remote.getRemoteName()

    def remote(self, room):

        if room not in self.__remoteByRooms:
            logging.info("Can't find remote control for room %s" % room)
            return None

        return self.__remoteByRooms[room]

    def disableMultiroom(self):
        hasUnlink = False
        for remote in self.__remoteByRooms.values():
            hasUnlink = remote.unlink() != None or hasUnlink

        if hasUnlink:
            time.sleep(2)

    def enableMultiroom(self, serverRoom):

        for remote in self.__remoteByRooms.values():
            remote.turnOn()

        serverRemote = self.__remoteByRooms[serverRoom]

        clientRemotes = list(map(lambda room: self.__remoteByRooms[room],
                                 filter(lambda room: room != serverRoom, self.__remoteByRooms.keys())))

        clientHostnames = list(map(lambda clientRemote: clientRemote.getHostName(), clientRemotes))

        # Si le serveur multiroom a déja ce role, on ne fait rien
        if serverRemote.getLinkRole() == 'server':
            return

        # Sinon on désactive le multiroom actuelle
        self.disableMultiroom()

        # Et on créé à nouveau le réseau multiroom

        serverRemote.linkServer(self.LINK_GROUP_ID, clientHostnames)

        for clientRemote in clientRemotes:
            clientRemote.linkClient(self.LINK_GROUP_ID, serverRemote.getHostName())

        serverRemote.startDistribution()
        serverRemote.createGroup(self.LINK_GROUP)
