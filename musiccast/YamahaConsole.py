from musiccast.Color import Color;
from musiccast.YamahaRemote import YamahaRemote;

class YamahaConsole:

    DIRECTORY_TYPE=125829122

    SPR='    '

    def __init__(self, hostName):
        self.remote = YamahaRemote(hostName);

    def setInput(self, input):

        lowerInput=input.lower()

        for remoteInput in self.getInputs():

            inputId = remoteInput['id'].lower()
            inputText = remoteInput['text'].lower()

            if inputId == lowerInput or inputText == lowerInput:
                self.remote.setInput(inputId);


    def setVolume(self, volume):
        self.remote.setVolume(volume);

    def setMute(self, mute):
        self.remote.setMute(mute);

    def play(self):
        self.remote.play();

    def stop(self):
        self.remote.stop();

    def pause(self):
        self.remote.pause();

    def nextSong(self):
        self.remote.nextSong();

    def previousSong(self):
        self.remote.previousSong();

    def isOn(self):
        self.remote.isOn();

    def turnOn(self):
        self.remote.turnOn();

    def turnOff(self):
        self.remote.turnOff();

    def getInputs(self):
        return self.remote.getAllLabels()['input_list']

    def prepareInput(self, input):
        self.remote.prepareInput(input)

    def search(self, pattern, searchType, media='server'):
        return self.remote.searchPlay(pattern, searchType, media)

    def sumUp(self):
        self.showCommonInfo()
        self.showPlayback(True)
        self.showPlayList(True)

    def showInputs(self, displayTitle = False):

        if displayTitle:
            print()
            print('Inputs list')

        currentInput = self.remote.getInput();

        for input in self.getInputs():

            line = '%-15s%-15s' % (input['id'], input['text'])

            if input['id'] == currentInput:
                print(Color.BOLD + Color.GREEN + '(*) ' + line + Color.END)
            else:
                print(self.SPR + line)

    def showCommonInfo(self):

        if (self.remote.isOn()):
            power = Color.GREEN + '[ON]' + Color.END
        else:
            power = Color.RED + '[OFF]' + Color.END

        print('Power : %s' % power)

        if (self.remote.isPlay()):
            playback = Color.GREEN + '[PLAY]' + Color.END
        elif (self.remote.isPaused()):
            playback = Color.YELLOW + '[PAUSE]' + Color.END
        elif (self.remote.isStopped()):
            playback = Color.RED + '[STOPPED]' + Color.END
        print('Playback : %s' % playback)

        if (self.remote.isMute()):
            muted = ' (muted)'
        else:
            muted = ''

        print('Level : {}/100 {}'.format(self.remote.getVolume(), muted))

    def showPlayback(self, displayTitle = False):

        playInfo=self.remote.getPlayInfo()

        if not self.remote.isStopped():
            if displayTitle:
                print()
                print('Current playback...')
            if self.remote.getInput() == 'net_radio':
                print(self.SPR+'Radio: %s' % playInfo['artist'])
            else:
                print(self.SPR+'Artist: %s' % playInfo['artist'])
                print(self.SPR+'Album: %s' % playInfo['album'])
                print(self.SPR+'Track: %s' % playInfo['track'])
                print(self.SPR+'Time: %i' % playInfo['play_time'])


    def showDirectory(self, path, displayTitle = False):

        self.__gotoPath(path)

        files=self.remote.listDirectory()

        if displayTitle:
            print()
            print('%-15s%s' % Color.BOLD+''+Color.END, Color.BOLD+'List music files'+Color.END)
            print
        for index in range(len(files)):

            file=files[index]

            if file['attribute']==self.DIRECTORY_TYPE:
                fileType='[dir]'
            else:
                fileType=str(index+1)

            print('%-15s%s' % Color.BOLD+fileType+Color.END, file['text'])


    def showPlayList(self, displayTitle = False):

        if not self.remote.isStopped():
            if displayTitle:
                print()
                print('Playlist')

            playIndex = self.remote.getPlayIndex()
            playList = self.remote.getPlayList()

            for index in range(len(playList)):

                track = self.SPR+'{:02d} {}'.format(index + 1, playList[index]['text'])

                if (index == playIndex):
                    print(Color.BOLD + track + Color.END)
                else:
                    print(track)


    def playFile(self, path, trackNumber):

        self.__gotoPath(path)

        self.remote.listInfo(0)

        self.remote.menuPlay(trackNumber-1)

    def playDirectory(self, path):

        self.__gotoPath(path)

        files=self.remote.listDirectory()

        for index in range(len(files)):

            file=files[index]

            if file['attribute'] != self.DIRECTORY_TYPE:
                self.remote.menuPlay(index)
                return

    def playTrack(self, trackNumber):
        self.remote.gotoPlayIndex(trackNumber - 1)
        self.play()



    def __gotoPath(self, path):

        self.remote.gotoRoot();

        self.remote.selectItem('nas')

        self.remote.selectItem('Musique')

        self.remote.selectItem('Par dossier')


        pathTokens=path.split('/')

        while '' in pathTokens:
            pathTokens.remove('')


        if len(pathTokens)>0 and pathTokens[0]=='media':
            pathTokens.remove('media')

        if len(pathTokens)>0 and pathTokens[0]=='nas':
            pathTokens.remove('nas')

        if len(pathTokens)>0 and pathTokens[0]=='music':
            pathTokens.remove('music')


        for pathToken in pathTokens:
            self.gotoDirectory(pathToken)


    def gotoDirectory(self, gotoItem):
        return self.remote.selectItem(gotoItem)