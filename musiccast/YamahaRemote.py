import json
import logging
import socket
import time

import requests
from musiccast.YamahaRadio import YamahaRadio
from utils.SearchUtils import distance

FOLDER_ATTRIBUTE = 2


class YamahaRemote:

    __CONTEXT_PATH = "/YamahaExtendedControl/v1"

    PAGE_SIZE = 8

    UNLINK_GROUP = "00000000000000000000000000000000"

    yamahaRadio=YamahaRadio()

    def __init__(self, hostName: str, remoteName: str = None, defaultVolume: int = None, maxVolume: int = None):
        self.baseURL = "http://" + hostName + self.__CONTEXT_PATH
        self.__hostName = hostName
        self.__remoteName = remoteName
        self.__defaultVolume = defaultVolume
        self.__maxVolume = maxVolume

    def getRemoteName(self):
        return self.__remoteName

    def getHostName(self):
        return self.__hostName

    def __checkResultCode(self, result, action):
        if 'response_code' not in result:
            raise Exception("Can't %s ! " % action)
        elif result['response_code'] != 0:
            raise Exception("Can't %s ! (%s)" % (action, result['response_code']))

    def __get(self, message, command, params=[]):
        return self.__http(message, 'GET', command, params)

    def __post(self, message, command, params=[]):
        return self.__http(message, 'POST', command, params)

    def __http(self, message, method, command, params=[]):

        url = self.baseURL + '/' + command

        t0 = time.perf_counter()

        if method == 'GET':
            result = requests.get(url=url, params=params).json()
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            self.__checkResultCode(result, message)
        elif method == 'POST':
            result = requests.post(url, data=json.dumps(params), headers={'content-type': 'application/json'}).json()
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            self.__checkResultCode(result, message)
        else:
            raise Exception('Unknown http method %s' % method)

        return result

    def prepareInput(self, input):
        self.__get('prepare input change %s' % input, 'main/prepareInputChange', params={'input': input})

    def linkServer(self, groupId, clientHostnames):

        clientIps = list(map(lambda hostname: socket.gethostbyname(hostname), clientHostnames))

        return self.__post('link server %s with clients %s ' % (self.__hostName, str(clientIps)), "dist/setServerInfo",
                           params={'group_id': groupId, 'type': 'add', 'zone': 'main', 'client_list': clientIps})

    def linkClient(self, groupId, serverHostname):

        serverIp = socket.gethostbyname(serverHostname)

        return self.__post('link client %s with server %s ' % (str(serverIp), self.__hostName), "dist/setClientInfo",
                           params={'group_id': groupId, 'zone': ['main'], 'server_ip_address': serverIp})

    def getLinkRole(self):
        distributionInfo = self.getDistributionInfo()
        if 'group_id' not in distributionInfo or distributionInfo['group_id'] == self.UNLINK_GROUP:
            return None
        return distributionInfo['role']

    def unlink(self):
        linkRole = self.getLinkRole()
        if linkRole == 'client':
            return self.unlinkClient()
        elif linkRole == 'server':
            return self.unlinkServer()
        else:
            return None

    def unlinkServer(self):
        return self.__post('unlink server %s' % self.__hostName, "dist/setServerInfo", params={'group_id': ''})

    def unlinkClient(self):
        return self.__post('unlink client %s' % self.__hostName, "dist/setClientInfo", params={'group_id': ''})

    def getDistributionInfo(self):
        return self.__get('get distribution info', 'dist/getDistributionInfo')

    def startDistribution(self):
        return self.__get('start distribution', 'dist/startDistribution', params={'num': 0})

    def createGroup(self, groupName):
        self.__post('set group name %s' % groupName, 'dist/setGroupName', params={'name': groupName})

    def playRadio(self, radio):

        media = 'net_radio'

        self.turnOn()
        self.prepareInput(media)
        self.gotoRoot()

        if self.selectItem('radio', media):

            self.__post('set search string %s' % radio, 'netusb/setSearchString',
                        params={'list_id': 'main', 'string': radio, 'index': 9})

            return self.selectNearest(radio, True, media)

        else:

            foundRadio=self.yamahaRadio.search(radio)

            if foundRadio!=None:

                self.__post('set stream %s' % foundRadio['title'], 'netusb/setYmapUri', params={'zone':'main','uri':'ymap://NET_RADIO@vTuner.com/%s' % foundRadio['id']})

                return foundRadio['title']

    def searchPlay(self, pattern, searchType, media='server'):

        self.turnOn()
        self.prepareInput(media)
        self.gotoRoot()

        if not self.selectItem('search', media):
            return None

        self.__post('set search string %s' % pattern, 'netusb/setSearchString',
                    params={'list_id': 'main', 'string': pattern, 'index': 6})

        ##tracks
        if searchType == 'tracks':

            self.setInput(media)

            ##on joue le premier titre
            if not self.selectAfterItem(searchType, True, media):
                return None

            return self.getPlayInfo(True)

        ##albums
        elif searchType == 'albums':

            ##on selectionne le premier album
            if not self.selectAfterItem(searchType, False, media):
                return None

            if len(self.listInfo(0, media)['list_info']) == 0:
                return None

            self.setInput(media)

            self.menuPlay(0)

            return self.getPlayInfo(True)

        ##artists
        elif searchType == 'artists':

            ##on selectionne le premier atist
            if not self.selectAfterItem(searchType, False, media):
                return None

            ##on selectionne top tracks
            if not self.selectItem('top tracks', media):
                return None

            if len(self.listInfo(0, media)['list_info']) == 0:
                return None

            self.setInput(media)

            self.menuPlay(0)

            return {'artist': pattern}

    def getStatus(self):
        return self.__get('get status', 'main/getStatus')

    def getPlayQueue(self, index):
        return self.__get('get play queue at %s' % index, 'netusb/getPlayQueue', params={'index': index})

    def getPlayInfo(self, waitResult=False):

        maxIteration = 6
        playInfo = self.__get('get play info', 'netusb/getPlayInfo')

        t0 = time.perf_counter()

        while waitResult and maxIteration > 0 and playInfo['track'] == '':
            maxIteration = maxIteration - 1
            time.sleep(0.4)
            playInfo = self.__get('get play info', 'netusb/getPlayInfo')

        logging.info("WAITING-PLAY-INFO - %.1f" % (time.perf_counter() - t0))

        return playInfo

    def getAllLabels(self):
        return self.__get('get all labels', 'system/getNameText')

    def gotoPlayIndex(self, index):
        return self.__get('goto play index %s' % index, 'netusb/managePlayQueue',
                          params={'type': 'play', 'index': index, 'zone': 'main'})

    def __findItemInList(self, listItem, item):
        try:
            return list(map(lambda line: line['text'].lower(), listItem)).index(item)
        except ValueError:
            return None

    def selectNearest(self, selectedItem, play: bool = False, media='server') -> str:

        listInfos = self.listInfo(0, media)['list_info']

        nearestIndex = -1
        nearestDistance = float('inf')
        nearestItem = None

        for currentIndex in range(0, len(listInfos)):
            listInfo = listInfos[currentIndex]
            if listInfo['attribute'] != FOLDER_ATTRIBUTE:
                currentItem = listInfo['text']
                currentDistance = distance(currentItem, selectedItem)

                if currentDistance < nearestDistance:
                    nearestIndex = currentIndex
                    nearestDistance = currentDistance
                    nearestItem = currentItem

        if nearestIndex != -1:
            if play:
                self.menuPlay(nearestIndex)
            else:
                self.menuSelect(nearestIndex)

        return nearestItem

    def selectItem(self, selectedItem, media='server'):

        selectedIndex = self.findItem(selectedItem, media)

        if selectedIndex != None:
            self.menuSelect(selectedIndex)
            return True
        else:
            logging.warn("Can't find item \"" + selectedItem + "\"")
            return False

    def selectAfterItem(self, selectedItem, play=False, media='server'):
        selectedIndex = self.findItem(selectedItem, media)
        if selectedIndex != None:
            if play:
                self.menuPlay(selectedIndex + 1)
            else:
                self.menuSelect(selectedIndex + 1)
            return True
        else:
            logging.warn("Can't find item \"" + selectedItem + "\"")
            return False

    def findItem(self, selectedItem, media='server'):

        menuIndex = 0

        data = self.listInfo(0, media)

        listInfos = data['list_info']

        if data['max_line'] > 0:

            selectedIndex = self.__findItemInList(listInfos, selectedItem)
            if (selectedIndex != None):
                return selectedIndex + menuIndex

            nbPage = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for pageIndex in range(1, nbPage):

                menuIndex = self.PAGE_SIZE * pageIndex

                listInfos = self.listInfo(menuIndex, media)['list_info']

                selectedIndex = self.__findItemInList(listInfos, selectedItem)
                if (selectedIndex != None):
                    return selectedIndex + menuIndex

        return None

    def listDirectory(self, media='server'):

        data = self.listInfo(0, media)

        result = data['list_info']

        if data['max_line'] > 0:

            nbPage = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for pageIndex in range(1, nbPage):
                data = self.listInfo(self.PAGE_SIZE * pageIndex, media)
                result.extend(data['list_info'])

        return result

    def getPlayList(self):

        data = self.getPlayQueue(0)

        result = data['track_info']

        if data['max_line'] > 0:

            nbPage = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for pageIndex in range(1, nbPage):
                data = self.getPlayQueue(self.PAGE_SIZE * pageIndex)
                result.extend(data['track_info'])

        return result

    def getPlayIndex(self):
        return self.getPlayQueue(0)['playing_index']

    def listInfo(self, index, media='server'):

        return self.__get('list %s' % index, 'netusb/getListInfo',
                          params={'list_id': 'main', 'input': media, 'lang': 'en', 'index': index,
                                  'size': self.PAGE_SIZE})

    def gotoRoot(self):
        try:
            for i in range(10):
                self.gotoParentDirectory();
        except:
            pass

    def gotoParentDirectory(self):
        self.__get('back menu', 'netusb/setListControl', params={'type': 'return', 'zone': 'main'})

    def menuPlay(self, index):
        self.__get('play menu index %s' % index, 'netusb/setListControl',
                   params={'type': 'play', 'zone': 'main', 'index': index})
        self.__waitPlay()

    def menuSelect(self, index):
        self.__get('select menu index %s' % index, 'netusb/setListControl',
                   params={'type': 'select', 'zone': 'main', 'index': index})

    def setInput(self, input):
        currentInput = self.getInput()
        if currentInput != input:
            self.__get('set input to %s' % input, 'main/setInput', params={'input': input})
            self.__waitInput(input)

    def setVolume(self, volume: int):
        maxVolume = self.__getMaxVolume();
        v = int(round((volume * maxVolume) / 100))
        self.__get('set volume to %s' % volume, 'main/setVolume', params={'volume': v})

    def setMute(self, status):
        self.__get('set mute to %s' % status, 'main/setMute', params={'enable': status})

    def setPlayback(self, playback):
        self.__get('set playback to %s' % playback, 'netusb/setPlayback', params={'playback': playback})

    def play(self):
        self.setPlayback('play')
        self.__waitPlay()

    def __waitPlay(self):
        maxIteration = 100
        while not self.isPlay() and maxIteration > 0:
            time.sleep(0.1)
            maxIteration = maxIteration - 1

    def __waitInput(self, input):
        maxIteration = 10
        logging.info('Waiting for input %s...' % input)

        currentInput = self.getInput()
        while currentInput != input and maxIteration > 0:
            logging.info('current input is %s' % currentInput)
            time.sleep(0.4)
            maxIteration = maxIteration - 1

        time.sleep(1)

        logging.info('current input is %s' % currentInput)

    def stop(self):
        return self.setPlayback('stop')

    def pause(self):
        return self.setPlayback('pause')

    def nextSong(self):
        return self.setPlayback('next')

    def previousSong(self):
        return self.setPlayback('previous')

    def setPower(self, power):
        result = self.__get('set power to %s' % power, 'main/setPower', params={'power': power})

    def turnOn(self):

        if self.isOn():
            return

        self.setPower('on')
        time.sleep(1)

        for iteration in range(100):
            if self.isOn():
                break
            time.sleep(0.1)

        if self.__defaultVolume != None:
            self.setVolume(self.__defaultVolume)

    def turnOff(self):
        self.setPower('standby')

    def getVolume(self) -> int:
        maxVolume = self.__getMaxVolume();
        volume = int(self.getStatus()['volume'])
        return int(round(100 * volume / maxVolume))

    def __getMaxVolume(self):
        if self.__maxVolume == None:
            return int(self.getStatus()['max_volume'])
        else:
            return self.__maxVolume

    def isMute(self):
        return bool(self.getStatus()['mute'])

    def isOn(self):
        power = self.getStatus()['power']
        return power == 'on'

    def isStopped(self):
        playback = self.getPlayInfo()['playback']
        return playback == 'stop'

    def isPlay(self):
        playback = self.getPlayInfo()['playback']
        return playback == 'play'

    def isPaused(self):
        playback = self.getPlayInfo()['playback']
        return playback == 'pause'

    def getInput(self):
        status = self.getStatus()
        return status['input']
