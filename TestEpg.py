import os
import sys

from eglantinews.ChannelsConfig import ChannelsConfig
from epg.XmlTvReader import XmlTvReader

channels = ChannelsConfig().get_channels()

xml = os.path.dirname(os.path.realpath(sys.argv[0])) + '/config/tvguide_tnt.xml'

reader = XmlTvReader(channels, xml)

programs = reader.get_current_programs_by_channels()

for channel in sorted(programs.keys()):
    print("%s: %s" % (channel, programs[channel]))



pass
