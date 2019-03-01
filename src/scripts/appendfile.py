#!/usr/bin/env python3
#
# appendfile.py
#
# tool for appending resource files to DDR game images. this tool can append
# new resources that may be previously unknown to the shipping game code, or it
# can append and overwrite the file table entry for existing resource files in
# the game.
#
# this script currently cannot compress resource data using the same compression
# algorithm in the main game code, but if a file is already compressed the
# script can set the correct flag so that it is properly interpreted by the game
# at runtime.
#
# written by zanneth <root@zanneth.com>
#

import collections
import optparse
import os
import sys
from ddrutil import *
from enum import Enum

GAME_DAT_MAGICNUM = (0x24, b"PS-X EXE")
ISO9660_MAGICNUM  = (0x8001, b"\x43\x44\x30\x30\x31")

# -----------------------------------------------------------------------------

class GameImageType(Enum):
    UNKNOWN       = 0
    ISO9660_IMAGE = 1
    GAME_DAT      = 2

class GameDATFileSection:
    def __init__(self):
        self.offset = 0
        self.length = 0

# -----------------------------------------------------------------------------

def create_optparser():
    usage = "usage: %prog [options] iso_image_or_game_dat"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", 
                      "--name",
                      dest="name",
                      help="the name of the file to use when referring within DDR")
    parser.add_option("-f", 
                      "--file",
                      dest="file",
                      help="the path to the file to insert into the game binary",
                      metavar="FILE")
    parser.add_option("-c", 
                      "--compressed",
                      dest="compressed",
                      action="store_true",
                      default=False,
                      help="whether the input file should be treated as compressed by DDR")
    parser.add_option("-v", 
                      "--verbose",
                      dest="verbose",
                      action="store_true",
                      default=False,
                      help="verbose output")
    
    return parser

def print_err(msg):
    print(msg, file=sys.stderr)

def compute_game_image_type(path):
    with open(path, "rb") as game_image_file:
        game_image_file.seek(GAME_DAT_MAGICNUM[0], os.SEEK_SET)
        magicnum = game_image_file.read(len(GAME_DAT_MAGICNUM[1]))

        if magicnum == GAME_DAT_MAGICNUM[1]:
            return GameImageType.GAME_DAT
        
        game_image_file.seek(ISO9660_MAGICNUM[0], os.SEEK_SET)
        magicnum = game_image_file.read(len(ISO9660_MAGICNUM[1]))

        if magicnum == ISO9660_MAGICNUM[1]:
            return GameImageType.ISO9660_IMAGE
        
    return GameImageType.UNKNOWN

def get_game_dat_file_section(path):
    game_dat_file_section = None
    image_type = compute_game_image_type(path)

    if image_type == GameImageType.GAME_DAT:
        game_dat_file_section = GameDATFileSection()
        game_dat_file_section.offset = 0
        game_dat_file_section.length = os.stat(path).st_size
    elif image_type == GameImageType.ISO9660_IMAGE:
        # parse the ISO record tables and find GAME.DAT section
        iso = isoparser.parse(path)
        game_dat_record = None

        for child in iso.root.children:
            if child.name == bytes(GAME_DAT_FILENAME, "ascii"):
                game_dat_record = child
                break

        if game_dat_record == None:
            raise Exception("GAME.DAT not found in provided ISO image")
        
        # compute GAME.DAT file info
        gamedat_stream = game_dat_record.get_stream()
        game_dat_file_section = GameDATFileSection()
        game_dat_file_section.offset = gamedat_stream._offset
        game_dat_file_section.length = gamedat_stream._length

        # we're done with parsing the ISO
        iso.close()

    return game_dat_file_section

def find_free_space(file, target_size, begin_offset=0, end_offset=None):
    chunk_size = 1024
    token = 0xff
    crumb = None
    cur_offset = begin_offset

    file.seek(begin_offset, os.SEEK_SET)
    while end_offset == None or cur_offset < end_offset:
        cur_chunk_size = chunk_size
        if end_offset != None:
            cur_chunk_size = max(chunk_size, end_offset - cur_offset)
        
        chunk = file.read(max(chunk_size, end_offset - cur_offset))
        if len(chunk) == 0:
            break
        
        for b in chunk:
            if b == token:
                if crumb == None and FileTableEntry.offset_is_aligned(cur_offset - begin_offset):
                    crumb = cur_offset
                
                if crumb != None and cur_offset - crumb >= target_size:
                    return crumb
            else:
                crumb = None
            
            cur_offset += 1
    
    return None

def append_file(in_file_path, filename, compressed, game_image_path, verbose):
    success = False

    try:
        # verify game image path exists
        if not os.path.exists(game_image_path):
            raise FileNotFoundError("game image path does not exist")

        # verify a valid input file was provided
        if not os.path.exists(in_file_path):
            raise FileNotFoundError("input file \"%s\" does not exist" % in_file_path)
        
        # compute game dat file section info
        gamedat_file_section = get_game_dat_file_section(game_image_path)

        # make sure GAME.DAT file info is valid
        if gamedat_file_section == None:
            raise Exception("GAME.DAT has invalid offset from provided ISO image")
        
        if gamedat_file_section.length != GAME_DAT_SIZE:
            raise Exception("unexpected size for GAME.DAT file")
        
        if verbose:
            print("found valid GAME.DAT at offset %x length %x" %
                (gamedat_file_section.offset, gamedat_file_section.length))
        
        # start modifying the game image file
        with open(game_image_path, "rb+") as game_image_file:
            gamedat_offset = gamedat_file_section.offset
            gamedat_length = gamedat_file_section.length

            # read file table from game image
            game_image_file.seek(gamedat_offset + FILE_TABLE_OFFSET, os.SEEK_SET)
            filetable = FileTable(game_image_file)

            # compute space necessary to insert input file, and find available
            # free space in the game image file where we can put it
            in_file_size = os.stat(in_file_path).st_size
            free_space = find_free_space(game_image_file, 
                                         in_file_size,
                                         gamedat_offset,
                                         gamedat_offset + gamedat_length)
            
            # if there isn't a big enough free space contiguous region, we
            # can't do anything else
            if free_space == None:
                raise Exception("unable to find a large enough contiguous free space region in file")
            
            if verbose:
                print("input file size: %u bytes" % in_file_size)
                print("found free space at offset %x" % free_space)
            
            # insert the input file into the game image
            game_image_file.seek(free_space, os.SEEK_SET)
            with open(in_file_path, "rb") as in_file:
                game_image_file.write(in_file.read())
            
            # modify the file table to point to the new input file
            if filename == None:
                filename = os.path.basename(in_file_path)
            
            ft_entry = filetable.find_entry(filename)
            if ft_entry == None:
                ft_entry = FileTableEntry()
                ft_entry.filename_hash = hash_filename(filename)
                filetable.insert_entry(ft_entry)
                
                if verbose:
                    print("inserting new filetable entry: %s" % ft_entry)
            elif verbose:
                print("found existing filetable entry: %s" % ft_entry)
            
            ft_entry.offset = free_space - gamedat_offset
            ft_entry.length = in_file_size
            ft_entry.compression_flags = (0x1 if compressed else 0x0)
            
            # overwrite the file table
            if verbose:
                print("writing file to offset %x" % (gamedat_offset + FILE_TABLE_OFFSET))
            game_image_file.seek(gamedat_offset + FILE_TABLE_OFFSET, os.SEEK_SET)
            game_image_file.write(filetable.data())

            # finished
            success = True

    except Exception as e:
        print_err(str(e))
    
    return success

def main(argv):
    retval = 0
    parser = create_optparser()
    (options, args) = parser.parse_args(argv)

    if len(argv) == 1:
        parser.print_help()
    elif len(args) < 2:
        print_err("a path to DDR's GAME.DAT file or the DDR disk image is required.")
        retval = 1
    elif options.file == None:
        print_err("a path to a file to add is required.")
        retval = 1
    else:
        success = append_file(
            in_file_path=options.file,
            filename=options.name,
            compressed=options.compressed,
            game_image_path=args[1],
            verbose=options.verbose
        )
        retval = 0 if success else 1
    
    return retval

if __name__ == "__main__":
    sys.exit(main(sys.argv))