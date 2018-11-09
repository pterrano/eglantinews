import json
import logging
import traceback
from copy import copy

from flask import Flask, request
from flask_restful import Resource, Api

from alexa.AlexaRequest import AlexaRequest
from alexa.AlexaRequestParser import AlexaRequestParser
from alexa.AlexaResponse import AlexaResponse
from eglantinews.EglantineSentences import EglantineSentences
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
LAUNCH_INTENT = 'LaunchRequest'

AVAILABLE_SERVICES: EglantineService = [
    EglantineTVService(),
    EglantineMusicService(),
    EglantineMockService()
]


class EglantineWebService(Resource):
    __single_session = Session()

    __alexaRequestParser = AlexaRequestParser()

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

    def __get_session(self, alexa_request: AlexaRequest):
        return self.__single_session

    def get(self):
        return {'hello': 'world'}

    def post(self):

        json_data = json.loads(request.data)

        logging.info('POST')
        logging.info(json_data)

        try:

            alexa_request = self.__alexaRequestParser.parse(json_data)

            return self.process_request(alexa_request).to_json()

        except Exception:

            traceback.print_exc()

            alexa_response = AlexaResponse()
            alexa_response.set_sentence(EglantineSentences.ERROR_PROMPT)
            alexa_response.set_end_session(True)

            return alexa_response.to_json()

    """
    Traitement de la requête Alexa
    """

    def process_request(self, alexa_request) -> AlexaResponse:

        alexa_response = AlexaResponse()

        alexa_intent = alexa_request.get_intent()

        # S'il n'y a pas de phrase fournie par Alexa, c'est une erreur
        if alexa_intent is None:
            alexa_response.set_sentence(EglantineSentences.ERROR_PROMPT)
            alexa_response.set_end_session(True)

        # S'il s'agit d'une requete de lancement de la skill
        elif alexa_intent == LAUNCH_INTENT:
            alexa_response.set_sentence(EglantineSentences.LAUNCH_PROMPT)
            alexa_response.set_end_session(False)

        # Sinon on traite la requete demandée
        else:

            thread_service = self.__get_current_service(alexa_request)

            # S'il y a un service précédemment non terminé et que l'on dit "OK"
            if thread_service is not None and alexa_intent == OK_INTENT:

                # On attend l'attend à nouveau
                self.__wait_result(alexa_request, thread_service)

            # S'il y a Thread précédemment non terminé, qu'il tourne toujours et que l'on dit autre chose que "OK"
            elif thread_service is not None and thread_service.isAlive():

                # On demande d'attendre
                alexa_response.set_sentence(EglantineSentences.BUSY_PROMPT)
                alexa_response.set_end_session(True)

            # S'il n'y a pas ou plus de Thread en cours, on execute la requete
            else:

                execution_context = ExecutionContext( \
                    alexa_intent, \
                    alexa_request.get_slots(), \
                    self.__get_session(alexa_request) \
                    )

                has_candidate = self.executeCandidateService(alexa_request, alexa_response, execution_context)

                if not has_candidate:
                    alexa_response.set_sentence(EglantineSentences.UNKNOWN_PROMPT)
                    alexa_response.set_end_session(False)

        return alexa_response

    """
    Execute un service candidat
    @Return True si un candidat est trouvé, sinon False
    """

    def executeCandidateService(self, alexa_request, alexa_response, execution_context) -> bool:

        for service in self.get_session_services(alexa_request):

            if service.canManageIntent(execution_context):
                thread_service = EglantineThreadService(service)

                self.__set_current_service(alexa_request, thread_service)

                thread_service.launch(execution_context)

                self.__wait_result(alexa_request, alexa_response, thread_service)

                return True

        return False

    """
    Attente du résultat du service dans un Thread séparée jusqu'à un timeout
    """

    def __wait_result(self, alexa_request: AlexaRequest, alexa_response: AlexaResponse, thread_service):

        result = thread_service.wait_result(DEFAULT_SERVICE_TIMEOUT)

        # S'il y a un résultat, le service s'est terminé
        if result is not None:

            # Il n'y a plus de servoce en cours
            self.__set_current_service(alexa_request, None)

            # Le service qui vient de s'execute remonte au dessus de la pile
            self.__place_service_as_first(alexa_request, thread_service.get_service())

            alexa_response.set_sentence(result.get_sentence())
            alexa_response.set_prompt(result.get_prompt())
            alexa_response.set_end_session(result.is_should_end_session())

        # Sinon le service est toujours en attente
        else:
            alexa_response.set_sentence(EglantineSentences.TOO_LONG)
            alexa_response.set_end_session(False)

    """
    Met en session le service en cours d'execution
    """

    def __set_current_service(self, alexa_request, thread_service: EglantineThreadService):
        self.__get_session(alexa_request).set_attribute('common.current-service', thread_service)

    """
    Récupération en session du service en cours d'execution
    """

    def __get_current_service(self, alexa_request: AlexaRequest) -> EglantineThreadService:
        return self.__get_session(alexa_request).get_attribute('common.current-service')

    """
    Récupération/Stockage de la liste des services en session
    Cette liste donne la liste des services ordonnées par dernière execution
    """

    def get_session_services(self, alexa_request: AlexaRequest):

        session = self.__get_session(alexa_request)

        last_services = session.get_attribute(LAST_SERVICES_SESSION)
        if last_services is None:
            last_services = copy(AVAILABLE_SERVICES)
            session.set_attribute(LAST_SERVICES_SESSION, last_services)

        return last_services

    """
    On place le service sur le haut de la pile dans la liste des services en service
    """

    def __place_service_as_first(self, alexa_request, service: EglantineService):
        services = self.get_session_services(alexa_request)
        services.remove(service)
        services.insert(0, service)

    def __correct_prepositions(self, sentence: str):
        return sentence \
            .replace(' de le ', ' du ') \
            .replace(' de les ', ' des ') \
            .replace(' à le ', ' au  ') \
            .replace(' à les ', ' aux ')
