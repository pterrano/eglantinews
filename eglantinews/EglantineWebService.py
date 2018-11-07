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
    __singleSession = Session()

    def __init__(self):
        self.__name__ = 'eglantine-ws';
        self.app = Flask(self.__name__)
        self.api = Api(self.app)
        self.api.add_resource(self, '/ws-eglantine')

    def run(self):
        logging.info('Server started')
        self.app.run(debug=True, host='0.0.0.0')

    def placeServiceAsFirst(self, alexaRequest, service: EglantineService):
        services = self.getSessionServices(alexaRequest)
        services.remove(service)
        services.insert(0, service)

    def correctPrepositions(self, sentence: str):
        return sentence \
            .replace(' de le ', ' du ') \
            .replace(' de les ', ' des ') \
            .replace(' à le ', ' au  ') \
            .replace(' à les ', ' aux ')

    def getSessionServices(self, alexaRequest):
        session = self.getSession(alexaRequest)
        lastServices = session.getAttribute(LAST_SERVICES_SESSION)
        if lastServices == None:
            lastServices = copy(AVAILABLE_SERVICES)
            session.setAttribute(LAST_SERVICES_SESSION, lastServices)
        return lastServices

    def getSession(self, alexaRequest):
        return self.__singleSession

    def post(self):

        req = json.loads(request.data);

        logging.info('POST')
        logging.info(req)

        try:

            result = None

            if 'request' in req:

                alexaRequest = req['request']

                logging.info('<ALEXA-REQUEST>')
                logging.info(alexaRequest)
                logging.info('</ALEXA-REQUEST>')

                if 'type' in alexaRequest and alexaRequest['type'] == 'LaunchRequest':
                    result = EglantineServiceResult("Bonjour c'est Eglantine, que puis-je faire ?", False)
                elif 'intent' in alexaRequest:

                    alexaIntent = alexaRequest['intent']

                    if 'name' in alexaIntent:

                        intent = alexaIntent['name']

                        threadService = self.__getCurrentService(alexaRequest)

                        if threadService != None and intent == OK_INTENT:

                            result = self.__waitResult(alexaRequest, threadService)

                        elif threadService != None and threadService.isAlive():

                            result = EglantineServiceResult(BUSY_PROMPT, False)

                        else:

                            slots = self.__getSlots(alexaRequest);

                            executionContext = ExecutionContext(intent, slots, self.getSession(alexaRequest))

                            for service in self.getSessionServices(alexaRequest):

                                if service.canManageIntent(executionContext):
                                    threadService = EglantineThreadService(service)

                                    self.__setCurrentService(alexaRequest, threadService)

                                    threadService.launch(executionContext)

                                    result = self.__waitResult(alexaRequest, threadService)

                                    break

                if result == None:
                    result = EglantineServiceResult(UNKNOWN_PROMPT, False)



        except Exception:
            result = EglantineServiceResult(ERROR_PROMPT)
            traceback.print_exc()

        alexaResponse = deepcopy(RESPONSE_TEMPLATE)

        if result == None:
            result = EglantineServiceResult(ERROR_PROMPT)
        elif result.getSentence() is None:
            result.setSentence('')

        alexaResponse['response']['shouldEndSession'] = result.isShouldEndSession()

        alexaResponse['response']['outputSpeech'] = {
            "type": "PlainText",
            "text": self.correctPrepositions(result.getSentence())
        }

        if not result.getPrompt() is None:
            alexaResponse['response']['reprompt'] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": result.getPrompt()
                }

            }

        logging.info('<ALEXA-RESPONSE>')
        logging.info(alexaResponse)
        logging.info('</ALEXA-RESPONSE>')

        return alexaResponse

    def __waitResult(self, alexaRequest, threadService):

        result = threadService.waitResult(DEFAULT_SERVICE_TIMEOUT)

        # Le service s'est terminé
        if result != None:
            self.__setCurrentService(alexaRequest, None)
            self.placeServiceAsFirst(alexaRequest, threadService.getService())
        else:
            result = EglantineServiceResult(TOO_LONG, False)

        return result

    def __setCurrentService(self, alexaRequest, threadService: EglantineThreadService):
        self.getSession(alexaRequest).setAttribute('common.current-service', threadService)

    def __getCurrentService(self, alexaRequest) -> EglantineThreadService:
        return self.getSession(alexaRequest).getAttribute('common.current-service')

    def get(self):
        return {'hello': 'world'}

    def __getSlots(self, alexaRequest):

        if 'intent' not in alexaRequest:
            return None

        alexaIntent = alexaRequest['intent']

        if 'slots' not in alexaIntent:
            return None

        alexaSlots = alexaIntent['slots']

        slots = {}

        for slotName in alexaSlots:

            slot = alexaSlots[slotName]

            slotId=self.__getSlotId(slot)

            if 'value' in slot:
                slotValue = slot['value']
            else:
                slotValue = None

            slots[slotName] = { 'id' : slotId, 'value' : slotValue }

        return slots;

    def __getSlotId(self, slot) -> str:

        if 'resolutions' not in slot:
            return None

        resolutions = slot['resolutions']
        if 'resolutionsPerAuthority' not in resolutions:
            return None

        resolutionsPerAuthority = resolutions['resolutionsPerAuthority']

        if len(resolutionsPerAuthority) < 1:
            return None

        for resolutionPerAuthority in resolutionsPerAuthority:

            values = resolutionPerAuthority['values']

            if len(values) > 0:
                return values[0]['value']['id']

