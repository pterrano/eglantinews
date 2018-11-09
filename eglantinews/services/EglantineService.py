import logging
import time

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from alexa.Slot import Slot


class EglantineService:

    _service_name = None

    # Public

    def canManageIntent(self, context: ExecutionContext) -> bool:

        intentConfig = self._getIntentConfig(context)

        if intentConfig == None:
            return False

        return self._checkConfig(context)

    def processIntent(self, context: ExecutionContext) -> EglantineServiceResult:

        intentConfig = self._getIntentConfig(context)

        if 'complete-slots' in intentConfig:
            context.add_slots(intentConfig['complete-slots'])

        function = self._getIntentFunction(context)

        logging.info('PROCESS-INTENT - BEGIN - slots = %s' % str(context.get_slots().to_json()))

        t0 = time.perf_counter()

        resultFunction = function(context)

        if isinstance(resultFunction, str):
            resultFunction = EglantineServiceResult(resultFunction)

        logging.info('PROCESS-INTENT - END - %.1f - slots = %s' % ((time.perf_counter() - t0), str(context.get_slots().to_json())))

        logging.info('PROCESS-INTENT - RESULT="%s"' % resultFunction.get_sentence())

        return resultFunction

    # Protected

    def get_intent_configs(self):
        raise NotImplementedError

    def _getIntentConfig(self, context: ExecutionContext):

        intentConfigs = self.get_intent_configs()

        intent = context.get_intent()

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

                inputSlot : Slot = context.get_slot(expectedSlotName)
                if inputSlot == None:
                    return False

                expectedSlot = expectedSlots[expectedSlotName]
                if expectedSlot == None:
                    return True

                if isinstance(expectedSlot, list):
                    if self.__hasExpectedSlot(inputSlot, expectedSlot):
                        return False
                elif not self.__isExpectedSlot(inputSlot, expectedSlot):
                    return False

        return True

    def getName(self):
        return self._service_name


    def __getAttribute(self, jsonObject, attributeName):
        if jsonObject == None or attributeName not in jsonObject:
            return None
        return jsonObject[attributeName]

    def __hasExpectedSlot(self, inputSlot:Slot, expectedSlots):
        for acceptableSlot in expectedSlots:
            if self.__isExpectedSlot(inputSlot, acceptableSlot):
                return True
        return False

    def __isExpectedSlot(self, inputSlot:Slot, expectedSlot):

        expectedSlotId = self.__getAttribute(expectedSlot, 'value')
        expectedSlotValue = self.__getAttribute(expectedSlot, 'id')

        return \
            (expectedSlotId == None or inputSlot.get_id() == expectedSlotId) and \
            (expectedSlotValue == None or inputSlot.get_value() == expectedSlotValue)




