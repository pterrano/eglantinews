import json

from utils.PathUtils import get_path

DEFAULT_CONFIG_FILE = "config/channels.json"


class ChannelsConfig:
    json_config: dict = None

    def __init__(self):
        config_file = get_path(DEFAULT_CONFIG_FILE)
        with open(config_file) as json_file:
            self.json_config = json.load(json_file)

    def get_channels(self) -> dict:
        return self.json_config
