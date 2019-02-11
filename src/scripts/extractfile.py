#!/usr/bin/env python3
#
# extractfile.py
#
# extract any file from a DDR game image according to its virtual filesystem
# path (e.g. "data/gpct/dance/gmob_25.cmt"). this script will also decompress
# the file's contents if the filetable entry indicates that the requested file
# is compressed.
#
# written by zanneth <root@zanneth.com>
#

from ddrutil import *
import os
import sys

def print_err(msg):
    print(msg, file=sys.stderr)

def extract_file(filename, game_dat_path):
    success = True

    with open(game_dat_path, "rb") as game_dat_file:
        game_dat_file.seek(FILE_TABLE_OFFSET)
        filetable = FileTable(game_dat_file)
        filename_hash = hash_filename(filename)

        target_entry = None
        for ft_entry in filetable.entries:
            if ft_entry.filename_hash == filename_hash:
                target_entry = ft_entry
                break
        
        if target_entry:
            game_dat_file.seek(ft_entry.offset, os.SEEK_SET)
            file_data = game_dat_file.read(target_entry.length)

            if target_entry.is_compressed():
                file_data = decompress(file_data)

            output_filename = os.path.basename(filename)
            output_file_path = os.path.join(os.getcwd(), output_filename)
            with open(output_file_path, "wb") as output_file:
                output_file.write(file_data)
                success = True
        else:
            print_err("filename not found: %s" % filename)
            success = False
    
    return success

def main(argv):
    retval = 0

    if len(argv) > 2:
        filename = argv[1]
        game_dat_path = argv[2]

        success = extract_file(filename, game_dat_path)
        retval = 0 if success else 1
    else:
        print("usage: %s filename path_to_game_dat" % argv[0])
    
    return retval

if __name__ == "__main__":
    sys.exit(main(sys.argv))
