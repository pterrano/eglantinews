import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.Slot import Slot
from eglantinews.services.EglantineRoomService import EglantineRoomService
from samsungtv.SamsungTvRemote import SamsungTvRemote

TV_INPUT = 'av4'


class EglantineTVService(EglantineRoomService):
    _serviceName = "T.V."

    samsung_tv_remote = SamsungTvRemote('tv', '5C:49:7D:EF:35:2B')

    def __turn_off(self, context: ExecutionContext):
        logging.info('OFF TV')
        self.samsung_tv_remote.turn_off()
        return 'Extinction de la télé'

    def __turn_on(self, context: ExecutionContext):
        logging.info('ON TV')
        self.samsung_tv_remote.turn_on()
        return EglantineServiceResult('Allumage de la télé')

    def __next_channel(self, context: ExecutionContext):
        logging.info('NEXT CHANNEL')
        self.samsung_tv_remote.send_key('KEY_CHUP')
        return EglantineServiceResult(None, False, '')

    def __previous_channel(self, context: ExecutionContext):
        logging.info('PREVIOUS CHANNEL')
        self.samsung_tv_remote.send_key('KEY_CHDOWN')
        return EglantineServiceResult(None, False, '')

    def __change_channel(self, context: ExecutionContext):
        room = context.get_slot_id('room', self._get_default_room())

        channel = context.get_slot_id('channel')

        logging.info('CHANGE CHANNEL')

        self.samsung_tv_remote.ensure_up()

        self._remote_by_room(room).set_input(TV_INPUT)

        for digit in channel:
            self.samsung_tv_remote.send_key('KEY_' + digit)
            logging.info('sendKey KEY_' + digit)

        return EglantineServiceResult('Je mets la chaine %s' % channel, False)

    def __resume(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_PLAY')

        return EglantineServiceResult('Reprise du visionnage de la télé')

    def __pause(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_PAUSE')

        return EglantineServiceResult('Pause de la télé')

    def __return_direct(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_STOP')

        return EglantineServiceResult('Retour au direct sur la télé')

    def __nothing(self, context: ExecutionContext):
        return ""

    def _turn_off_all(self, context: ExecutionContext):
        self.__turn_off(context)
        super()._turn_off_all(context)
        return "Ok, j'éteins tout"

    def get_intent_configs(self):
        tv_room = Slot('TV')
        expected_tv_room = {'room': tv_room}
        expected_volume = {'volume': None}
        expected_channel = {'channel': None}

        return {
            'ChangeVolume': {
                'function': self._change_volume,
                'expected-slots': expected_volume
            },
            'TurnOn': {
                'function': self.__turn_on,
                'expected-slots': expected_tv_room
            },
            'TurnOff': {
                'function': self.__turn_off,
                'expected-slots': expected_tv_room
            },
            'TurnOffAll': {
                'function': self._turn_off_all,
            },
            'ChangeChannel': {
                'function': self.__change_channel,
                'expected-slots': expected_channel
            },
            'NextChannel': {
                'function': self.__next_channel
            },
            'PreviousChannel': {
                'function': self.__previous_channel
            },
            'AMAZON.StopIntent': {
                'function': self.__nothing
            },
            'Next': {
                'function': self.__next_channel
            },
            'Previous': {
                'function': self.__previous_channel
            },
            'Resume': {
                'function': self.__resume
            },
            'Pause': {
                'function': self.__pause
            },
            'ReturnDirect': {
                'function': self.__return_direct
            },

        }
