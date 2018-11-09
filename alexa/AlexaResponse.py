import logging


class AlexaResponse:
    __end_session: bool = True

    __sentence: str = ''

    __prompt: str = None

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

        logging.info('<ALEXA-RESPONSE>')
        logging.info(alexa_response)
        logging.info('</ALEXA-RESPONSE>')

        return alexa_response
