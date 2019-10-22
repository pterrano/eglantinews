import logging

from alexa.AlexaRequest import AlexaRequest
from alexa.Slot import Slot
from alexa.Slots import Slots


class AlexaRequestParser:
    """
    Parse JSON request en return AlexaRequest
    """

    def parse(self, json: dict) -> AlexaRequest:

        alexa_request=AlexaRequest()

        if 'request' in json:

            json_request = json['request']

            if 'type' in json_request:
                alexa_request.set_request_type(json_request['type'])

            if 'intent' in json_request:
                alexa_intent = json_request['intent']

                if 'name' in alexa_intent:
                    intent = alexa_intent['name']
                    alexa_request.set_intent(intent)

            alexa_request.set_slots(self.__parse_slots(json_request))

        if 'context' in json:

            json_context = json['context']

            if 'System' in json_context:

                json_system = json_context['System']

                if 'user' in json_system:

                    json_user = json_system['user']

                    if 'userId' in json_user:

                        alexa_request.set_user_id(json_user['userId'])

                if 'device' in json_system:

                    json_device = json_system['device']

                    if 'deviceId' in json_device:

                        alexa_request.set_device_id(json_device['deviceId'])


        return alexa_request

    """
    Parse Slots in JSON request
    """

    def __parse_slots(self, json_request) -> Slots:

        slots = Slots()

        if 'intent' not in json_request:
            return slots

        json_intent = json_request['intent']

        if 'slots' not in json_intent:
            return slots

        json_slots = json_intent['slots']

        for slot_name in json_slots:

            json_slot = json_slots[slot_name]

            slot_id = self.__get_slot_id(json_slot)

            if 'value' in json_slot:
                slot_value = json_slot['value']
            else:
                slot_value = None

            slots.add(slot_name, Slot(slot_id, slot_value))

        return slots

    """
    Get Slot Id from JSON slot
    """

    def __get_slot_id(self, json_slot) -> str:

        if 'resolutions' not in json_slot:
            return None

        resolutions = json_slot['resolutions']
        if 'resolutionsPerAuthority' not in resolutions:
            return None

        resolutions_per_authority = resolutions['resolutionsPerAuthority']

        if len(resolutions_per_authority) < 1:
            return None

        for resolution_per_authority in resolutions_per_authority:

            if 'values' not in resolution_per_authority:
                continue

            values = resolution_per_authority['values']

            if len(values) > 0:
                return values[0]['value']['id']
