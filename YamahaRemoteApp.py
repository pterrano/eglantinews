import os.path as path
import sys

from musiccast.YamahaConsole import YamahaConsole

argv = sys.argv

script = path.basename(argv.pop(0))


def check_args(expected_argument):
    if len(argv) != expected_argument:
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
    usage()

device = argv.pop(0)

yamaha_console = YamahaConsole(device)

if len(argv) == 0:
    yamaha_console.sum_up()
    exit(0)

command = argv.pop(0)
argc = len(argv)

if command == 'on':
    check_args(0)
    yamaha_console.turn_on()
    yamaha_console.sum_up()
    exit(0)

if command == 'off':
    check_args(0)
    yamaha_console.turn_off()
    yamaha_console.sum_up()
    exit(0)

if command == 'play':
    if argc == 0:
        yamaha_console.play()
        yamaha_console.sum_up()
        exit(0)
    elif argc == 1:
        yamaha_console.play_track(int(argv[0]))
        yamaha_console.sum_up()
        exit(0)

if command == 'stop':
    check_args(0)
    yamaha_console.stop()
    yamaha_console.sum_up()
    exit(0)

if command == 'pause':
    check_args(0)
    yamaha_console.pause()
    yamaha_console.sum_up()
    exit(0)

if command == 'previous':
    check_args(0)
    yamaha_console.previous_song()
    yamaha_console.sum_up()
    exit(0)

if command == 'next':
    check_args(0)
    yamaha_console.next_song()
    yamaha_console.sum_up()
    exit(0)

if command == 'inputs':
    check_args(0)
    yamaha_console.show_inputs()
    exit(0)

if command == 'set-input':
    check_args(1)
    yamaha_console.set_input(argv[0])
    yamaha_console.show_inputs()
    exit(0)

if command == 'set-volume':
    check_args(1)
    yamaha_console.set_volume(int(argv[0]))
    yamaha_console.sum_up()
    exit(0)

if command == 'set-mute':
    check_args(1)
    yamaha_console.set_mute(argv[0])
    yamaha_console.sum_up()
    exit(0)

if command == 'dlna':
    if argc == 0:
        yamaha_console.prepare_input('server')
        yamaha_console.show_directory('/')
        exit(0)
    elif argc == 1:
        yamaha_console.prepare_input('server')
        yamaha_console.show_directory(argv[0])
        exit(0)
    elif argc == 2 and argv[1] == 'play':
        yamaha_console.prepare_input('server')
        yamaha_console.play_directory(argv[0])
        yamaha_console.sum_up()
    elif argc == 3 and argv[1] == 'play':
        yamaha_console.prepare_input('server')
        yamaha_console.play_file(argv[0], int(argv[2]))
        yamaha_console.sum_up()
        exit(0)

if command == 'deezer':
    if argc == 2 and argv[0] == 'search':
        result = yamaha_console.search(argv[1], 'tracks', command)
        print('listening "%s" ...' % result)
        exit(0)

usage()
