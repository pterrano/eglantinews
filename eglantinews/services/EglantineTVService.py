import logging

from eglantinews.EglantineServiceResult import EglantineServiceResult
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineRoomService import EglantineRoomService
from samsungtv.SamsungTvRemote import SamsungTvRemote

TV_INPUT = 'av4'


class EglantineTVService(EglantineRoomService):

    _serviceName= "T.V."

    samsungTvRemote = SamsungTvRemote('tv', '5C:49:7D:EF:35:2B')

    def __turnOff(self, context: ExecutionContext):
        logging.info('OFF TV')
        self.samsungTvRemote.turnOff()
        return 'Extinction de la télé'

    def __turnOn(self, context: ExecutionContext):
        logging.info('ON TV')
        self.samsungTvRemote.turnOn()
        return EglantineServiceResult('Allumage de la télé')

    def __nextChannel(self, context: ExecutionContext):
        logging.info('NEXT CHANNEL')
        self.samsungTvRemote.sendKey('KEY_CHUP')
        return EglantineServiceResult(None, False, '')

    def __previousChannel(self, context: ExecutionContext):
        logging.info('PREVIOUS CHANNEL')
        self.samsungTvRemote.sendKey('KEY_CHDOWN')
        return EglantineServiceResult(None, False, '')

    def __changeChannel(self, context: ExecutionContext):

        room = context.getSlot('room', self._getDefaultRoom())

        channel = context.getSlot('channel')

        logging.info('CHANGE CHANNEL')

        self.samsungTvRemote.ensureUp()

        self._remoteByRoom(room).setInput(TV_INPUT)

        for digit in channel:
            self.samsungTvRemote.sendKey('KEY_' + digit)
            logging.info('sendKey KEY_' + digit)

        return EglantineServiceResult('Je mets la chaine %s' % channel, False)

    def __resume(self, context: ExecutionContext):
        self.samsungTvRemote.sendKey('KEY_PLAY')

        return EglantineServiceResult('Reprise du visionnage de la télé')

    def __pause(self, context: ExecutionContext):
        self.samsungTvRemote.sendKey('KEY_PAUSE')

        return EglantineServiceResult('Pause de la télé')

    def __returnDirect(self, context: ExecutionContext):
        self.samsungTvRemote.sendKey('KEY_STOP')

        return EglantineServiceResult('Retour au direct sur la télé')

    def __nothing(self, context: ExecutionContext):
        return ""

    def getIntentConfigs(self):
        return {
            'ChangeVolume': {
                'function': self._changeVolume,
                'expected-slots': {
                    'volume': None
                }
            },
            'TurnOn': {
                'function': self.__turnOn,
                'expected-slots': {
                    'room': 'la télé'}
            }
            ,
            'TurnOff': {
                'function': self.__turnOff,
                'expected-slots': {
                    'room': 'la télé'
                }
            },
            'TurnOffAll': {
                'function': self.__turnOff,
            },
            'ChangeChannel': {
                'function': self.__changeChannel,
                'expected-slots': {
                    'channel': None
                } ,
                'complete-slots' : {
                    'room' : 'le salon'
                }
            },
            'NextChannel': {
                'function': self.__nextChannel
            },
            'PreviousChannel': {
                'function': self.__previousChannel
            },
            'AMAZON.StopIntent': {
                'function': self.__nothing
            },
            'Next': {
                'function': self.__nextChannel
            },
            'Previous': {
                'function': self.__previousChannel
            },
            'Resume': {
                'function': self.__resume
            },
            'Pause': {
                'function': self.__pause
            },
            'ReturnDirect': {
                'function': self.__returnDirect
            },

        }
