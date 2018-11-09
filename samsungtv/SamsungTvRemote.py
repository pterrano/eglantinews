import asyncio
import base64
import json
import time

import websockets
from wakeonlan import send_magic_packet


class SamsungTvRemote:
    __DEFAULT_PORT = 8001
    __CONTEXT_PATH = "/api/v2/channels/samsung.remote.control?name="
    __DEFAULT_REMOTE_NAME = "SamsungTvRemote"
    __KEY_SLEEP = 1
    __KEY_TEST = 'KEY_TEST'
    __DEBUG = True
    __PAGE_SIZE = 8

    __url: str = None

    __mac_address: str = None

    def __serialize_string(self, string):
        if isinstance(string, str):
            string = str.encode(string)
        return base64.b64encode(string).decode("utf-8")

    def __init__(self, host_name: str, mac_address: str = None, remote_name: str = __DEFAULT_REMOTE_NAME):
        self.__url = "ws://" + host_name + ':' + str(
            self.__DEFAULT_PORT) + self.__CONTEXT_PATH + self.__serialize_string(
            remote_name)
        self.__mac_address = mac_address

    async def __async_send_key(self, key):
        async with websockets.connect(self.__url) as websocket:
            result = await websocket.recv()

            print(result)

            payload = json.dumps({
                "method": "ms.remote.control",
                "params": {
                    "Cmd": "Click",
                    "DataOfCmd": key,
                    "Option": "false",
                    "TypeOfRemote": "SendRemoteKey"
                }
            })
            """

            payload = json.dumps({
                "method": "ms.channel.emit",
                "params": {
                    "event": "ed.apps.launch",
                    "to": "host",
                    "data": {"appId": "bstjKvX6LM.molotov",
                             "action_type": "DEEP_LINK"}
                }
            })

            Ahw07WXIjx.Dailymotion
tisT7SVUug.tunein
cexr1qp97S.Deezer
xqqJ00GGlC.okidoki
4ovn894vo9.Facebook
vbUQClczfR.Wuakitv
QizQxC7CUf.PlayMovies
QBA3qXl8rv.Kick
DJ8grEH6Hu.arte
JtPoChZbf4.Vimeo
hIWwRyZjcD.GameFlyStreaming
sHi2hDJGmf.nolim
guMmq95nKK.CanalPlusLauncher
RN1MCdNq8t.Netflix / org.tizen.netflix-app
evKhCgZelL.AmazonIgnitionLauncher2 / org.tizen.ignition
9Ur5IzDKqV.TizenYouTube
gDhibXvFya.HBOGO
EmCpcvhukH.ElevenSports
ASUvdWVqRb.FilmBoxLive
rJeHak5zRg.Spotify
ABor2M9vjb.acc   (AccuWeather)
EkzyZtmneG.My5
yFo6bAK50v.Dennexpres
gdEZI5lLXr.Europa2FHD
bm9PqdAwjv.TvSme
dH3Ztod7bU.IDNES
wsFJCxteqc.OnetVodEden
rZyaXW5csM.TubaFM
4bjaTLNMia.curzon
RVvpJ8SIU6.ocs
bstjKvX6LM.molotov
RffagId0eC.SfrSport
phm0eEdRZ4.ExtraTweetIM2
VAarU8iUtx.samsungTizen   (Vevo)
g0ScrkpO1l.SmartIPTV
kIciSQlYEM.plex
            

            payload = json.dumps({"method": "ms.channel.emit", "params": {"event": "ed.apps.launch", "to": "host",
                                                                          "data": {"appId": "org.tizen.browser",
                                                                                   "action_type": "NATIVE_LAUNCH"}}})

            payload = json.dumps({
                "method": "ms.channel.emit",
                "params": {
                    "event": "ed.apps.launch",
                    "to": "host",
                    "data": {"appId": "9Ur5IzDKqV.TizenYouTube",
                             "action_type": "DEEP_LINK"}
                }
            })

            payload = json.dumps({"method": "ms.channel.emit", "params": {"event": "ed.apps.launch", "to": "host",
                                                                "data": {"appId": "org.tizen.browser",
                                                                         "action_type": "NATIVE_LAUNCH"}}})

            ## Close Current Application
            payload = json.dumps({"method": "ms.channel.emit", "params": {"event": "ed.apps.launch", "to": "host",
                                                                          "data": {"appId": "org.tizen.tv-viewer",
                                                                                   "action_type": "NATIVE_LAUNCH"}}})

            """
            await websocket.send(payload)

            if key != self.__KEY_TEST:
                time.sleep(self.__KEY_SLEEP)

    def send_key(self, key):
        self.ensure_up()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.__async_send_key(key))

    def is_up(self):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.__async_send_key('KEY_TEST'))
            return True
        except:
            return False

    def ensure_up(self):
        if self.__mac_address is None or self.is_up():
            return

        self.turn_on()
        time.sleep(3)
        for iteration in range(10):
            if self.is_up():
                return

    def turn_on(self):
        if self.__mac_address is not None:
            send_magic_packet(self.__mac_address)

    def turn_off(self):
        if self.is_up():
            self.send_key('KEY_POWER')
