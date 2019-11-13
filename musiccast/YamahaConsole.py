from musiccast.Color import Color
from musiccast.YamahaRemote import YamahaRemote


class YamahaConsole:
    DIRECTORY_TYPE = 125829122

    SPR = '    '

    def __init__(self, host_name):
        self.remote = YamahaRemote(host_name)

    def set_input(self, input_source: str):

        lower_input = input_source.lower()

        for remote_input in self.get_inputs():

            input_id = remote_input['id'].lower()
            input_text = remote_input['text'].lower()

            if input_id == lower_input or input_text == lower_input:
                self.remote.set_input(input_id)

    def set_volume(self, volume):
        self.remote.set_volume(volume)

    def set_mute(self, mute):
        self.remote.set_mute(mute)

    def play(self):
        self.remote.play()

    def stop(self):
        self.remote.stop()

    def pause(self):
        self.remote.pause()

    def next_song(self):
        self.remote.next_song()

    def previous_song(self):
        self.remote.previous_song()

    def is_on(self):
        self.remote.is_on()

    def turn_on(self):
        self.remote.turn_on()

    def turn_off(self):
        self.remote.turn_off()

    def get_inputs(self):
        return self.remote.get_all_labels()['input_list']

    def prepare_input(self, input_source):
        self.remote.prepare_input(input_source)

    def search(self, pattern, search_type, media='server'):
        return self.remote.search_play(pattern, search_type, media)

    def sum_up(self):
        self.show_common_info()
        self.show_playback(True)
        self.show_play_list(True)

    def show_inputs(self, display_title=False):

        if display_title:
            print()
            print('Inputs list')

        current_input = self.remote.get_input()

        for inputSource in self.get_inputs():

            line = '%-15s%-15s' % (inputSource['id'], inputSource['text'])

            if inputSource['id'] == current_input:
                print(Color.BOLD + Color.GREEN + '(*) ' + line + Color.END)
            else:
                print(self.SPR + line)

    def show_common_info(self):

        if self.remote.is_on():
            power = Color.GREEN + '[ON]' + Color.END
        else:
            power = Color.RED + '[OFF]' + Color.END

        print('Power : %s' % power)

        if self.remote.is_play():
            playback = Color.GREEN + '[PLAY]' + Color.END
        elif self.remote.is_paused():
            playback = Color.YELLOW + '[PAUSE]' + Color.END
        else:
            playback = Color.RED + '[STOPPED]' + Color.END

        print('Playback : %s' % playback)

        if self.remote.is_mute():
            muted = ' (muted)'
        else:
            muted = ''

        print('Level : {}/100 {}'.format(self.remote.get_volume(), muted))

    def show_playback(self, display_title=False):

        play_info = self.remote.get_play_info()

        if not self.remote.is_stopped():
            if display_title:
                print()
                print('Current playback...')
            if self.remote.get_input() == 'net_radio':
                print(self.SPR + 'Radio: %s' % play_info['artist'])
            else:
                print(self.SPR + 'Artist: %s' % play_info['artist'])
                print(self.SPR + 'Album: %s' % play_info['album'])
                print(self.SPR + 'Track: %s' % play_info['track'])
                print(self.SPR + 'Time: %i' % play_info['play_time'])

    def show_directory(self, path, display_title=False):

        self.__goto_path(path)

        files = self.remote.list_directory()

        if display_title:
            print()
            print('%-15s%s' % Color.BOLD + '' + Color.END, Color.BOLD + 'List music files' + Color.END)
            print()
        for index in range(len(files)):

            file = files[index]

            if file['attribute'] == self.DIRECTORY_TYPE:
                file_type = '[dir]'
            else:
                file_type = str(index + 1)

            print('%-15s%s' % Color.BOLD + file_type + Color.END, file['text'])

    def show_play_list(self, display_title=False):

        if not self.remote.is_stopped():
            if display_title:
                print()
                print('Playlist')

            play_index = self.remote.get_play_index()
            play_list = self.remote.get_play_list()

            for index in range(len(play_list)):

                track = self.SPR + '{:02d} {}'.format(index + 1, play_list[index]['text'])

                if index == play_index:
                    print(Color.BOLD + track + Color.END)
                else:
                    print(track)

    def play_file(self, path, track_number):

        self.__goto_path(path)

        self.remote.list_info(0)

        self.remote.menu_play(track_number - 1)

    def play_directory(self, path):

        self.__goto_path(path)

        files = self.remote.list_directory()

        for index in range(len(files)):

            file = files[index]

            if file['attribute'] != self.DIRECTORY_TYPE:
                self.remote.menu_play(index)
                return

    def play_track(self, track_number):
        self.remote.goto_play_index(track_number - 1)
        self.play()

    def __goto_path(self, path):

        self.remote.goto_root()

        self.remote.select_item('nas')

        self.remote.select_item('Musique')

        self.remote.select_item('Par dossier')

        path_tokens = path.split('/')

        while '' in path_tokens:
            path_tokens.remove('')

        if len(path_tokens) > 0 and path_tokens[0] == 'media':
            path_tokens.remove('media')

        if len(path_tokens) > 0 and path_tokens[0] == 'nas':
            path_tokens.remove('nas')

        if len(path_tokens) > 0 and path_tokens[0] == 'music':
            path_tokens.remove('music')

        for path_token in path_tokens:
            self.goto_directory(path_token)

    def goto_directory(self, goto_item: str):
        return self.remote.select_item(goto_item)
