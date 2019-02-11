#!/usr/bin/env python3
#
# ddraddrconv.py
#
# converts virtual addresses referenced by the DDR game executable's .text
# section into GAME.DAT file offsets.
#
# adopted from neko68k's DDRAddrCalc windows program.
#
# written by zanneth <root@zanneth.com>
#

import sys
from ddrutil import exe_text_addr_to_game_dat_offset

def main(argv):
    if len(argv) < 2:
        print("usage: %s <text-section-addr>" % argv[0])
        print("compute the offset into a GAME.DAT file based on a virtual address from the game executable's .text section")
    else:
        vaddr = int(argv[1], 0)
        game_dat_offset = exe_text_addr_to_game_dat_offset(vaddr)
        print(hex(game_dat_offset))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
