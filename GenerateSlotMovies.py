from kodijson import Kodi

from eglantinews.EglantineConfig import EglantineConfig
from utils.SearchUtils import simplify

config = EglantineConfig()

kodi = Kodi(config.get_kodi_config()['url'])

movies = kodi.VideoLibrary.GetMovies(
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
    })['result']['movies']

for movie in movies:
    print('"' + simplify(movie['label']) + '"')
