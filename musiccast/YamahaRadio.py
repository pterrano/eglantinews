import logging
import time
from xml.dom.minidom import parseString

import requests

from utils.SearchUtils import distance


class YamahaRadio:
    BASE_URL = 'http://radioyamaha.vtuner.com/setupapp/Yamaha/asp/Browsexml/'

    def __get_tag_by_name(self, node, node_name):
        nodes = node.getElementsByTagName(node_name)
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None

    def __get_tag_value_by_name(self, node, node_name):

        tag = self.__get_tag_by_name(node, node_name)
        if tag is None:
            return None
        else:
            child_nodes = tag.childNodes
            for text_node in child_nodes:
                rc = []
                if text_node.nodeType == text_node.TEXT_NODE:
                    rc.append(text_node.nodeValue)
                return ''.join(rc)

    def __marshall_radios(self, xml: str):

        dom = parseString(xml)

        radios = {}

        for list_of_items in dom.childNodes:

            for item in list_of_items.getElementsByTagName('Item'):
                station_id = self.__get_tag_value_by_name(item, 'StationId')
                station_name = self.__get_tag_value_by_name(item, 'StationName')
                if station_id is not None and station_name is not None:
                    radios[station_name] = station_id

        return radios

    def __http(self, method: str, command: str, params={}):

        url = self.BASE_URL + '/' + command

        t0 = time.perf_counter()

        if method == 'GET':
            result = requests.get(url=url, params=params).text
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            return self.__marshall_radios(result)

        return None

    def search(self, radio):

        radios = self.__http('GET', 'search.asp', {'sSearchtype': '2', 'search': radio, 'dlang': 'fr', 'fver': 'W'})

        if radio in radios:
            return {'id': radios[radio], 'title': radio}
        else:

            radio_names = radios.keys()

            nearest_radio: str = None
            nearest_distance = float('inf')

            for current_radio in radio_names:

                current_distance = distance(current_radio, radio)

                if current_distance < nearest_distance:
                    nearest_distance = current_distance
                    nearest_radio = current_radio

            if nearest_radio is not None:
                return {'id': radios[nearest_radio], 'title': nearest_radio}

            return None
