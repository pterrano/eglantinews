import json
import os
import sys


class EglantineConfig:
    DEFAULT_CONFIG_FILE = "/config/eglantine-skill.json"

    json_config: dict = None

    def __init__(self):

        if len(sys.argv) <= 1:
            config_file = self.__get_default_config_file()
        else:
            config_file = sys.argv[1]

        with open(config_file) as json_file:
            self.json_config = json.load(json_file)

    def get_authorized_users(self) -> dict:
        return self.json_config['security']['authorized-users']

    def get_authorized_devices(self):
        return self.json_config['security']['authorized-devices']

    def is_security_enabled(self) -> bool:
        return self.json_config['security']['enabled']

    def get_ws_infos(self):
        return self.json_config['infos']

    def get_rooms_config(self) -> dict:
        return self.json_config['services']['musiccast']['devices']

    def get_multiroom_link_group_id(self) -> dict:
        return self.json_config['services']['musiccast']['multiroom']['group-id']

    def get_multiroom_link_group_name(self) -> dict:
        return self.json_config['services']['musiccast']['multiroom']['group-name']

    def get_samsung_tv_config(self) -> dict:
        return self.json_config['services']['samsung-tv']

    def __get_default_config_file(self) -> str:
        return os.path.dirname(os.path.realpath(sys.argv[0])) + self.DEFAULT_CONFIG_FILE
