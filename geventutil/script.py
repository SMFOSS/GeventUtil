from gevent import monkey
from pkg_resources import load_entry_point
import sys


monkey.patch_all()


def main(args=None):
    if args is None:
        args = sys.argv
    pkg, ep = args[1].split(':')

    script = load_entry_point(pkg, 'console_scripts', ep)
    return script()
