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

        return remote.get_remote_name()

    def remote(self, room: str):

        if room not in self.__remoteByRooms:
            logging.info("Can't find remote control for room %s" % room)
            return None

        return self.__remoteByRooms[room]

    def disable_multiroom(self):
        hasUnlink = False
        for remote in self.__remoteByRooms.values():
            hasUnlink = remote.unlink() != None or hasUnlink

        if hasUnlink:
            time.sleep(2)

    def enable_multiroom(self, serverRoom):

        for remote in self.__remoteByRooms.values():
            remote.turn_on()

        serverRemote = self.__remoteByRooms[serverRoom]

        clientRemotes = list(map(lambda room: self.__remoteByRooms[room],
                                 filter(lambda room: room != serverRoom, self.__remoteByRooms.keys())))

        clientHostnames = list(map(lambda clientRemote: clientRemote.get_host_name(), clientRemotes))

        # Si le serveur multiroom a déja ce role, on ne fait rien
        if serverRemote.get_link_role() == 'server':
            return

        # Sinon on désactive le multiroom actuelle
        self.disable_multiroom()

        # Et on créé à nouveau le réseau multiroom

        serverRemote.link_server(self.LINK_GROUP_ID, clientHostnames)

        for clientRemote in clientRemotes:
            clientRemote.link_client(self.LINK_GROUP_ID, serverRemote.get_host_name())

        serverRemote.start_distribution()
        serverRemote.create_group(self.LINK_GROUP)
