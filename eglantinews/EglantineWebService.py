import json
import logging
import traceback
from copy import copy
from copy import deepcopy

from flask import Flask, request
from flask_restful import Resource, Api

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.EglantineThreadService import EglantineThreadService
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.Session import Session
from eglantinews.Slot import Slot
from eglantinews.Slots import Slots
from eglantinews.services.EglantineMockService import EglantineMockService
from eglantinews.services.EglantineMusicCastService import EglantineMusicService
from eglantinews.services.EglantineService import EglantineService
from eglantinews.services.EglantineTVService import EglantineTVService

LAST_SERVICES_SESSION = 'common.last-services'
DEFAULT_SERVICE_TIMEOUT: int = 6

OK_INTENT = 'OK'

DEFAULT_PROMPT = 'Que puis je faire ?'
TOO_LONG = 'Je cherche toujours. Dîtes OK pour avoir ma réponse'
UNKNOWN_PROMPT = 'Je ne comprends pas'
ERROR_PROMPT = "Une erreur s'est produite"
BUSY_PROMPT = "Je suis déjà occupé. Peux-tu attendre un instant, s'il te plaît ?"

RESPONSE_TEMPLATE = {
    "version": "1.0",
    "sessionAttributes": {},
    "response": {
        "shouldEndSession": False
    }
}

AVAILABLE_SERVICES: EglantineService = [
    EglantineTVService(),
    EglantineMusicService(),
    EglantineMockService()
]


class EglantineWebService(Resource):
    __single_session = Session()

    __app: Flask

    __api: Api

    def __init__(self):
        self.__name__ = 'eglantine-ws'
        self.__app = Flask(self.__name__)
        self.__api = Api(self.__app)
        self.__api.add_resource(self, '/ws-eglantine')

    def run(self):
        logging.info('Server started')
        self.__app.run(debug=True, host='0.0.0.0')

    def place_service_as_first(self, alexa_request, service: EglantineService):
        services = self.get_session_services(alexa_request)
        services.remove(service)
        services.insert(0, service)

    def correct_prepositions(self, sentence: str):
        return sentence \
            .replace(' de le ', ' du ') \
            .replace(' de les ', ' des ') \
            .replace(' à le ', ' au  ') \
            .replace(' à les ', ' aux ')

    def get_session_services(self, alexa_request):
        session = self.get_session(alexa_request)
        last_services = session.get_attribute(LAST_SERVICES_SESSION)
        if last_services is None:
            last_services = copy(AVAILABLE_SERVICES)
            session.set_attribute(LAST_SERVICES_SESSION, last_services)
        return last_services

    def get_session(self, alexa_request):
        return self.__single_session

    def post(self):

        req = json.loads(request.data)

        logging.info('POST')
        logging.info(req)

        try:

            result = None

            if 'request' in req:

                alexa_request = req['request']

                logging.info('<ALEXA-REQUEST>')
                logging.info(alexa_request)
                logging.info('</ALEXA-REQUEST>')

                if 'type' in alexa_request and alexa_request['type'] == 'LaunchRequest':
                    result = EglantineServiceResult("Bonjour c'est Eglantine, que puis-je faire ?", False)
                elif 'intent' in alexa_request:

                    alexa_intent = alexa_request['intent']

                    if 'name' in alexa_intent:

                        intent = alexa_intent['name']

                        thread_service = self.__get_current_service(alexa_request)

                        if thread_service is not None and intent == OK_INTENT:

                            result = self.__wait_result(alexa_request, thread_service)

                        elif thread_service is not None and thread_service.isAlive():

                            result = EglantineServiceResult(BUSY_PROMPT, False)

                        else:

                            slots = self.__get_slots(alexa_request)

                            execution_context = ExecutionContext(intent, slots, self.get_session(alexa_request))

                            for service in self.get_session_services(alexa_request):

                                if service.canManageIntent(execution_context):
                                    thread_service = EglantineThreadService(service)

                                    self.__set_current_service(alexa_request, thread_service)

                                    thread_service.launch(execution_context)

                                    result = self.__wait_result(alexa_request, thread_service)

                                    break

                if result is None:
                    result = EglantineServiceResult(UNKNOWN_PROMPT, False)

        except Exception:
            result = EglantineServiceResult(ERROR_PROMPT)
            traceback.print_exc()

        alexa_response: dict = deepcopy(RESPONSE_TEMPLATE)

        if result is None:
            result = EglantineServiceResult(ERROR_PROMPT)
        elif result.get_sentence() is None:
            result.set_sentence('')

        alexa_response['response']['shouldEndSession'] = result.is_should_end_session()

        alexa_response['response']['outputSpeech'] = {
            "type": "PlainText",
            "text": self.correct_prepositions(result.get_sentence())
        }

        if not result.get_prompt() is None:
            alexa_response['response']['reprompt'] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": result.get_prompt()
                }

            }

        logging.info('<ALEXA-RESPONSE>')
        logging.info(alexa_response)
        logging.info('</ALEXA-RESPONSE>')

        return alexa_response

    def __wait_result(self, alexa_request, thread_service):

        result = thread_service.wait_result(DEFAULT_SERVICE_TIMEOUT)

        # Le service s'est terminé
        if result is not None:
            self.__set_current_service(alexa_request, None)
            self.place_service_as_first(alexa_request, thread_service.get_service())
        else:
            result = EglantineServiceResult(TOO_LONG, False)

        return result

    def __set_current_service(self, alexa_request, thread_service: EglantineThreadService):
        self.get_session(alexa_request).set_attribute('common.current-service', thread_service)

    def __get_current_service(self, alexa_request) -> EglantineThreadService:
        return self.get_session(alexa_request).get_attribute('common.current-service')

    def get(self):
        return {'hello': 'world'}

    def __get_slots(self, alexa_request) -> Slots:

        if 'intent' not in alexa_request:
            return None

        alexa_intent = alexa_request['intent']

        if 'slots' not in alexa_intent:
            return None

        alexa_slots = alexa_intent['slots']

        slots = Slots()

        for slot_name in alexa_slots:

            slot = alexa_slots[slot_name]

            slot_id = self.__get_slot_id(slot)

            if 'value' in slot:
                slot_value = slot['value']
            else:
                slot_value = None

            slots.add(slot_name, Slot(slot_id, slot_value))

        return slots

    def __get_slot_id(self, slot) -> str:

        if 'resolutions' not in slot:
            return None

        resolutions = slot['resolutions']
        if 'resolutionsPerAuthority' not in resolutions:
            return None

        resolutions_per_authority = resolutions['resolutionsPerAuthority']

        if len(resolutions_per_authority) < 1:
            return None

        for resolution_per_authority in resolutions_per_authority:

            values = resolution_per_authority['values']

            if len(values) > 0:
                return values[0]['value']['id']
