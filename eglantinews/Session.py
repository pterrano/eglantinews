class Session:
    __attributes = {}

    def get_attribute(self, attribute_name: str, default_value=None):
        if attribute_name in self.__attributes:
            return self.__attributes[attribute_name]

        return default_value

    def set_attribute(self, attribute_name: str, attribute_value):
        self.__attributes[attribute_name] = attribute_value
