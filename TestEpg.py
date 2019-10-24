import logging

from eglantinews.epg.XmlTvService import XmlTvService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

epg_service = XmlTvService()

programs = epg_service.get_first_part_programs_by_channels()

for channel in sorted(programs.keys()):
    print("%s: %s - %s" % (programs[channel].title, programs[channel].start, programs[channel].stop))
