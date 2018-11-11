from copy import deepcopy

from alexa.Slot import Slot


class Slots:
    __slots: dict

    def __init__(self, slots={}):
        self.__slots = deepcopy(slots)

    def merge(self, slots):
        for slot_name in slots.__slots:
            self.add(slot_name, slots.__slots[slot_name])

    def add(self, slot_name: str, slot: Slot, overwrite: bool = False):
        if overwrite or self.get(slot_name) is None:
            self.__slots[slot_name] = slot

    def get(self, slot_name: str) -> Slot:
        if slot_name in self.__slots:
            return self.__slots[slot_name]

    def get_value(self, slot_name: str) -> str:
        if slot_name in self.__slots:
            return self.get(slot_name).get_value()
        return None

    def get_id(self, slot_name: str) -> str:
        if slot_name in self.__slots:
            return self.get(slot_name).get_value()
        return None

    def to_json(self):

        json = {}

        for slot_name in self.__slots:
            json[slot_name] = self.__slots[slot_name].to_json()

        return json
