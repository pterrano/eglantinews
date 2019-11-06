class AlexaResponse:

    def __init__(self, sentence: str = "", end_session: str = True, prompt: str = None):
        self.__sentence = sentence
        self.__end_session = end_session
        self.__prompt = prompt

    def set_sentence(self, sentence: str):
        self.__sentence = sentence

    def set_prompt(self, prompt: str):
        self.__prompt = prompt

    def set_end_session(self, end_session: bool):
        self.__end_session = end_session

    def to_json(self) -> dict:
        alexa_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "shouldEndSession": self.__end_session,
                "outputSpeech": {
                    "type": "PlainText",
                    "text": self.__sentence
                }
            }
        }

        if self.__prompt is not None:
            alexa_response['response']['reprompt'] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": self.__prompt
                }

            }

        return alexa_response
