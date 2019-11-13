import os.path as path
import sys

from samsungtv.SamsungTvKeys import SamsungKeys
from samsungtv.SamsungTvRemote import SamsungTvRemote

argv = sys.argv

samsung_tv_remote = SamsungTvRemote('tv')

script = path.basename(argv.pop(0))


def check_args(expected_argument: int):
    if len(argv) != expected_argument:
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
        print('%-15s%-15s' % (code.get('code'), code.get('label')))

    exit(1)


if len(argv) < 2:
    usage()

device = argv.pop(0)

command = argv.pop(0)
argc = len(argv)

if command == 'on':
    check_args(0)
    samsung_tv_remote.turn_on()
    exit(0)

if command == 'off':
    check_args(0)
    samsung_tv_remote.turn_off()
    exit(0)

if command == 'status':
    check_args(0)
    if samsung_tv_remote.is_up():
        print(device + ' is up.')
        exit(0)
    else:
        print(device + ' is down.')
        exit(1)

if command in map(lambda key: key.get('code'), SamsungKeys.keys):
    samsung_tv_remote.send_key(command)
    exit(0)
else:
    samsung_tv_remote.send_key(command)
