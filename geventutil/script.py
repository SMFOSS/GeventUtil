from gevent import monkey
from pkg_resources import load_entry_point
import sys

monkey.patch_all()

def main(args=None):
    """
    Main entry point for easily overpatching scripts for use with
    gevent
    """
    if args is None:
        args = list(sys.argv)
    if not args:
        print('Provide a speficification Package:scriptname and any arguments')
        sys.exit(1)
    spec = args.pop(1)
    sys.argv = args
    pkg, ep = spec.split(':')

    script = load_entry_point(pkg, 'console_scripts', ep)
    return script()
