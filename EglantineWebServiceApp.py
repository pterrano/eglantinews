from eglantinews.EglantineWebService import EglantineWebService;
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s - [%(levelname)s] - %(message)s')

ws = EglantineWebService()
ws.run()
