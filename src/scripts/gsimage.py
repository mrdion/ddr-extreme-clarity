#!/usr/bin/env python3
import os
import sys
import struct

class GsIMAGE:
    def __init__(self):
        self.pmode = 0
        self.px = 0
        self.py = 0
        self.pw = 0
        self.ph = 0
        self.pixel = 0
        self.cx = 0
        self.cy = 0
        self.cw = 0
        self.ch = 0
        self.clut = 0
    
    def parse(self, bin):
        (
            self.pmode, 
            self.px,
            self.py,
            self.pw,
            self.ph,
            self.pixel,
            self.cx,
            self.cy,
            self.cw,
            self.ch,
            self.clut
        ) = struct.unpack("<IHHHHIHHHHI", bin)
    
    def __str__(self):
        return (
            "pmode  = {self.pmode}\n" +
            "px     = {self.px}\n" +
            "py     = {self.py}\n" +
            "pw     = {self.pw}\n" +
            "ph     = {self.ph}\n" +
            "pixel  = {self.pixel:#x}\n" +
            "cx     = {self.cx}\n" +
            "cy     = {self.cy}\n" +
            "cw     = {self.cw}\n" +
            "ch     = {self.ch}\n" +
            "clut   = {self.clut:#x}"
        ).format(self=self)

def main(argv):
    data = None
    if len(argv) < 2:
        data = sys.stdin.buffer.read()
    else:
        with open(argv[1], "rb") as f:
            data = f.read()
    
    img = GsIMAGE()
    img.parse(data)
    print(img)
    
    return 0

if (__name__ == "__main__"):
    sys.exit(main(sys.argv))
