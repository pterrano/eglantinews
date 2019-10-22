from kodijson import Kodi
import re
kodi = Kodi("http://mediacenter:8080/jsonrpc")

print(kodi.VideoLibrary.GetMovies(
    {
        "filter": {
            "field": "title",
            "operator": "contains",
            "value": "terminator deux le jugement dernier"
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
    }))

#print(kodi.Player.Open( {"item":{"movieid":1232}} ))


#print(kodi.Player.GetActivePlayers())

#playerId = kodi.Player.GetActivePlayers()['result'][0]['playerid']

#print(kodi.Player.Stop({"playerid": playerId}))

# kodi.Player.PlayPause()
