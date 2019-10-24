import datetime
import logging
import os

import requests

from eglantinews.EglantineConfig import EglantineConfig
from eglantinews.epg.XmlTvReader import XmlTvReader
from eglantinews.epg.XmlTvProgram import XmlTvProgram
from utils.PathUtils import get_path

PATTERN_DATE_EPG_FILE = '%Y-%m-%d'
PATTERN_EPG_FILE = "tvguide-tnt_%s.xml"
EPG_DIRECTORY = "config/epg"


class XmlTvService:

    def __init__(self):
        self.epg_directory = get_path(EPG_DIRECTORY)
        self.epg_url = EglantineConfig().get_epg_config()['url']

        if not os.path.exists(self.epg_directory):
            os.mkdir(self.epg_directory)

        self.__download_epg_if_needed()

    def __get_epg_filename(self):
        return PATTERN_EPG_FILE % datetime.datetime.today().strftime(PATTERN_DATE_EPG_FILE)

    def __get_epg_file(self):
        return os.path.join(self.epg_directory, self.__get_epg_filename())

    def __download_epg_if_needed(self):

        epg_file = self.__get_epg_file()

        if not os.path.exists(epg_file):
            request = requests.get(self.epg_url)

            logging.info("downloading epg...")

            with open(epg_file, 'wb') as file:
                file.write(request.content)

            logging.info("epg has been written to %s (%s bytes)" % (epg_file, os.path.getsize(epg_file)))

        self.epg_reader = XmlTvReader(epg_file)
        logging.info("epg reloaded.")

    def get_programs_by_channel(self, channel_number: str):
        self.__download_epg_if_needed()
        return self.epg_reader.epg_reader.get_programs_by_channel(channel_number)

    def get_current_programs_by_channels(self) -> dict:
        self.__download_epg_if_needed()
        return self.epg_reader.get_current_programs_by_channels()

    def get_current_programs_by_channel(self, channel_number: str) -> XmlTvProgram:
        self.__download_epg_if_needed()
        return self.epg_reader.get_current_program_by_channel(channel_number)

    def get_first_part_programs_by_channels(self) -> dict:
        self.__download_epg_if_needed()
        return self.epg_reader.get_first_part_programs_by_channels()

    def get_first_part_programs_by_channel(self, channel_number: str) -> XmlTvProgram:
        self.__download_epg_if_needed()
        return self.epg_reader.get_first_part_program_by_channel(channel_number)

    def get_second_part_programs_by_channels(self) -> dict:
        self.__download_epg_if_needed()
        return self.epg_reader.get_second_part_programs_by_channels()

    def get_second_part_programs_by_channel(self, channel_number: str) -> XmlTvProgram:
        self.__download_epg_if_needed()
        return self.epg_reader.get_second_part_program_by_channel(channel_number)
