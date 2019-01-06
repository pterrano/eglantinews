import logging
import time

from alexa.Slot import Slot
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext


class EglantineService:
    _service_name = None

    # Public

    def can_manage_intent(self, context: ExecutionContext) -> bool:

        intent_config = self._get_intent_config(context)

        if intent_config is None:
            return False

        return self._check_config(context)

    def process_intent(self, context: ExecutionContext) -> EglantineServiceResult:

        intent_config = self._get_intent_config(context)

        if 'complete-slots' in intent_config:
            context.add_slots(intent_config['complete-slots'])

        intent_function = self._get_intent_function(context)

        logging.info('PROCESS-INTENT - BEGIN - slots = %s' % str(context.get_slots().to_json()))

        t0 = time.perf_counter()

        result_function = intent_function(context)

        if result_function is None:
            result_function = EglantineServiceResult(None, False)
        if isinstance(result_function, str):
            result_function = EglantineServiceResult(result_function)

        logging.info('PROCESS-INTENT - END - %.1f - slots = %s' % (
            (time.perf_counter() - t0), str(context.get_slots().to_json())))

        logging.info('PROCESS-INTENT - RESULT="%s"' % result_function.get_sentence())

        return result_function

    # Protected

    def get_intent_configs(self):
        raise NotImplementedError

    def _get_intent_config(self, context: ExecutionContext):

        intent_configs = self.get_intent_configs()

        intent = context.get_intent()

        if intent in intent_configs:
            return intent_configs[intent]
        return None

    def _get_intent_function(self, context: ExecutionContext):

        intent_config = self._get_intent_config(context)

        return intent_config['function']

    def _check_config(self, context: ExecutionContext) -> bool:

        intent_config = self._get_intent_config(context)

        if 'expected-slots' in intent_config:

            expected_slots = intent_config['expected-slots']

            for expected_slot_name in expected_slots:

                input_slot: Slot = context.get_slot(expected_slot_name)
                if input_slot is None:
                    return False

                expected_slot = expected_slots[expected_slot_name]
                if expected_slot is None:
                    return True

                if isinstance(expected_slot, list):
                    return self.__has_expected_slot(input_slot, expected_slot)
                elif not self.__is_expected_slot(input_slot, expected_slot):
                    return False

        return True

    def get_name(self):
        return self._service_name

    def __get_attribute(self, json_object, attribute_name):
        if json_object is None or attribute_name not in json_object:
            return None
        return json_object[attribute_name]

    def __has_expected_slot(self, input_slot: Slot, expected_slots):
        for acceptable_slot in expected_slots:
            if self.__is_expected_slot(input_slot, acceptable_slot):
                return True
        return False

    def __is_expected_slot(self, input_slot: Slot, expected_slot):

        expected_slot_id = expected_slot.get_id();
        expected_slot_value = expected_slot.get_value();

        return \
            (expected_slot_id is None or input_slot.get_id() == expected_slot_id) and \
            (expected_slot_value is None or input_slot.get_value() == expected_slot_value)
