#!/usr/bin/env python3
#
# dumpsym.py
#
# utility program that can dump the binary code from an ELF file matching a
# given symbol name.
#
# written by zanneth <root@zanneth.com>
#

import optparse
import os
import sys

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from pprint import pprint

def print_err(msg):
    print(msg, file=sys.stderr)

def dumpsym(elf_path, sym_name, output_path):
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
        syms_matching_name = sym_table.get_symbol_by_name(sym_name)
        if syms_matching_name and len(syms_matching_name) > 0:
            matching_sym = syms_matching_name[0]
        
        if not matching_sym:
            print_err("no symbol matching '%s' was found" % sym_name)
            return False
        
        # calculate the symbol's size and offset into the file
        sym_size = matching_sym.entry.st_size
        sym_file_offset = code_file_off + matching_sym.entry.st_value - code_img_addr
        print(vars(matching_sym.entry))
        print("found symbol: %s (size = 0x%lx, file offset = 0x%lx)" % (
            matching_sym.name,
            sym_size,
            sym_file_offset
        ))
        
        # write just the symbol's data to a new file
        with open(output_path, "wb") as outf:
            f.seek(sym_file_offset)
            outf.write(f.read(sym_size))
    
    return True
        
def main(argv):
    cli_parser = optparse.OptionParser()
    cli_parser.add_option("-o", dest="output_path")
    cli_parser.add_option("-s", dest="sym_name")
    (options, args) = cli_parser.parse_args()
    
    if options.output_path != None and options.sym_name != None and len(args) > 0:
        dumpsym(args[0], options.sym_name, options.output_path)
    else:
        print("Usage: %s -o <output_path> -s <sym_name> elf_file" % sys.argv[0])
    
    return 0

if __name__ == "__main__":
    main(sys.argv)
