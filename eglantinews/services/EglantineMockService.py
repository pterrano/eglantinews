import logging

from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineService import EglantineService


class EglantineMockService(EglantineService):

    _serviceName= "Mock"

    def __watchMovie(self, context: ExecutionContext):
        movie = context.getSlot('movie')

        logging.info('WATCH MOVIE: %s ' % movie)

        return "Ok, je mets le film %s " % movie

    def __watchPhotoAlbum(self, context: ExecutionContext):
        photoAlbum = context.getSlot('photoAlbum')

        logging.info('WATCH PHOTO ALBUM: %s ' % photoAlbum)

        return "Regardons l'album photo %s " % photoAlbum

    def getIntentConfigs(self):
        return {
            'WatchMovie': {
                'function': self.__watchMovie,
                'expected-slots': {
                    'movie': None
                }
            }
            ,
            'WatchPhotoAlbum': {
                'function': self.__watchPhotoAlbum,
                'expected-slots': {
                    'photoAlbum': None
                }
            }

        }
