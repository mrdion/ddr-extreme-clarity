#!/usr/bin/env python3
from add_clarity import *
from calcjmp import *

import ddrutil
import json
import os
import sys

def mamepatch(manifest_path):
    mame_cmds = []
    manifest = PayloadManifest(manifest_path)
    
    for patch_tuple in GAME_EXECUTABLE_PATCHES:
        mame_cmds.append("d@(%X)=%X;" % (patch_tuple[0], patch_tuple[1]))
    
    for hook in GAME_EXECUTABLE_HOOKS:
        payload_name = hook[0]
        dst_addr = hook[1]
        patch_type = hook[2]
        
        payload_item = manifest.get_payload_item(payload_name)
        
        if patch_type == PatchType.UNCONDITIONAL_JUMP:
            jmp_addr = USELESS_CODE_TEXT_ADDR + payload_item.offset
            jmp = calcjmp(jmp_addr, MIPSJumpType.UNCONDITIONAL)
            mame_cmds.append("d@(%X)=%X;" % (dst_addr, jmp))
        elif patch_type == PatchType.ADDRESS_TRANSPOSITION:
            off = USELESS_CODE_TEXT_ADDR + payload_item.offset
            mame_cmds.append("d@(%X)=%X;" % (dst_addr, off))
    
    return mame_cmds

def main(argv):
    retval = 0
    
    if len(argv) >= 2:
        mame_cmds = mamepatch(argv[1])
        
        for cmd in mame_cmds:
            print(cmd)
        
        retval = 0
    else:
        print("usage: %s <manifest-json-path>" % argv[0])
        retval = 1
    
    return retval
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
