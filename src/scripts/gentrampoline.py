#!/usr/bin/env python3
#
# gentrampoline.py
#
# generate trampoline shellcode that can be injected into a live game
# executable. sets up a proper stack according to the MIPS32 ABI and jumps to
# any virtual memory location.
#
# written by zanneth <root@zanneth.com>
#

import binascii
import optparse
import os
import struct
import sys

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from pprint import pprint

"""
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $t9, 8($sp)
sw $gp, 12($sp)

li $t9, 0xdeadbeef
jal $t9

lw $ra, 4($sp)
lw $t9, 8($sp)
lw $gp, 12($sp)
addiu $sp, $sp, 16

jr $ra
"""
TRAMPOLINE_SHELLCODE = b"\xF0\xFF\xBD\x27\x04\x00\xBF\xAF\x08\x00\xB9\xAF\x0C\x00\xBC\xAF\xAD\xDE\x19\x3C\xEF\xBE\x39\x37\x09\xF8\x20\x03\x00\x00\x00\x00\x04\x00\xBF\x8F\x08\x00\xB9\x8F\x0C\x00\xBC\x8F\x08\x00\xE0\x03\x10\x00\xBD\x27"

def print_err(msg):
    print(msg, file=sys.stderr)

def calcjmp(dst):
    return ((dst >> 2) & 0x7FFFFFF) | 0xC000000

def gentrampoline(elf_path, target_vaddr, entry_sym_name, output_path):
    with open(elf_path, "rb") as f:
        elf_file = ELFFile(f)
        if not elf_file:
            print_err("failed to parse ELF file")
            return False
        
        matching_sym = None
        sym_table = None
        
        # read info about the main code section
        code_section = elf_file.get_section_by_name(".text")
        if not code_section:
            print_err("failed to find code section")
            return False
        
        code_file_off = code_section.header.sh_offset
        code_img_addr = code_section.header.sh_addr
        
        # get the symbol table so that we can find what we're looking for
        for section in elf_file.iter_sections():
            if isinstance(section, SymbolTableSection):
                sym_table = section
                break
        
        if not sym_table:
            print_err("failed to find symbol table")
            return False
        
        # find our symbol using the table
        syms_matching_name = sym_table.get_symbol_by_name(entry_sym_name)
        if syms_matching_name and len(syms_matching_name) > 0:
            matching_sym = syms_matching_name[0]
        
        if not matching_sym:
            print_err("no symbol matching '%s' was found" % entry_sym_name)
            return False
        
        # calculate the symbol's size and offset into the file
        sym_size = matching_sym.entry.st_size
        sym_file_offset = code_file_off + matching_sym.entry.st_value - code_img_addr
        
        sym_vaddr = target_vaddr + sym_file_offset
        sym_addr_lower = (sym_vaddr & 0xFFFF)
        sym_addr_upper = (sym_vaddr & 0xFFFF0000) >> 16
        
        shellcode = bytearray(TRAMPOLINE_SHELLCODE)
        struct.pack_into("<H", shellcode, 0x10, sym_addr_upper)
        struct.pack_into("<H", shellcode, 0x14, sym_addr_lower)
        
        # write the shellcode binary to the output file
        with open(output_path, "wb") as outf:
            outf.write(shellcode)
    
    return True
        
def main(argv):
    cli_parser = optparse.OptionParser()
    cli_parser.add_option("-a", dest="target_vaddr", type="int")
    cli_parser.add_option("-o", dest="output_path")
    cli_parser.add_option("-s", dest="entry_sym_name")
    (options, args) = cli_parser.parse_args()
    
    if (options.target_vaddr != None and
            options.output_path != None and 
            options.entry_sym_name != None and 
            len(args) > 0):
        gentrampoline(args[0], options.target_vaddr, options.entry_sym_name, options.output_path)
    else:
        print("Usage: %s -a <target_vaddr> -s <entry_sym_name> -o <output_path> elf_file" % sys.argv[0])
    
    return 0

if __name__ == "__main__":
    main(sys.argv)
