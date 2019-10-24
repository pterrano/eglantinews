import datetime

from utils.JsonUtils import json_serialize

MARGIN_PERIOD = 300
MIN_PART_DURATION = 1800
START_FIRST_PERIOD = datetime.time(20, 45, 00)
START_SECOND_PERIOD = datetime.time(22, 00, 00)
END_SECOND_PERIOD = datetime.time(23, 59, 59)


class XmlTvProgram:

    def __init__(self):
        self.channel_number = None
        self.channel_name = None
        self.channel_id = None
        self.start = None
        self.stop = None
        self.title = None
        self.sub_title = None
        self.description = None

    def __str__(self):
        return json_serialize(self)

    def __get_start_period(self):
        return datetime.datetime.combine(datetime.date.today(), START_FIRST_PERIOD)

    def __get_second_period(self):
        return datetime.datetime.combine(datetime.date.today(), START_SECOND_PERIOD)

    def __get_end_period(self):
        return datetime.datetime.combine(datetime.date.today(), END_SECOND_PERIOD)

    def is_playing(self, now: datetime):
        return self.start <= now + datetime.timedelta(seconds=MARGIN_PERIOD) <= self.stop

    def is_first_part(self):
        return self.start > self.__get_start_period() and self.start < self.__get_end_period() and self.get_duration() > MIN_PART_DURATION and not self.is_second_part()

    def is_second_part(self):
        return self.start > self.__get_second_period() and self.start < self.__get_end_period() and self.get_duration() > MIN_PART_DURATION

    def get_duration(self):
        return (self.stop - self.start).seconds
