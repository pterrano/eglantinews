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


