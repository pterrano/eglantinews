from kodijson import Kodi

from eglantinews.EglantineConfig import EglantineConfig
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineTVService import EglantineTVService


class EglantineMovieService(EglantineTVService):
    __config = EglantineConfig()

    _serviceName = "KODI"

    def __init__(self):
        EglantineTVService.__init__(self)
        url = self.__config.get_kodi_config()['url']
        self.__kodi = Kodi(url)

    def __find_movie(self, label):
        response = self.__kodi.VideoLibrary.GetMovies(
            {
                "filter": {
                    "field": "title",
                    "operator": "contains",
                    "value": label
                },
                "limits": {
                    "start": 0,
                    "end": 75
                },
                "sort": {
                    "order": "ascending",
                    "method": "title",
                    "ignorearticle": True
                }
            })

        if not 'result' in response or not 'movies' in response['result']:
            return None

        movies = response['result']['movies']

        if len(movies) == 0:
            return None
        else:
            return movies[0]

    def __check_result(self, response):
        return 'result' in response and response['result'] == 'OK'

    def __watch_movie(self, context: ExecutionContext):

        queryMovie = context.get_slot_value('queryMovie')

        movie = self.__find_movie(queryMovie)

        if movie is None:
            return Sentences.MOVIE_NOT_FOUND % (queryMovie)

        response = self.__kodi.Player.Open({"item": {"movieid": movie['movieid']}})

        if self.__check_result(response):
            return Sentences.MOVIE_FOUND % (movie['label'])
        else:
            return Sentences.MOVIE_ERROR_STARTED % (movie['label'])

    def get_intent_configs(self):

        super_config = EglantineTVService.get_intent_configs(self).copy()

        super_config.update({
            'WatchMovie': {
                'function': self.__watch_movie,
                'expected-slots': {
                    'queryMovie': None
                }
            },
        })

        return super_config
