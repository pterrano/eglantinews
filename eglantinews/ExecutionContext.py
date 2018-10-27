from eglantinews.Session import Session


class ExecutionContext:

    def addSlots(self, slots):
        if slots!=None:
            self.__slots.update(slots)

    def __init__(self, intent: str, slots, session: Session):

        self.__intent = intent

        self.__slots = {}

        self.addSlots(slots)

        self.__session = session

    def getSlot(self, slotName, defaultValue = None) -> str:
        if slotName in self.__slots:
            return self.__slots[slotName]

        return defaultValue

    def getSlots(self):
        return self.__slots

    def getIntent(self) -> str:
        return self.__intent

    def getSession(self) -> Session:
        return self.__session
