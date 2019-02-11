#!/usr/bin/env python3
#
# ddrutil.py
#
# common module which contains a bunch of utility code for modifying and
# introspecting DDR's game image.
#
# written by zanneth <root@zanneth.com>
#

import ctypes
import io
import isoparser
import os
import struct
import sys

FILE_TABLE_OFFSET           = 0xfe4000
GAME_DAT_FILENAME           = "GAME.DAT"
GAME_DAT_SIZE               = 0x1000000
GAME_DAT_BOOTROM_START      = 0x80800
GAME_EXE_TEXT_SECTION_START = 0x80010000

class FileTableEntry:
    def __init__(self, bytes=None):
        if bytes != None:
            self._arr = struct.unpack("<LLLL", bytes)

            if self.is_valid():
                self.filename_hash = self._arr[0]
                self.offset = (self._arr[1] << 11)
                self.length = self._arr[3]
                self.compression_flags = self._arr[2]
                self.entry_offset = 0
    
    def __str__(self):
        return "{filename_hash = 0x%x, offset = 0x%x, length = 0x%x, compressed = %d}" % (
            self.filename_hash,
            self.offset,
            self.length,
            self.is_compressed()
        )
    
    def data(self):
        assert(FileTableEntry.offset_is_aligned(self.offset))
        return struct.pack("<LLLL",
            self.filename_hash,
            (self.offset >> 11),
            self.compression_flags,
            self.length
        )
    
    def is_compressed(self):
        return (self.compression_flags == 1)
    
    def is_valid(self):
        return (
            not self.is_end() and
            self._arr != tuple([0x0] * 4)
        )
    
    @staticmethod
    def offset_is_aligned(offset):
        return ((offset & 0x7ff) == 0)
    
    def is_end(self):
        return (self._arr == tuple([0xffffffff] * 4))

class FileTable:
    def __init__(self, stream):
        self.entries = []

        while True:
            ft_file_offset = stream.tell()
            ft_entry_bytes = stream.read(16)
            if not ft_entry_bytes:
                break
            
            ft_entry = FileTableEntry(ft_entry_bytes)
            if ft_entry.is_valid():
                ft_entry.entry_offset = ft_file_offset
                self.entries.append(ft_entry)
            else:
                break
    
    def data(self):
        data = bytearray()
        

        for entry in self.entries:
            data += entry.data()
        
        return data

    def insert_entry(self, new_entry):
        filename_hash = new_entry.filename_hash

        for (idx, entry) in enumerate(self.entries):
            if entry.filename_hash >= filename_hash:
                self.entries.insert(idx, new_entry)
                break
    
    def get_last_entry(self):
        last_entry = None

        for entry in self.entries:
            if last_entry == None or entry.entry_offset > last_entry.entry_offset:
                last_entry = entry
        
        return last_entry
    
    def find_entry(self, filename):
        found_entry = None
        filename_hash = hash_filename(filename)

        for entry in self.entries:
            if entry.filename_hash == filename_hash:
                found_entry = entry
                break
        
        return found_entry
                
def int32(val):
    return ctypes.c_int32(val).value

def uint32(val):
    return ctypes.c_uint32(val).value

def decompress(data):
    in_stream = io.BytesIO(data)
    out_data = bytearray()
    xloop = False
    flags = 0x0

    def read_byte(stream):
        b = stream.read(1)
        if len(b) == 1:
            return b[0]
        else:
            return None
    
    def append_byte(barray, b):
        barray += bytes([b])

    while True:
        flags >>= 1
        if (flags & 0x100) == 0:
            b = read_byte(in_stream)
            if b == None:
                break
            
            flags = b | 0xff00
        
        c = read_byte(in_stream)
        if (flags & 0x1) == 0:
            append_byte(out_data, c)
            continue
        
        if (c & 0x80) == 0:
            i = read_byte(in_stream)
            i |= (c & 0x3) << 8
            j = (c >> 2) + 2
            xloop = True
        
        if not xloop:
            if (c & 0x40) == 0:
                i = (c & 0xf) + 1
                j = (c >> 4) - 7
                xloop = True
        
        if xloop:
            xloop = False
            while j >= 0:
                if len(out_data) - i > 0 and len(out_data) - i < len(out_data):
                    append_byte(out_data, out_data[len(out_data) - i])
                else:
                    append_byte(out_data, 0x00)
                
                j -= 1
            
            continue
        
        j = c - 0xb9
        eof = False
        while j >= 0:
            b = read_byte(in_stream)
            if b == None:
                eof = True
                break

            append_byte(out_data, b)
            j -= 1
        
        if eof:
            break
    
    return out_data

def hash_filename(filename):
    t4 = 0x4C11DB7
    t3 = 0
    t5 = 0 # filename cur ptr
    t0 = filename[0]

    if t0 != None:
        v0 = t5 + 1

        # loc_8002AC0C
        while True:
            if t0 == None:
                break

            a3 = 0
            t2 = filename[v0] if v0 < len(filename) else None
            t1 = v0 + 1

            # loc_8002AC18
            while True:
                a0 = (t3 << 1) & 0xffffffff
                v0 = uint32(int32(ord(t0)) >> int32(a3))
                v0 &= 1
                a0 |= v0
                v1 = uint32(int32(t3) >> 31)
                v1 &= t4
                a3 += 1
                v0 = (a3 < 6)

                t3 = uint32(int32(a0) ^ int32(v1))
                if v0 != 0:
                    continue # loc_8002AC18
                else:
                    t0 = t2

                    if t0 != 0:
                        v0 = t1
                        break # loc_8002AC0C
        
    # loc_8002AC4C
    return t3

def exe_text_addr_to_game_dat_offset(text_addr):
    return text_addr + GAME_DAT_BOOTROM_START - GAME_EXE_TEXT_SECTION_START
