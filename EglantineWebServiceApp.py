import logging

from eglantinews.EglantineWebService import EglantineWebService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

ws = EglantineWebService()
ws.run()
