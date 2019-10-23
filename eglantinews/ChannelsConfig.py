import json
import os
import sys


class ChannelsConfig:
    DEFAULT_CONFIG_FILE = "/config/channels.json"

    json_config: dict = None

    def __init__(self):

        if len(sys.argv) <= 1:
            config_file = self.__get_default_config_file()
        else:
            config_file = sys.argv[1]

        with open(config_file) as json_file:
            self.json_config = json.load(json_file)

    def get_channels(self) -> dict:
        return self.json_config

    def __get_default_config_file(self) -> str:
        return os.path.dirname(os.path.realpath(sys.argv[0])) + self.DEFAULT_CONFIG_FILE
