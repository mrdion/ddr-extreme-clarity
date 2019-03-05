#!/usr/bin/env python3
#
# add_clarity.py
#
# mega-script that combines functionality from all of the other modules to patch
# a live game image.
#
# performs three distinct steps to produce a final patched image:
# 1. overwrites the filetable and inserts the data for the replacement
#    spritesheet used during gameplay.
# 2. injects a giant payload containing all of the game code required for the
#    feature. this must already be compiled from the custom-written native game 
#    code located in the "game-code" source directory.
# 3. patches a couple of instructions in the game's executable to jump to the
#    hooks located in the payload.
#
# written by zanneth <root@zanneth.com>
#

import appendfile
import calcjmp
import ddrutil
import json
import optparse
import os
import struct
import sys
from enum import Enum

class PatchType(Enum):
    UNCONDITIONAL_JUMP      = 1
    ADDRESS_TRANSPOSITION   = 2

JUDGMENT_SPRITESHEET_GAME_FILENAME  = "data/gpct/dance/gmob_25.cmt"
RESULTS_SPRITESHEET_GAME_FILENAME   = "data/gpct/result/rslob_25.cmt"
RESULTS_SPRITESHEET_DST_OFFSET      = 0x68800 # hardcoded in results_main_hook.s
USELESS_CODE_TEXT_ADDR              = 0x8003B268 # overwrite the DIP SWITCH CHECK
GAME_EXECUTABLE_PATCHES             = [
#   payload name                destination  type
    ("init_player_stats_hook",  0x80025DF0,  PatchType.UNCONDITIONAL_JUMP),
    ("reset_player_stats_hook", 0x80076490,  PatchType.UNCONDITIONAL_JUMP),
    ("checkstep_hook",          0x80077618,  PatchType.UNCONDITIONAL_JUMP),
    ("texcoord_hook",           0x8005A5A4,  PatchType.UNCONDITIONAL_JUMP),
    ("vertex_hook",             0x8005B6FC,  PatchType.UNCONDITIONAL_JUMP),
    ("results_load_hook",       0x80061154,  PatchType.UNCONDITIONAL_JUMP),
    ("results_texcoord_hook",   0x8006C9DC,  PatchType.UNCONDITIONAL_JUMP),
    ("results_main_hook",       0x800D8B70,  PatchType.ADDRESS_TRANSPOSITION),
]

# ------------------------------------------------------------------------------

class PayloadItem:
    def __init__(self, name, offset, size):
        self.name = name
        self.offset = offset
        self.size = size

class PayloadManifest:
    def __init__(self, json_path):
        self.items = []
        
        with open(json_path, "rb") as json_file:
            json_doc = json.load(json_file)
        
        json_payloads = json_doc["payloads"]
        for json_payload in json_payloads:
            name = json_payload["name"]
            offset = int(json_payload["offset"])
            size = int(json_payload["size"])
            
            payload_item = PayloadItem(name, offset, size)
            self.items.append(payload_item)
    
    def get_payload_item(self, name):
        payload_item = None
        
        for item in self.items:
            if item.name == name:
                payload_item = item
                break
        
        return payload_item

class HookTarget:
    def __init__(self, payload_item, hook_text_addr, patch_type):
        self.payload_item = payload_item
        self.hook_text_addr = hook_text_addr
        self.patch_type = patch_type

# ------------------------------------------------------------------------------

def create_optparser():
    usage = "usage: %prog [options] game-dat-file"
    parser = optparse.OptionParser(usage)
    parser.add_option("-j", 
                      "--judgment-spritesheet",
                      dest="judgment_spritesheet_path",
                      help="the path to the replacement 'gmob' sprite TIM file",
                      metavar="FILE")
    parser.add_option("-r", 
                      "--results-spritesheet",
                      dest="results_spritesheet_path",
                      help="the path to the replacement 'rslob' sprite TIM file",
                      metavar="FILE")
    parser.add_option("-p", 
                      "--payload",
                      dest="payload_path",
                      help="the path to the compiled shellcode",
                      metavar="FILE")
    parser.add_option("-m", 
                      "--manifest",
                      dest="manifest_path",
                      help="the path to the manifest file describing the shellcode payload",
                      metavar="FILE")
    
    return parser

def print_err(msg):
    print(msg, file=sys.stderr)

def insert_shellcode(payload_path, dst_offset, game_dat_file_path):
    with open(game_dat_file_path, "rb+") as game_dat_file:
        game_dat_file.seek(dst_offset, os.SEEK_SET)
        
        with open(payload_path, "rb") as payload_file:
            game_dat_file.write(payload_file.read())
    
    return True

def patch_game_executable(payload_manifest_path, shellcode_text_addr, game_dat_file_path):
    success = False
    
    try:
        # read manifest file
        manifest = PayloadManifest(payload_manifest_path)
        
        # create hook targets for each payload item
        hook_targets = []
        for patch_tuple in GAME_EXECUTABLE_PATCHES:
            payload_item = manifest.get_payload_item(patch_tuple[0])
            
            if payload_item == None:
                raise Exception("required shellcode \"%s\" not found in payload" % patch_tuple[0])
            
            hook_target = HookTarget(payload_item, patch_tuple[1], patch_tuple[2])
            hook_targets.append(hook_target)
        
        # open GAME.DAT file and start patching
        with open(game_dat_file_path, "rb+") as game_dat_file:
            for hook_target in hook_targets:
                payload_text_addr = shellcode_text_addr + hook_target.payload_item.offset
                hook_dst_offset = ddrutil.exe_text_addr_to_game_dat_offset(hook_target.hook_text_addr)
                
                if hook_target.patch_type == PatchType.UNCONDITIONAL_JUMP:
                    jump_instruction_word = calcjmp.calcjmp(payload_text_addr, calcjmp.MIPSJumpType.UNCONDITIONAL)
                    jump_instruction_data = struct.pack("<I", jump_instruction_word)
                    
                    game_dat_file.seek(hook_dst_offset, os.SEEK_SET)
                    game_dat_file.write(jump_instruction_data)
                elif hook_target.patch_type == PatchType.ADDRESS_TRANSPOSITION:
                    addr_data = struct.pack("<I", payload_text_addr)
                    game_dat_file.seek(hook_dst_offset, os.SEEK_SET)
                    game_dat_file.write(addr_data)
        
    except Exception as e:
        print_err(str(e))
    
    return True

def add_clarity(judgment_spritesheet_path,
                results_spritesheet_path,
                payload_path,
                manifest_path,
                game_dat_file_path):
    success = False
    
    try:
        # make sure GAME.DAT file exists
        if not os.path.exists(game_dat_file_path):
            raise FileNotFoundError("GAME.DAT file \"%s\" does not exist" % game_dat_file_path)
        
        # make sure replacement judgment spritesheet file exists
        if not os.path.exists(judgment_spritesheet_path):
            raise FileNotFoundError("spritesheet file \"%s\" does not exist" % judgment_spritesheet_path)
        
        # make sure replacement results spritesheet file exists
        if not os.path.exists(results_spritesheet_path):
            raise FileNotFoundError("spritesheet file \"%s\" does not exist" % results_spritesheet_path)
        
        # make sure shellcode file exists
        if not os.path.exists(payload_path):
            raise FileNotFoundError("payload file \"%s\" does not exist" % payload_path)
        
        # make sure manifest file exists
        if not os.path.exists(manifest_path):
            raise FileNotFoundError("manifest file \"%s\" does not exist" % manifest_path)
        
        # first append the replacement results spritesheet to the game binary
        # and overwrite the existing filetable entry
        # it must be done at a specific offset because we hard-coded this
        # address in the game code for results_main_hook.s. the appendfile
        # module will make sure that the free space destination is valid before
        # writing the file data.
        print("- replacing results screen spritesheet in game binary...")
        results_sprt_replace_success = appendfile.append_file(
            in_file_path=results_spritesheet_path,
            filename=RESULTS_SPRITESHEET_GAME_FILENAME,
            compressed=False,
            dst_offset=RESULTS_SPRITESHEET_DST_OFFSET,
            game_image_path=game_dat_file_path
        )
        if not results_sprt_replace_success:
            raise Exception("*** failed to replace results screen spritesheet in game binary.")
        
        # next, append the replacement judgment spritesheet to the game binary
        # we don't care where this file is placed, so let the appendfile module
        # find the free space automatically.
        print("- replacing judgment spritesheet in game binary...")
        judgment_sprt_replace_success = appendfile.append_file(
            in_file_path=judgment_spritesheet_path,
            filename=JUDGMENT_SPRITESHEET_GAME_FILENAME,
            compressed=False,
            game_image_path=game_dat_file_path
        )
        if not judgment_sprt_replace_success:
            raise Exception("*** failed to replace judgment spritesheet in game binary.")
        
        # next, insert the feature's shellcode into the binary
        print("- inserting shellcode into game executable...")
        shellcode_dst_offset = ddrutil.exe_text_addr_to_game_dat_offset(USELESS_CODE_TEXT_ADDR)
        insert_shellcode_success = insert_shellcode(payload_path, shellcode_dst_offset, game_dat_file_path)
        if not insert_shellcode_success:
            raise Exception("*** failed to insert shellcode into game executable.")
        
        # finally, patch the few places in the game's executable that we need in
        # order for the feature to work
        print("- patching game executable...")
        patch_success = patch_game_executable(manifest_path, USELESS_CODE_TEXT_ADDR, game_dat_file_path)
        if not patch_success:
            raise Exception("*** failed to patch game executable.")
        
        # finished
        print("successfully patched %s" % game_dat_file_path)
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
        print_err("a path to DDR's GAME.DAT file is required.")
        retval = 1
    elif options.judgment_spritesheet_path == None:
        print_err("a path to the replacement judgment UI spritesheet is required.")
        retval = 1
    elif options.results_spritesheet_path == None:
        print_err("a path to the replacement results screen UI spritesheet is required.")
        retval = 1
    elif options.payload_path == None:
        print_err("a path to the compiled shellcode binary is required.")
        retval = 1
    elif options.manifest_path == None:
        print_err("a path to the shellcode's manifest file is required.")
        retval = 1
    else:
        success = add_clarity(
            judgment_spritesheet_path=options.judgment_spritesheet_path,
            results_spritesheet_path=options.results_spritesheet_path,
            payload_path=options.payload_path,
            manifest_path=options.manifest_path,
            game_dat_file_path=args[1]
        )
        
        retval = 0 if success else 1
    
    return retval

if __name__ == "__main__":
    sys.exit(main(sys.argv))
