class AlexaRequestParser:

    def __init__(self, slots={}):
        self.__slots = deepcopy(slots)
