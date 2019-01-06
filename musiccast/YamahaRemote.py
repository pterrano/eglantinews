import json
import logging
import socket
import time

import requests

from musiccast.YamahaException import YamahaException
from musiccast.YamahaRadio import YamahaRadio
from utils.SearchUtils import distance


class YamahaRemote:
    __CONTEXT_PATH = "/YamahaExtendedControl/v1"

    PAGE_SIZE = 8

    UNLINK_GROUP = "00000000000000000000000000000000"

    DEFAULT_STEP_VOLUME = 10

    FOLDER_ATTRIBUTE = 2

    __yamaha_radio = YamahaRadio()

    __baseURL: str = None
    __host_name: str = None
    __remote_name: str = None
    __default_volume: int = None
    __max_volume: int = None

    def __init__(self, host_name: str, remote_name: str = None, default_volume: int = None, max_volume: int = None):
        self.__baseURL = "http://" + host_name + self.__CONTEXT_PATH
        self.__host_name = host_name
        self.__remote_name = remote_name
        self.__default_volume = default_volume
        self.__max_volume = max_volume

    def get_remote_name(self) -> str:
        return self.__remote_name

    def get_host_name(self):
        return self.__host_name

    def __check_result_code(self, result, action):
        if 'response_code' not in result:
            raise YamahaException("Can't %s ! " % action)
        elif result['response_code'] != 0:
            raise YamahaException("Can't %s ! (%s)" % (action, result['response_code']))

    def __get(self, message, command, params={}):
        return self.__http(message, 'GET', command, params)

    def __post(self, message, command, params={}):
        return self.__http(message, 'POST', command, params)

    def __http(self, message, method, command, params={}):

        url = self.__baseURL + '/' + command

        t0 = time.perf_counter()

        if method == 'GET':
            result = requests.get(url=url, params=params).json()
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            self.__check_result_code(result, message)
        elif method == 'POST':
            result = requests.post(url, data=json.dumps(params), headers={'content-type': 'application/json'}).json()
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            self.__check_result_code(result, message)
        else:
            raise YamahaException('Unknown http method %s' % method)

        return result

    def prepare_input(self, input_source):
        self.__get('prepare input change %s' % input_source, 'main/prepareInputChange', params={'input': input_source})

    def link_server(self, group_id, client_hostnames):

        client_ips = list(map(lambda hostname: socket.gethostbyname(hostname), client_hostnames))

        return self.__post('link server %s with clients %s ' % (self.__host_name, str(client_ips)),
                           "dist/setServerInfo",
                           params={'group_id': group_id, 'type': 'add', 'zone': 'main', 'client_list': client_ips})

    def link_client(self, group_id, server_hostname):

        server_ip = socket.gethostbyname(server_hostname)

        return self.__post('link client %s with server %s ' % (str(server_ip), self.__host_name), "dist/setClientInfo",
                           params={'group_id': group_id, 'zone': ['main'], 'server_ip_address': server_ip})

    def get_link_role(self):
        distribution_info = self.get_distribution_info()
        if 'group_id' not in distribution_info or distribution_info['group_id'] == self.UNLINK_GROUP:
            return None
        return distribution_info['role']

    def unlink(self):
        link_role = self.get_link_role()
        if link_role == 'client':
            return self.unlink_client()
        elif link_role == 'server':
            return self.unlink_server()
        else:
            return None

    def unlink_server(self):
        return self.__post('unlink server %s' % self.__host_name, "dist/setServerInfo", params={'group_id': ''})

    def unlink_client(self):
        return self.__post('unlink client %s' % self.__host_name, "dist/setClientInfo", params={'group_id': ''})

    def get_distribution_info(self):
        return self.__get('get distribution info', 'dist/getDistributionInfo')

    def start_distribution(self):
        return self.__get('start distribution', 'dist/startDistribution', params={'num': 0})

    def create_group(self, group_name):
        self.__post('set group name %s' % group_name, 'dist/setGroupName', params={'name': group_name})

    def play_radio(self, radio):

        media = 'net_radio'

        self.turn_on()
        self.prepare_input(media)
        self.goto_root()

        if self.select_item('radio', media):

            self.__post('set search string %s' % radio, 'netusb/setSearchString',
                        params={'list_id': 'main', 'string': radio, 'index': 9})

            return self.select_nearest(radio, True, media)

        else:

            found_radio = self.__yamaha_radio.search(radio)

            if found_radio is not None:
                self.__post('set stream %s' % found_radio['title'], 'netusb/setYmapUri',
                            params={'zone': 'main', 'uri': 'ymap://NET_RADIO@vTuner.com/%s' % found_radio['id']})

                return found_radio['title']

    def search_play(self, pattern, search_type: str, media='server'):

        self.turn_on()
        self.prepare_input(media)
        self.goto_root()

        if not self.select_item('search', media):
            return None

        self.__post('set search string %s' % pattern, 'netusb/setSearchString',
                    params={'list_id': 'main', 'string': pattern, 'index': 6})

        # tracks
        if search_type == 'tracks':

            self.set_input(media)

            # on selectionne all tracks
            if not self.select_item('all tracks', media):
                #si on y arrive pas on prend le premier
                if not self.select_after_item(search_type, True, media):
                    return None

            # on selectionne le track le plus proche parmis les 8 premiers
            elif not self.select_nearest(pattern, True, media):
                return None


            return self.get_play_info(True)

        # albums
        elif search_type == 'albums':

            # on selectionne all albums
            if not self.select_item('all albums', media):
                #si on y arrive pas on prend le premier
                if not self.select_after_item(search_type, False, media):
                    return None

            # on selectionne l'album le plus proche parmis les 8 premiers
            elif not self.select_nearest(pattern, False, media):
                return None

            if len(self.list_info(0, media)['list_info']) == 0:
                return None

            self.set_input(media)

            self.menu_play(0)

            return self.get_play_info(True)

        # artists
        elif search_type == 'artists':

            # on selectionne all artists
            if not self.select_item('all artists', media):
                if not self.select_after_item(search_type, False, media):
                    return None
            # on selectionne l'artist le plus proche parmis les 8 premiers
            elif not self.select_nearest(pattern, False, media):
                return None

            # on selectionne top tracks
            if not self.select_item('top tracks', media):
                return None

            if len(self.list_info(0, media)['list_info']) == 0:
                return None

            self.set_input(media)

            self.menu_play(0)

            return {'artist': pattern}

    def get_status(self):
        return self.__get('get status', 'main/getStatus')

    def get_play_queue(self, index):
        return self.__get('get play queue at %s' % index, 'netusb/getPlayQueue', params={'index': index})

    def get_play_info(self, wait_result=False):

        max_iteration = 6

        play_info = self.__get('get play info', 'netusb/getPlayInfo')

        t0 = time.perf_counter()

        while wait_result and max_iteration > 0 and play_info['track'] == '':
            max_iteration = max_iteration - 1
            time.sleep(0.4)
            play_info = self.__get('get play info', 'netusb/getPlayInfo')

        logging.info("WAITING-PLAY-INFO - %.1f" % (time.perf_counter() - t0))

        return play_info

    def get_all_labels(self):
        return self.__get('get all labels', 'system/getNameText')

    def goto_play_index(self, index):
        return self.__get('goto play index %s' % index, 'netusb/managePlayQueue',
                          params={'type': 'play', 'index': index, 'zone': 'main'})

    def __find_item_in_list(self, list_item, item):
        try:
            return list(map(lambda line: line['text'].lower(), list_item)).index(item)
        except ValueError:
            return None

    def select_nearest(self, selected_item: str, play: bool = False, media='server') -> str:

        list_infos = self.list_info(0, media)['list_info']

        nearest_index = -1
        nearest_distance = float('inf')
        nearest_item = None

        for current_index in range(0, len(list_infos)):
            list_info = list_infos[current_index]
            if list_info['attribute'] != self.FOLDER_ATTRIBUTE:
                current_item = list_info['text']
                current_distance = distance(current_item, selected_item)

                if current_distance < nearest_distance:
                    nearest_index = current_index
                    nearest_distance = current_distance
                    nearest_item = current_item

        if nearest_index != -1:
            if play:
                self.menu_play(nearest_index)
            else:
                self.menu_select(nearest_index)

        return nearest_item

    def select_item(self, selected_item, media='server'):

        selected_index = self.find_item(selected_item, media)

        if selected_index is not None:
            self.menu_select(selected_index)
            return True
        else:
            logging.warning("Can't find item \"" + selected_item + "\"")
            return False

    def select_after_item(self, selected_item, play=False, media='server'):
        selected_index = self.find_item(selected_item, media)
        if selected_index is not None:
            if play:
                self.menu_play(selected_index + 1)
            else:
                self.menu_select(selected_index + 1)
            return True
        else:
            logging.warning("Can't find item \"" + selected_item + "\"")
            return False

    def find_item(self, selected_item, media='server'):

        menu_index = 0

        data = self.list_info(0, media)

        list_infos = data['list_info']

        if data['max_line'] > 0:

            selected_index = self.__find_item_in_list(list_infos, selected_item)
            if selected_index is not None:
                return selected_index + menu_index

            nb_page = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for page_index in range(1, nb_page):

                menu_index = self.PAGE_SIZE * page_index

                list_infos = self.list_info(menu_index, media)['list_info']

                selected_index = self.__find_item_in_list(list_infos, selected_item)
                if selected_index is not None:
                    return selected_index + menu_index

        return None

    def list_directory(self, media='server'):

        data = self.list_info(0, media)

        result = data['list_info']

        if data['max_line'] > 0:

            nb_page = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for page_index in range(1, nb_page):
                data = self.list_info(self.PAGE_SIZE * page_index, media)
                result.extend(data['list_info'])

        return result

    def get_play_list(self):

        data = self.get_play_queue(0)

        result = data['track_info']

        if data['max_line'] > 0:

            nb_page = int(1 + (data['max_line'] - 1) / self.PAGE_SIZE)

            for pageIndex in range(1, nb_page):
                data = self.get_play_queue(self.PAGE_SIZE * pageIndex)
                result.extend(data['track_info'])

        return result

    def get_play_index(self):
        return self.get_play_queue(0)['playing_index']

    def list_info(self, index, media='server'):

        return self.__get('list %s' % index, 'netusb/getListInfo',
                          params={'list_id': 'main', 'input': media, 'lang': 'en', 'index': index,
                                  'size': self.PAGE_SIZE})

    def goto_root(self):
        try:
            for i in range(10):
                self.goto_parent_directory()
        except YamahaException:
            print()

    def goto_parent_directory(self):
        self.__get('back menu', 'netusb/setListControl', params={'type': 'return', 'zone': 'main'})

    def menu_play(self, index):
        self.__get('play menu index %s' % index, 'netusb/setListControl',
                   params={'type': 'play', 'zone': 'main', 'index': index})
        self.__wait_play()

    def menu_select(self, index):
        self.__get('select menu index %s' % index, 'netusb/setListControl',
                   params={'type': 'select', 'zone': 'main', 'index': index})

    def set_input(self, input_source: str, mode:str='autoplay_disabled'):
        current_input = self.get_input()
        if current_input != input_source:
            self.__get('set input to %s' % input_source, 'main/setInput', params={'input': input_source, 'mode': mode})
            self.__wait_input(input_source)

    def set_volume(self, volume: int):
        max_volume = self.__get_max_volume()
        v = int(round((volume * max_volume) / 100))
        self.__get('set volume to %s' % volume, 'main/setVolume', params={'volume': v})

    def increase_volume(self, step:int=DEFAULT_STEP_VOLUME):
        max_volume = self.__get_max_volume()
        s = int(round((step * max_volume) / 100))
        self.__get('increase volume to %s' % s, 'main/setVolume', params={'volume': 'up', 'step': s})

    def decrease_volume(self, step:int=DEFAULT_STEP_VOLUME):
        max_volume = self.__get_max_volume()
        s = int(round((step * max_volume) / 100))
        self.__get('decrease volume to %s' % s, 'main/setVolume', params={'volume': 'down', 'step': s})

    def set_mute(self, status):
        self.__get('set mute to %s' % status, 'main/setMute', params={'enable': status})

    def set_playback(self, playback):
        self.__get('set playback to %s' % playback, 'netusb/setPlayback', params={'playback': playback})

    def play(self):
        self.set_playback('play')
        self.__wait_play()

    def __wait_play(self):
        max_iteration = 100
        while not self.is_play() and max_iteration > 0:
            time.sleep(0.1)
            max_iteration = max_iteration - 1

    def __wait_input(self, input_source: str):
        max_iteration = 10
        logging.info('Waiting for input %s...' % input_source)

        current_input = self.get_input()
        while current_input != input_source and max_iteration > 0:
            logging.info('current input is %s' % current_input)
            time.sleep(0.4)
            max_iteration = max_iteration - 1

        time.sleep(1)

        logging.info('current input is %s' % current_input)

    def stop(self):
        return self.set_playback('stop')

    def pause(self):
        return self.set_playback('pause')

    def next_song(self):
        return self.set_playback('next')

    def previous_song(self):
        return self.set_playback('previous')

    def set_power(self, power):
        self.__get('set power to %s' % power, 'main/setPower', params={'power': power})

    def turn_on(self):

        if self.is_on():
            return

        self.set_power('on')
        time.sleep(1)

        for iteration in range(100):
            if self.is_on():
                break
            time.sleep(0.1)

        if self.__default_volume is not None:
            self.set_volume(self.__default_volume)

    def turn_off(self):
        self.set_power('standby')

    def get_volume(self) -> int:
        max_volume = self.__get_max_volume()
        volume = int(self.get_status()['volume'])
        return int(round(100 * volume / max_volume))

    def __get_max_volume(self):
        if self.__max_volume is None:
            return int(self.get_status()['max_volume'])
        else:
            return self.__max_volume

    def is_mute(self):
        return bool(self.get_status()['mute'])

    def is_on(self):
        power = self.get_status()['power']
        return power == 'on'

    def is_stopped(self):
        playback = self.get_play_info()['playback']
        return playback == 'stop'

    def is_play(self):
        playback = self.get_play_info()['playback']
        return playback == 'play'

    def is_paused(self):
        playback = self.get_play_info()['playback']
        return playback == 'pause'

    def get_input(self):
        status = self.get_status()
        return status['input']
