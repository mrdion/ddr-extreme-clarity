#!/usr/bin/python3
#
# calcjmp.py
#
# simple script that does the math to assemble a long-jump instruction which can
# be injected into game code.
#
# supports unconditional jumps (J) and jump-and-link instructions (JAL) for MIPS
# 32-bit machine code.
#
# written by zanneth <root@zanneth.com>
#

import sys
from enum import Enum

class MIPSJumpType(Enum):
    UNCONDITIONAL = 0x8000000
    JUMP_AND_LINK = 0xC000000

def calcjmp(dst, jmp_type):
    return ((dst >> 2) & 0x7FFFFFF) | jmp_type.value

def main(argv):
    if len(argv) > 1:
        jmp = calcjmp(int(argv[1], 16), MIPSJumpType.UNCONDITIONAL)
        print(hex(jmp))
    else:
        print("usage: %s dst_addr" % argv[0])
    
    return 0

if __name__ == "__main__":
    main(sys.argv)
