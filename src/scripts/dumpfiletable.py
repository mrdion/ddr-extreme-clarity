#!/usr/bin/env python3
#
# dumpfiletable.py
#
# reads a GAME.DAT file and dumps a human-readable representation of the image's
# file table to stdout.
#
# written by zanneth <root@zanneth.com>
#

import os
import struct
import sys
from pprint import pprint
from ddrutil import FileTable, FileTableEntry, FILE_TABLE_OFFSET

def scan(path):
    with open(path, "rb") as f:
        f.seek(FILE_TABLE_OFFSET)
        filetable = FileTable(f)

        for ft_entry in filetable.entries:
            print(ft_entry)

def main(argv):
    if len(argv) > 1:
        path = argv[1]
        scan(path)
    else:
        print("usage: %s <path to game.dat>" % argv[0])
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
