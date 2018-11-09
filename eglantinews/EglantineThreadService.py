from threading import Thread

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineService import EglantineService

ERROR_PROMPT = "Une erreur s'est produite dans le service %s"


class EglantineThreadService(Thread):
    __result: EglantineServiceResult = None

    __context: ExecutionContext = None

    __service: EglantineService = None

    def __init__(self, service: EglantineService):
        super(EglantineThreadService, self).__init__()
        self.__service = service

    def run(self) -> None:
        try:
            self.__result = self.__service.processIntent(self.__context)
        except Exception as e:
            self.__result = EglantineServiceResult(ERROR_PROMPT % self.__service.getName())
            raise e

    def launch(self, context: ExecutionContext):
        self.__context = context
        self.start()

    def wait_result(self, timeout: int) -> EglantineServiceResult:
        if self.__result is None:
            self.join(timeout)

        return self.__result

    def get_service(self):
        return self.__service
