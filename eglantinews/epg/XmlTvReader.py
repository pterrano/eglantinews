import datetime
import xml.etree.ElementTree as ET

from eglantinews.ChannelsConfig import ChannelsConfig
from eglantinews.epg.XmlTvProgram import XmlTvProgram
from utils.SearchUtils import simplify_accronym


class XmlTvReader:

    def __init__(self, xml_file: str):

        self.channels_config = ChannelsConfig().get_channels()
        self.__parse_programs(xml_file)

    def __get_channels_by_ids(self, channels) -> dict:
        results = {}
        for channel in channels:
            if 'xmltv-id' not in channel:
                continue
            channel_number = channel['id']
            channel_name = channel['name']['synonyms'][0]
            channel_id = channel['xmltv-id']
            results[channel_id] = {'number': channel_number, 'name': channel_name}

        return results

    def __parse_programs(self, xml_file: str):

        self.__programs = {}

        channels = self.__get_channels_by_ids(self.channels_config)

        tree = ET.parse(xml_file)

        if tree is None:
            return

        root = tree.getroot()
        if root is None or root.tag != 'tv':
            return

        for child in root:

            program = self.__parse_program(child)
            if program is None:
                continue

            if program.channel_id in channels.keys():
                channel = channels[program.channel_id]

                if channel['number'] in self.__programs:
                    channel_programs = self.__programs[channel['number']]
                else:
                    channel_programs = []
                    self.__programs[channel['number']] = channel_programs

                program.channel_number = channel['number']
                program.channel_name = simplify_accronym(channel['name'])

                channel_programs.append(program)

    def __parse_program(self, node: dict) -> XmlTvProgram:

        if node.tag != 'programme':
            return None

        program = XmlTvProgram()

        program.channel_id = node.attrib['channel']
        program.start = self.__parse_date(node.attrib['start'])
        program.stop = self.__parse_date(node.attrib['stop'])

        for markup in node:
            if markup.tag == 'title':
                program.title = markup.text
            elif markup.tag == 'sub-title':
                program.sub_title = markup.text
            elif markup.tag == 'desc':
                program.description = markup.text

        return program

    def __parse_date(self, date_as_string: str):
        return datetime.datetime.strptime(date_as_string, '%Y%m%d%H%M%S %z').replace(tzinfo=None)

    def get_programs(self):
        return self.__programs

    def get_programs_by_channel(self, channel_number: str):
        if channel_number in self.__programs:
            return self.__programs[channel_number]
        else:
            return []

    def get_current_programs_by_channels(self) -> dict:
        result = {}
        for channel_id in self.__programs.keys():
            program = self.get_current_program_by_channel(channel_id)
            if program is not None:
                result[channel_id] = program

        return result

    def get_first_part_programs_by_channels(self) -> dict:
        result = {}
        for channel_id in self.__programs.keys():
            program = self.get_first_part_program_by_channel(channel_id)
            if program is not None:
                result[channel_id] = program
        return result

    def get_second_part_programs_by_channels(self) -> dict:
        result = {}
        for channel_id in self.__programs.keys():
            program = self.get_second_part_program_by_channel(channel_id)
            if program is not None:
                result[channel_id] = program
        return result

    def get_current_program_by_channel(self, channel_number: str) -> XmlTvProgram:

        programs = self.get_programs_by_channel(channel_number)

        now = datetime.datetime.now()

        for program in programs:
            if program.is_playing(now):
                return program

        return None

    def get_first_part_program_by_channel(self, channel_number: str):

        programs = self.get_programs_by_channel(channel_number)

        for program in programs:
            if program.is_first_part():
                return program

        return None

    def get_second_part_program_by_channel(self, channel_number: str):

        programs = self.get_programs_by_channel(channel_number)

        for program in programs:
            if program.is_second_part():
                return program

        return None
