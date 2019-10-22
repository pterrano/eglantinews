import json
import logging
import traceback
from copy import copy

from flask import Flask, request
from flask_restful import Resource, Api

from alexa.AlexaRequest import AlexaRequest
from alexa.AlexaRequestParser import AlexaRequestParser
from alexa.AlexaResponse import AlexaResponse
from eglantinews.EglantineConfig import EglantineConfig
from eglantinews.EglantineConstants import EglantineConstants
from eglantinews.sentences.Sentences import Sentences
from eglantinews.EglantineThreadService import EglantineThreadService
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.Session import Session
from eglantinews.services.EglantineMockService import EglantineMockService
from eglantinews.services.EglantineMusicCastService import EglantineMusicService
from eglantinews.services.EglantineService import EglantineService
from eglantinews.services.EglantineTVService import EglantineTVService
from eglantinews.services.EglantineMovieService import EglantineMovieService


class EglantineWebService(Resource):
    __available_services: EglantineService = [
        EglantineTVService(),
        EglantineMusicService(),
        EglantineMovieService(),
        EglantineMockService()
    ]

    __sessions = {}

    __alexaRequestParser = AlexaRequestParser()

    __config = EglantineConfig()

    __app: Flask

    __api: Api

    def __init__(self):
        self.__name__ = 'eglantine-ws'
        self.__app = Flask(self.__name__)
        self.__api = Api(self.__app)
        self.__api.add_resource(self, '/ws-eglantine')

    def run(self):
        logging.info('Server started')
        self.__app.run(debug=False, host='0.0.0.0')

    def __get_session(self, alexa_request: AlexaRequest) -> Session:

        user_id = alexa_request.get_user_id()

        if user_id not in self.__sessions:
            self.__sessions[user_id] = Session()

        return self.__sessions[user_id]

    """
    Information sur le web service
    """
    def get(self):
        return self.__config.get_ws_infos()

    """
    Réception requete Alexa
    """
    def post(self):

        json_data = json.loads(request.data)

        logging.info('<JSON-REQUEST>')
        logging.info(json_data)
        logging.info('</JSON-REQUEST>')

        json_response = self.process_post(json_data)

        logging.info('<JSON-RESPONSE>')
        logging.info(json_response)
        logging.info('</JSON-RESPONSE>')

        return json_response

    """
    Traitement de la requête POST JSON en provance d'Alexa
    """

    def process_post(self, json_data):
        try:

            alexa_request = self.__alexaRequestParser.parse(json_data)

            if not self.__check_access(alexa_request):
                alexa_response = AlexaResponse()
                alexa_response.set_sentence(Sentences.FORBIDDEN)
                alexa_response.set_end_session(True)
                return alexa_response.to_json()

            return self.process_request(alexa_request).to_json()

        except Exception:

            traceback.print_exc()

            alexa_response = AlexaResponse()
            alexa_response.set_sentence(Sentences.ERROR)
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
            alexa_response.set_sentence(Sentences.ERROR)
            alexa_response.set_end_session(True)

        # S'il s'agit d'une requete de lancement de la skill
        elif alexa_intent == EglantineConstants.LAUNCH_INTENT:
            alexa_response.set_sentence(Sentences.LAUNCH_PROMPT)
            alexa_response.set_end_session(False)

        # Sinon on traite la requete demandée
        else:

            thread_service = self.__get_current_service(alexa_request)

            # S'il y a un service précédemment non terminé et que l'on dit "OK"
            if thread_service is not None and alexa_intent == EglantineConstants.OK_INTENT:

                # On attend le service à nouveau
                self.__wait_result(alexa_request, alexa_response, thread_service)

            # S'il y a Thread précédemment non terminé, qu'il tourne toujours et que l'on dit autre chose que "OK"
            elif thread_service is not None and thread_service.isAlive():

                # On demande d'attendre
                alexa_response.set_sentence(Sentences.BUSY)
                alexa_response.set_end_session(True)

            # S'il n'y a pas ou plus de Thread en cours, on execute la requete
            else:

                execution_context = ExecutionContext(alexa_intent, alexa_request.get_slots(),
                                                     self.__get_session(alexa_request))

                has_candidate = self.process_candidate_service(alexa_request, alexa_response, execution_context)

                if not has_candidate:
                    alexa_response.set_sentence(Sentences.UNKNOWN)
                    alexa_response.set_end_session(False)

        return alexa_response

    """
    Execute un service candidat
    @Return True si un candidat est trouvé, sinon False
    """

    def process_candidate_service(self, alexa_request: AlexaRequest, alexa_response: AlexaResponse,
                                  execution_context: ExecutionContext) -> bool:

        for service in self.get_session_services(alexa_request):

            if service.can_manage_intent(execution_context):
                thread_service = EglantineThreadService(service)

                self.__set_current_service(alexa_request, thread_service)

                thread_service.launch(execution_context)

                self.__wait_result(alexa_request, alexa_response, thread_service)

                return True

        return False

    """
    Attente du résultat du service dans un Thread séparé jusqu'à un timeout
    """

    def __wait_result(self, alexa_request: AlexaRequest, alexa_response: AlexaResponse,
                      thread_service: EglantineThreadService):

        result = thread_service.wait_result(EglantineConstants.DEFAULT_SERVICE_TIMEOUT)

        # S'il y a un résultat, le service s'est terminé
        if result is not None:

            # Il n'y a plus de servoce en cours
            self.__set_current_service(alexa_request, None)

            # Le service qui vient de s'execute remonte au dessus de la pile
            self.__place_service_as_first(alexa_request, thread_service.get_service())

            # On remplace les prépopositions par leurs contractions
            sentence = Sentences.correct_prepositions(result.get_sentence())

            alexa_response.set_sentence(sentence)
            alexa_response.set_prompt(result.get_prompt())
            alexa_response.set_end_session(result.is_should_end_session())

        # Sinon le service est toujours en attente
        else:
            alexa_response.set_sentence(Sentences.TOO_LONG)
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

        last_services = session.get_attribute(EglantineConstants.LAST_SERVICES_SESSION)
        if last_services is None:
            last_services = copy(self.__available_services)
            session.set_attribute(EglantineConstants.LAST_SERVICES_SESSION, last_services)

        return last_services

    """
    On place le service sur le haut de la pile dans la liste des services en service
    """

    def __place_service_as_first(self, alexa_request, service: EglantineService):
        services = self.get_session_services(alexa_request)
        services.remove(service)
        services.insert(0, service)

    """
    Vérification que l'utilisateur à accès à la skill
    """

    def __check_access(self, alexa_request: AlexaRequest) -> bool:

        if not self.__config.is_security_enabled():
            return True

        access_user = alexa_request.get_user_id() in self.__config.get_authorized_users()

        access_device = alexa_request.get_device_id() in self.__config.get_authorized_devices()

        return access_user and access_device
