from typing import List

from alexa.Slot import Slot
from alexa.Slots import Slots
from eglantinews.EglantineConstants import QueryType


class SentenceAnalyser:

    @staticmethod
    def __processQueryType(slots: Slots, pattern: str, queryType: str):
        query = slots.get_value("query")
        if query.find(pattern) != -1:
            query = query.replace(pattern, "").strip()
            slots.add("query", Slot(None, query), True)
            slots.add("query-type", Slot(queryType), True)

    @staticmethod
    def __process_query_types(slots: Slots):
        slots.add("query-type", QueryType.LISTEN_TRACK)
        SentenceAnalyser.__processQueryType(slots, "le titre", QueryType.LISTEN_TRACK)
        SentenceAnalyser.__processQueryType(slots, "l'album", QueryType.LISTEN_ALBUM)
        SentenceAnalyser.__processQueryType(slots, "les titres de", QueryType.LISTEN_ARTIST)
        SentenceAnalyser.__processQueryType(slots, "l'artiste", QueryType.LISTEN_ARTIST)
        SentenceAnalyser.__processQueryType(slots, "la radio", QueryType.LISTEN_RADIO)

    @staticmethod
    def __process_multiroom(slots: Slots, pattern: str):
        query = slots.get_value("query")
        if query.find(pattern) != -1:
            query = query.replace(pattern, "").strip()
            slots.add("query", Slot(None, query), True)
            slots.add("multiroom", True)

    @staticmethod
    def __process_rooms(slots: Slots, room_slots: List[Slot]):
        for room_slot in room_slots:

            room_name = room_slot.get_value()

            query = slots.get_value("query")

            if query.find("dans " + room_name) != -1:
                query = query.replace("dans " + room_name, "").strip()
                slots.add("query", Slot(None, query), True)
                slots.add("room", room_slot)

    @staticmethod
    def analyse_and_create_slots(slots: Slots, room_slots: List[Slot]):
        SentenceAnalyser.__process_rooms(slots, room_slots)
        SentenceAnalyser.__process_query_types(slots)
        SentenceAnalyser.__process_multiroom(slots, 'en multiroom')
        SentenceAnalyser.__process_multiroom(slots, 'de partout')