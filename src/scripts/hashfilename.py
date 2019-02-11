#!/usr/bin/env python3
#
# hashfilename.py
#
# simple script that generate a filename hash for the provided filename and
# writes the result to stdout. this hash is used by the game code to compute an
# offset into the global filetable.
#
# written by zanneth <root@zanneth.com>
#

import sys
from ddrutil import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        h = hash_filename(sys.argv[1])
        print("0x%x" % h)
    else:
        print("usage: %s filename" % sys.argv[0])
