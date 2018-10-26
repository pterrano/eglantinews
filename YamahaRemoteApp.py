import sys
import os.path as path
import time

from musiccast.YamahaConsole import YamahaConsole;

argv = sys.argv;

script = path.basename(argv.pop(0))


def checkArgs(expectedArgument):
    if len(argv) != expectedArgument:
        usage()


def usage():
    print("Usage : %s <device>" % script)
    print("Usage : %s <device> on" % script)
    print("Usage : %s <device> off" % script)
    print("Usage : %s <device> play" % script)
    print("Usage : %s <device> play <trackNumber>" % script)
    print("Usage : %s <device> pause" % script)
    print("Usage : %s <device> stop" % script)
    print("Usage : %s <device> next" % script)
    print("Usage : %s <device> previous" % script)
    print("Usage : %s <device> inputs" % script)
    print("Usage : %s <device> set-input <input>" % script)
    print("Usage : %s <device> set-volume <volume>" % script)
    print("Usage : %s <device> set-mute [true|false]" % script)
    print("Usage : %s <device> dlna /path/to/nas/" % script)
    print("Usage : %s <device> dlna /path/to/nas/ play" % script)
    print("Usage : %s <device> dlna /path/to/nas/ play <trackNumber>" % script)
    print("Usage : %s <device> deezer search <pattern>" % script)
    exit(1)


if len(argv) < 1:
    usage();

device = argv.pop(0)

yamahaConsole = YamahaConsole(device);



if len(argv) == 0:
    yamahaConsole.sumUp();
    exit(0)

command = argv.pop(0)
argc = len(argv)

if command == 'on':
    checkArgs(0)
    yamahaConsole.turnOn()
    yamahaConsole.sumUp();
    exit(0)

if command == 'off':
    checkArgs(0)
    yamahaConsole.turnOff()
    yamahaConsole.sumUp();
    exit(0)

if command == 'play':
    if argc == 0:
        yamahaConsole.play()
        yamahaConsole.sumUp();
        exit(0)
    elif argc == 1:
        yamahaConsole.playTrack(int(argv[0]))
        yamahaConsole.sumUp();
        exit(0)


if command == 'stop':
    checkArgs(0)
    yamahaConsole.stop()
    yamahaConsole.sumUp();
    exit(0)

if command == 'pause':
    checkArgs(0)
    yamahaConsole.pause()
    yamahaConsole.sumUp();
    exit(0)

if command == 'previous':
    checkArgs(0)
    yamahaConsole.previousSong()
    yamahaConsole.sumUp();
    exit(0)

if command == 'next':
    checkArgs(0)
    yamahaConsole.nextSong()
    yamahaConsole.sumUp();
    exit(0)

if command == 'inputs':
    checkArgs(0)
    yamahaConsole.showInputs()
    exit(0)


if command == 'set-input':
    checkArgs(1)
    yamahaConsole.setInput(argv[0])
    yamahaConsole.showInputs()
    exit(0)

if command == 'set-volume':
    checkArgs(1)
    yamahaConsole.setVolume(int(argv[0]))
    yamahaConsole.sumUp();
    exit(0)

if command == 'set-mute':
    checkArgs(1)
    yamahaConsole.setMute(argv[0])
    yamahaConsole.sumUp();
    exit(0)

if command == 'dlna':
    if argc == 0:
        yamahaConsole.prepareInput('server')
        yamahaConsole.showDirectory('/')
        exit(0)
    elif argc == 1:
        yamahaConsole.prepareInput('server')
        yamahaConsole.showDirectory(argv[0])
        exit(0)
    elif argc == 2 and argv[1] == 'play':
        yamahaConsole.prepareInput('server')
        yamahaConsole.playDirectory(argv[0])
        yamahaConsole.sumUp();
    elif argc == 3 and argv[1] == 'play':
        yamahaConsole.prepareInput('server')
        yamahaConsole.playFile(argv[0], int(argv[2]))
        yamahaConsole.sumUp();
        exit(0)

if command == 'deezer':
    if argc == 2 and argv[0] == 'search':
        result=yamahaConsole.search(argv[1], 'tracks', command)
        print ('listening "%s" ...' % result)
        exit(0)


usage()


