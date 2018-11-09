from eglantinews.Session import Session
from eglantinews.Slots import Slots
from eglantinews.Slot import Slot


class ExecutionContext:

    __slots: Slots = None

    __intent : str = None

    __session : Session = None

    def addSlots(self, slots):
        if slots != None:
            self.__slots.update(slots)

    def __init__(self, intent: str, slots : Slots, session: Session):

        self.__intent = intent

        self.__slots = slots

        self.__session = session

    def get_slot_id(self, slotName, defaultValue=None) -> str:

        slot: Slot = self.getSlot(slotName)

        if slot is None or slot.get_id() is None:
            return defaultValue

        return slot.get_id()

    def getSlotValue(self, slotName, defaultValue=None) -> str:

        slot : Slot =self.getSlot(slotName)

        if slot is None or slot.get_value() is None:
            return defaultValue

        return slot.get_value()

    def getSlot(self, slotName) -> Slot:
        return self.__slots.get(slotName)

    def getSlots(self) -> Slots:
        return self.__slots

    def getIntent(self) -> str:
        return self.__intent

    def getSession(self) -> Session:
        return self.__session
