import logging

from alexa.Slot import Slot
from eglantinews.EglantineConfig import EglantineConfig
from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineRoomService import EglantineRoomService
from samsungtv.SamsungTvRemote import SamsungTvRemote

class EglantineTVService(EglantineRoomService):
    __config = EglantineConfig()

    _serviceName = "T.V."

    samsung_tv_remote: SamsungTvRemote = None

    def __init__(self):
        tv_config = self.__config.get_samsung_tv_config()
        self._tv_input = tv_config['input']
        self.samsung_tv_remote = SamsungTvRemote(tv_config['hostname'], tv_config['mac'])

    def __turn_off(self, context: ExecutionContext):
        logging.info('OFF TV')
        self.samsung_tv_remote.turn_off()
        return Sentences.TURN_OFF_TV

    def __turn_on(self, context: ExecutionContext):
        logging.info('ON TV')
        self.samsung_tv_remote.turn_on()
        self.samsung_tv_remote.send_key('KEY_CHUP')
        self.samsung_tv_remote.send_key('KEY_DOWN')
        return Sentences.TURN_ON_TV

    def __next_channel(self, context: ExecutionContext):
        logging.info('NEXT CHANNEL')
        self.samsung_tv_remote.send_key('KEY_CHUP')
        return EglantineServiceResult(None, False, "")

    def __previous_channel(self, context: ExecutionContext):
        logging.info('PREVIOUS CHANNEL')
        self.samsung_tv_remote.send_key('KEY_CHDOWN')
        return EglantineServiceResult(None, False, "")

    def __change_channel(self, context: ExecutionContext):

        room = context.get_slot_id('room', self._get_default_room())

        channel = context.get_slot_id('channel')

        logging.info('CHANGE CHANNEL')

        self.samsung_tv_remote.ensure_up()

        self._remote(room).set_input(self._tv_input)

        if context.service_changed():
            self.__next_channel(context)
            self.__previous_channel(context)

        for digit in channel:
            self.samsung_tv_remote.send_key('KEY_' + digit)
            logging.info('sendKey KEY_' + digit)

        return EglantineServiceResult(Sentences.CHANGE_CHANNEL % channel, False)

    def __stop(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_STOP')
        return EglantineServiceResult(Sentences.STOP_TV)

    def __resume(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_PLAY')

        return EglantineServiceResult(Sentences.RESUME_TV)

    def __pause(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_PAUSE')

        return EglantineServiceResult(Sentences.PAUSE_TV)

    def __return_direct(self, context: ExecutionContext):
        self.samsung_tv_remote.send_key('KEY_STOP')

        return EglantineServiceResult(Sentences.RETURN_TO_DIRECT)

    def __nothing(self, context: ExecutionContext):
        return ""

    def _turn_off_all(self, context: ExecutionContext):
        self.__turn_off(context)
        super()._turn_off_all(context)
        return Sentences.TURN_OFF_ALL

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
            'IncreaseVolume': {
                'function': self._increase_volume,
            },
            'DecreaseVolume': {
                'function': self._decrease_volume,
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
                'function': self.__stop
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
            'ResumeRoom': {
                'function': self.__resume,
                'expected-slots': expected_tv_room
            },
            'Pause': {
                'function': self.__pause
            },
            'PauseRoom': {
                'function': self.__pause,
                'expected-slots': expected_tv_room
            },
            'ReturnDirect': {
                'function': self.__return_direct
            },

        }
