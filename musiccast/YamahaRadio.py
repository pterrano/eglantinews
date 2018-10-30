import logging
import time
from xml.dom.minidom import parseString

import requests

from utils.SearchUtils import distance


class YamahaRadio:
    baseURL = 'http://radioyamaha.vtuner.com/setupapp/Yamaha/asp/Browsexml/'

    def __getTagByName(self, node, nodeName):
        nodes = node.getElementsByTagName(nodeName)
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None

    def __getTagValueByName(self, node, nodeName):

        tag = self.__getTagByName(node, nodeName)
        if tag == None:
            return None
        else:
            childNodes = tag.childNodes
            for textNode in childNodes:
                rc = []
                if textNode.nodeType == textNode.TEXT_NODE:
                    rc.append(textNode.nodeValue)
                return ''.join(rc)

    def __marshallRadios(self, xml: str):

        dom = parseString(xml)

        radios = {}

        for listOfItems in dom.childNodes:

            for item in listOfItems.getElementsByTagName('Item'):
                stationId = self.__getTagValueByName(item, 'StationId')
                stationName = self.__getTagValueByName(item, 'StationName')
                if stationId != None and stationName != None:
                    radios[stationName] = stationId

        return radios

    def __http(self, method: str, command: str, params=[]):

        url = self.baseURL + '/' + command

        t0 = time.perf_counter()

        if method == 'GET':
            result = requests.get(url=url, params=params).text
            logging.info('%s - %.1f - url=%s params=%s' % (method, time.perf_counter() - t0, url, params))
            return self.__marshallRadios(result)

        return None

    def search(self, radio):

        radios = self.__http('GET', 'search.asp', {'sSearchtype': '2', 'search': radio, 'dlang': 'fr', 'fver': 'W'})

        if radio in radios:
            return {'id': radios[radio], 'title': radio}
        else:

            radioNames = radios.keys()

            nearestRadio = None
            nearestDistance = float('inf')

            for currentRadio in radioNames:

                currentDistance = distance(currentRadio, radio)

                if currentDistance < nearestDistance:
                    nearestDistance = currentDistance
                    nearestRadio = currentRadio

            if nearestRadio != None:
                return {'id': radios[nearestRadio], 'title': nearestRadio}

            return None


yamahaRadio = YamahaRadio()

print(yamahaRadio.search('france bleu'))
