from eglantinews.Session import Session
from alexa.Slot import Slot
from alexa.Slots import Slots


class ExecutionContext:

    __slots: Slots = None

    __intent: str = None

    __session: Session = None

    def add_slots(self, slots):
        if slots is not None:
            self.__slots.merge(slots)

    def __init__(self, intent: str, slots: Slots, session: Session):

        self.__intent = intent

        self.__slots = slots

        self.__session = session

    def get_slot_id(self, slot_name, default_value=None) -> str:

        slot: Slot = self.get_slot(slot_name)

        if slot is None or slot.get_id() is None:
            return default_value

        return slot.get_id()

    def get_slot_value(self, slot_name, default_value=None) -> str:

        slot: Slot = self.get_slot(slot_name)

        if slot is None or slot.get_value() is None:
            return default_value

        return slot.get_value()

    def get_slot(self, slot_name) -> Slot:
        return self.__slots.get(slot_name)

    def get_slots(self) -> Slots:
        return self.__slots

    def get_intent(self) -> str:
        return self.__intent

    def get_session(self) -> Session:
        return self.__session
