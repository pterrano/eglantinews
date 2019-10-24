import os
import sys


def get_path(relative_path):
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), relative_path)
