import base64
import json
import time
import asyncio
import websockets
from wakeonlan import send_magic_packet

class SamsungTvRemote:

    __DEFAULT_PORT=8001

    __CONTEXT_PATH = "/api/v2/channels/samsung.remote.control?name="

    __DEFAULT_REMOTE_NAME="SamsungTvRemote"

    __KEY_SLEEP=1

    __KEY_TEST='KEY_TEST'

    DEBUG = True

    PAGE_SIZE=8

    def __serialize_string(self, string):
        if isinstance(string, str):
            string = str.encode(string)
        return base64.b64encode(string).decode("utf-8")

    def __init__(self, hostName, macAddress=None, remoteName=__DEFAULT_REMOTE_NAME):
        self.url = "ws://" + hostName + ':' + str(self.__DEFAULT_PORT) +self.__CONTEXT_PATH +  self.__serialize_string(remoteName)
        self.macAddress=macAddress

    async def __asyncSendKey(self, key):
        async with websockets.connect(self.url) as websocket:
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

            payload = json.dumps({
                "method": "ms.channel.emit",
                 "params": {
                     "event": "ed.apps.launch",
                     "to": "host",
                     "data": {"appId": "bstjKvX6LM.molotov",
                      "action_type": "DEEP_LINK"}
                }
            })

            """
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
            
            """


            payload = json.dumps({"method":"ms.channel.emit","params":{"event": "ed.apps.launch", "to":"host", "data":{"appId": "org.tizen.browser", "action_type": "NATIVE_LAUNCH"}}})


            payload = json.dumps({
                "method": "ms.channel.emit",
                 "params": {
                     "event": "ed.apps.launch",
                     "to": "host",
                     "data": {"appId": "9Ur5IzDKqV.TizenYouTube",
                      "action_type": "DEEP_LINK"}
                }
            })

            payload = json.dumps({"method":"ms.channel.emit","params":{"event": "ed.apps.launch", "to":"host", "data":{"appId": "org.tizen.browser", "action_type": "NATIVE_LAUNCH"}}})

            """ Close Current Application """
            payload = json.dumps({"method": "ms.channel.emit", "params": {"event": "ed.apps.launch", "to": "host", "data": {"appId": "org.tizen.tv-viewer", "action_type": "NATIVE_LAUNCH"}}})


            await websocket.send(payload)

            if key != self.__KEY_TEST:
                time.sleep(self.__KEY_SLEEP)

    def sendKey(self, key):
        self.ensureUp()
        loop=asyncio.new_event_loop()
        loop.run_until_complete(self.__asyncSendKey(key))


    def isUp(self):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.__asyncSendKey('KEY_TEST'))
            return True
        except:
            return False

    def ensureUp(self):
        if self.macAddress==None or self.isUp():
            return

        self.turnOn()
        time.sleep(3)
        for iteration in range(10):
            if (self.isUp()):
                return


    def turnOn(self):
        if self.macAddress!=None:
            send_magic_packet(self.macAddress)

    def turnOff(self):
        if self.isUp():
            self.sendKey('KEY_POWER')


