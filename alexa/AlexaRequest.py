from alexa.Slots import Slots


class AlexaRequest:
    __request_type: str

    __intent: str

    __slots: Slots

    def set_request_type(self, request_type: str):
        self.__request_type = request_type

    def set_intent(self, intent: str):
        self.__intent = intent

    def set_slots(self, slots: Slots):
        self.__slots = slots

    def get_request_type(self) -> str:
        return self.__request_type

    def get_intent(self) -> str:
        return self.__intent

    def get_slots(self) -> Slots:
        return self.__slots
