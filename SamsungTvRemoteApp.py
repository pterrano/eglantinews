import os.path as path
import sys

from samsungtv.SamsungTvKeys import SamsungKeys
from samsungtv.SamsungTvRemote import SamsungTvRemote

argv = sys.argv;

script = path.basename(argv.pop(0))


def checkArgs(expectedArgument):
    if len(argv) != expectedArgument:
        usage()


def usage():
    print("Usage : %s <mac> on" % script)
    print("Usage : %s <device> off" % script)
    print("Usage : %s <device> <keyCode>" % script)
    print()
    print("Key codes :")
    print("-----------")
    print()

    for code in SamsungKeys.keys:
        print('%-15s%-15s' % (code.get('code'),code.get('label')))

    exit(1)


if len(argv) < 2:
    usage();

device = argv.pop(0)

samsungTvRemote = SamsungTvRemote(device);


command = argv.pop(0)
argc = len(argv)

if command == 'on':
    checkArgs(0)
    samsungTvRemote.turnOn()
    exit(0)

if command == 'off':
    checkArgs(0)
    samsungTvRemote.turnOff()
    exit(0)

if command == 'status':
    checkArgs(0)
    if samsungTvRemote.isUp():
        print(device+' is up.')
        exit(0)
    else:
        print(device+' is down.')
        exit(1)



if command in map(lambda key:key.get('code'), SamsungKeys.keys):
    samsungTvRemote.sendKey(command)
    exit(0)
else:
    samsungTvRemote.sendKey(command)
