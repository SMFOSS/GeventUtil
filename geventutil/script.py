from gevent import monkey
from pkg_resources import load_entry_point
import sys


monkey.patch_all()


def main(args=None):
    if args is None:
        args = list(sys.argv)
    spec = args.pop(1)
    sys.argv = args
    pkg, ep = spec.split(':')

    script = load_entry_point(pkg, 'console_scripts', ep)
    return script()
