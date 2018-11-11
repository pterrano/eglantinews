import logging
import time

from alexa.Slot import Slot
from eglantinews.EglantineConfig import EglantineConfig
from musiccast.YamahaRemote import YamahaRemote


class YamahaRemoteFactory:
    __config = EglantineConfig()

    __remote_by_rooms = {}

    __default_room: str = None

    """ Initialisation des télécommandes à partir de la config """

    def __init__(self):

        room_configs = self.__config.get_rooms_config()

        for room_id in room_configs:

            room_config = room_configs[room_id]

            room_host_name = room_config["hostname"]
            room_label = room_config["label"]

            if "default-volume" in room_config:
                room_default_volume = room_config["default-volume"]
            else:
                room_default_volume = None

            if "max-volume" in room_config:
                room_max_volume = room_config["max-volume"]
            else:
                room_max_volume = None

            if "default" in room_config and room_config["default"]:
                self.__default_room = room_id

            self.__remote_by_rooms[room_id] = YamahaRemote(room_host_name, room_label, room_default_volume,
                                                           room_max_volume)

    """ ID de la pièce par défault """

    def get_default_room(self):
        return self.__default_room

    """ Donne la liste des ID de pièces """

    def get_room_ids(self):
        return self.__remote_by_rooms.keys()

    """ Nom d'une pièce """

    def get_room_name(self, room: str):

        remote = self.remote(room)

        if remote is None:
            return None

        return remote.get_remote_name()

    """ Donne la liste des slots de toutes les pièces """

    def get_room_slots(self) -> list:

        room_slots = []

        for room_id in self.__remote_by_rooms.keys():
            room_slots.append(Slot(room_id, self.__remote_by_rooms[room_id].get_remote_name()))

        return room_slots

    """ Télécommande d'une pièce """

    def remote(self, room: str):

        if room not in self.__remote_by_rooms:
            logging.info("Can't find remote control for room %s" % room)
            return None

        return self.__remote_by_rooms[room]

    """ Désactivation du multiroom """

    def disable_multiroom(self):
        has_unlink = False
        for remote in self.__remote_by_rooms.values():
            has_unlink = remote.unlink() is not None or has_unlink

        if has_unlink:
            time.sleep(2)

    """
    Activation du multiroom
    """

    def enable_multiroom(self, server_room):

        for remote in self.__remote_by_rooms.values():
            remote.turn_on()

        server_remote = self.__remote_by_rooms[server_room]

        client_remotes = list(map(lambda room: self.__remote_by_rooms[room],
                                  filter(lambda room: room != server_room, self.__remote_by_rooms.keys())))

        client_hostnames = list(map(lambda client_remote: client_remote.get_host_name(), client_remotes))

        # Si le serveur multiroom a déja ce role, on ne fait rien
        if server_remote.get_link_role() == 'server':
            return

        # Sinon on désactive le multiroom actuelle
        self.disable_multiroom()

        # Et on créé à nouveau le réseau multiroom
        link_group_id = self.__config.get_multiroom_link_group_id()
        link_group = self.__config.get_multiroom_link_group_name()

        server_remote.link_server(link_group_id, client_hostnames)

        for clientRemote in client_remotes:
            clientRemote.link_client(link_group_id, server_remote.get_host_name())

        server_remote.start_distribution()
        server_remote.create_group(link_group)
