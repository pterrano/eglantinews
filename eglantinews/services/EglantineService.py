import logging
import time

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext


class EglantineService:

    _serviceName = None

    # Public

    def canManageIntent(self, context: ExecutionContext) -> bool:

        intentConfig = self._getIntentConfig(context)

        if intentConfig == None:
            return False

        return self._checkConfig(context)

    def processIntent(self, context: ExecutionContext) -> EglantineServiceResult:

        intentConfig = self._getIntentConfig(context)

        if 'complete-slots' in intentConfig:
            context.addSlots(intentConfig['complete-slots'])

        function = self._getIntentFunction(context)

        logging.info('PROCESS-INTENT - BEGIN - slots = %s' % str(context.getSlots()))

        t0 = time.perf_counter()

        resultFunction = function(context)

        if isinstance(resultFunction, str):
            resultFunction = EglantineServiceResult(resultFunction)

        logging.info('PROCESS-INTENT - END - %.1f - slots = %s' % ((time.perf_counter() - t0), str(context.getSlots())))

        logging.info('PROCESS-INTENT - RESULT="%s"' % resultFunction.getSentence())

        return resultFunction

    # Protected

    def getIntentConfigs(self):
        raise NotImplementedError

    def _getIntentConfig(self, context: ExecutionContext):

        intentConfigs = self.getIntentConfigs()

        intent = context.getIntent()

        if intent in intentConfigs:
            return intentConfigs[intent]
        return None

    def _getIntentFunction(self, context: ExecutionContext):

        intentConfig = self._getIntentConfig(context)

        return intentConfig['function']

    def _checkConfig(self, context: ExecutionContext) -> bool:

        intentConfig = self._getIntentConfig(context)

        if 'expected-slots' in intentConfig:

            expectedSlots = intentConfig['expected-slots']

            for expectedSlotName in expectedSlots:

                slotValue = context.getSlot(expectedSlotName)

                if slotValue == None:
                    return False

                expectedValues = expectedSlots[expectedSlotName]

                if expectedValues != None and slotValue not in expectedValues:
                    return False

        return True

    def getName(self):
        return self._serviceName
