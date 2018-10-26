from threading import Thread
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineService import EglantineService
import traceback

ERROR_PROMPT = "Une erreur s'est produite dans le service %s"

class EglantineThreadService(Thread):

    __result: EglantineServiceResult = None

    def __init__(self, service: EglantineService):
        super(EglantineThreadService, self).__init__()
        self.__service = service

    def run(self) -> None:
        try:
            self.__result = self.__service.processIntent(self.__context)
        except Exception:
            self.__result = EglantineServiceResult(ERROR_PROMPT % self.__service.getName())
            traceback.print_exc()

    def launch(self, context: ExecutionContext):
        self.__context = context
        self.start()

    def waitResult(self, timeout: int) -> EglantineServiceResult:
        if self.__result == None:
            self.join(timeout)

        return self.__result

    def getService(self):
        return self.__service
