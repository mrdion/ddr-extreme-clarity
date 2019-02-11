#!/bin/bash
#
# genmanifest.sh
#
# simple script that generates a JSON file describing the memory layout of a
# concatenated game-code payload.
#
# written by zanneth <root@zanneth.com>
#

{
    curoffset=0
    for binfile in $*; do
        filename=$(basename -- "$binfile")
        extension="${filename##*.}"
        filename="${filename%.*}"
        
        filesize=$(stat --printf="%s" ${binfile})
        printf "%s %s %s\n" ${filename} ${curoffset} ${filesize}
        
        curoffset=$((curoffset + filesize))
    done
} | column -J -n payloads -N name,offset,size
