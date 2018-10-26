class Session:

    __attributes = {}

    def getAttribute(self, attributeName:str, defaultValue = None):

        if attributeName in self.__attributes:
            return self.__attributes[attributeName]

        return defaultValue

    def setAttribute(self, attributeName:str, attributeValue):

        self.__attributes[attributeName]=attributeValue