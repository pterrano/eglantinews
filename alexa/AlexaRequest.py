from alexa.Slots import Slots


class AlexaRequest:

    __user_id : str = None

    __device_id : str  = None

    __request_type: str = None

    __intent: str = None

    __slots: Slots = None

    def set_request_type(self, request_type: str):
        self.__request_type = request_type

    def set_intent(self, intent: str):
        self.__intent = intent

    def set_user_id(self, user_id: str):
        self.__user_id = user_id

    def set_device_id(self, device_id: str):
        self.__device_id = device_id

    def set_slots(self, slots: Slots):
        self.__slots = slots

    def get_request_type(self) -> str:
        return self.__request_type

    def get_intent(self) -> str:
        return self.__intent

    def get_user_id(self) -> str:
        return self.__user_id

    def get_device_id(self) -> str:
        return self.__device_id

    def get_slots(self) -> Slots:
        return self.__slots
