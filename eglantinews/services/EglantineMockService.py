import logging

from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.services.EglantineService import EglantineService


class EglantineMockService(EglantineService):
    __service_name = "Mock"

    def __watch_movie(self, context: ExecutionContext):
        movie = context.get_slot_id('movie')

        logging.info('WATCH MOVIE: %s ' % movie)

        return "Ok, je mets le film %s " % movie

    def __watch_photo_album(self, context: ExecutionContext):
        photo_album = context.get_slot_id('photoAlbum')

        logging.info('WATCH PHOTO ALBUM: %s ' % photo_album)

        return "Regardons l'album photo %s " % photo_album

    def get_intent_configs(self):
        return {
            'WatchPhotoAlbum': {
                'function': self.__watch_photo_album,
                'expected-slots': {
                    'photoAlbum': None
                }
            }

        }
