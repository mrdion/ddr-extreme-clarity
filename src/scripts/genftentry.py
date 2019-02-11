#!/usr/bin/env python3
#
# genftentry.py
#
# utility program that can generate the binary data of a filetable entry based
# on the provided options. useful for rapidly iterating on game image resource
# modification.
#
# written by zanneth <root@zanneth.com>
#

import optparse
import os
import sys
from ddrutil import *

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-n", 
                      "--name",
                      dest="name",
                      type="string",
                      help="the name of the file to use when referring within DDR")
    parser.add_option("-o", 
                      "--offset",
                      dest="offset",
                      type="int",
                      default=0,
                      help="the offset into the DAT file where the file's data will be stored")
    parser.add_option("-l", 
                      "--length",
                      dest="length",
                      type="int",
                      default=0,
                      help="the size of the file in bytes")
    parser.add_option("-c", 
                      "--compressed",
                      dest="compressed",
                      action="store_true",
                      default=False,
                      help="whether the file should be treated as compressed by DDR")
    
    (options, args) = parser.parse_args(argv)
    
    if options.name != None:
        entry = FileTableEntry()
        entry.filename_hash = hash_filename(options.name)
        entry.offset = options.offset
        entry.length = options.length
        entry.force_compressed = options.compressed

        entry_data = entry.data()

        if sys.stdout.isatty():
            print(entry_data)
        else:
            fp = os.fdopen(sys.stdout.fileno(), "wb")
            fp.write(entry_data)
    else:
        print("a file name is required")
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
