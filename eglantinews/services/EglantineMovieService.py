from kodijson import Kodi

from eglantinews.EglantineConfig import EglantineConfig
from eglantinews.ExecutionContext import ExecutionContext
from eglantinews.sentences.Sentences import Sentences
from eglantinews.services.EglantineTVService import EglantineTVService
from utils.SearchUtils import simplify


class EglantineMovieService(EglantineTVService):
    _kodi_config = EglantineConfig().get_kodi_config()

    _serviceName = "KODI"

    def __init__(self):
        EglantineTVService.__init__(self)
        self._kodi = Kodi(self._kodi_config['url'])
        self._kodi_input = self._kodi_config['input']

    def __find_movie(self, query: str):
        movies = self.__get_movies()
        if movies is None:
            return None

        simplified_query = simplify(query)

        for movie in movies:
            if simplified_query == simplify(movie['label']):
                return movie

        for movie in movies:
            if simplified_query in simplify(movie['label']):
                return movie

    def __get_movies(self):
        response = self._kodi.VideoLibrary.GetMovies(
            {
                "limits": {
                    "start": 0,
                    "end": 10000
                },
                "sort": {
                    "order": "ascending",
                    "method": "title",
                    "ignorearticle": True
                }
            })

        if not 'result' in response or not 'movies' in response['result']:
            return None

        return response['result']['movies']

    def __check_result(self, response):
        return 'result' in response and response['result'] == 'OK'

    def __watch_movie(self, context: ExecutionContext):

        queryMovie = context.get_slot_value('queryMovie')

        movie = self.__find_movie(queryMovie)

        if movie is None:
            return Sentences.MOVIE_NOT_FOUND % (queryMovie)

        room = context.get_slot_id('room', self._get_default_room())

        self._remote(room).set_input(self._kodi_input)

        response = self._kodi.Player.Open({"item": {"movieid": movie['movieid']}})

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
