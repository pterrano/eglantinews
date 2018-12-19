class Slot:
    __identifier = None

    __value = None

    def __init__(self, identifier=None, value=None):

        self.__identifier = identifier

        self.__value = value


    def get_id(self):
        return self.__identifier

    def get_value(self):
        return self.__value

    def to_json(self):
        return {'id': self.__identifier, 'value': self.__value}
