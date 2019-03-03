#!/usr/bin/env python3
import ddrutil
import os
import struct
import sys

RESULTS_ORIG_ADDRS_DICT = {
    0x80061858: 0x29420008,
    0x80060F7C: 0x24040008,
    0x80061020: 0x28840007,
    0x8006106C: 0x24060007,
    0x8006107C: 0x2D420006,
    0x80061108: 0x24020007,
    0x80061270: 0x24040007,
    0x80061278: 0x29420007,
    0x80061294: 0x29420007,
    0x800612A4: 0x29420007,
    0x8006132C: 0x29420007,
    0x80061640: 0x24420007,
    0x80061648: 0x24020007,
    0x80061650: 0x24020006,
    0x80061100: 0x24020006,
    0x80061264: 0x245EFFC7,
    0x80061630: 0x24420017
}

RESULTS_PATCHED_ADDRS_DICT = {
    0x80061858: 0x2942000A,
    0x80060F7C: 0x2404000A,
    0x80061020: 0x28840009,
    0x8006106C: 0x24060009,
    0x8006107C: 0x2D420009,
    0x80061108: 0x24020009,
    0x80061270: 0x24040009,
    0x80061278: 0x29420009,
    0x80061294: 0x29420009,
    0x800612A4: 0x29420009,
    0x8006132C: 0x29420009,
    0x80061640: 0x24420009,
    0x80061648: 0x24020009,
    0x80061650: 0x24020008,
    0x80061100: 0x24020008,
    0x80061264: 0x245EFFB1,
    0x80061630: 0x24420001
}

DST_ADDR_TMP_REG    = "$t1"
INSTR_DATA_TMP_REG  = "$t2"

RESULTS_PATCH_SUBROUTINE_NAME   = "ddr_results_patch_code"
RESULTS_UNPATCH_SUBROUTINE_NAME = "ddr_results_unpatch_code"

def generate_feature_switcher_subroutine(patch_dict):
    code = ""
    
    for text_addr, instr_data in patch_dict.items():
        code += "li %s, 0x%x\n" % (DST_ADDR_TMP_REG, text_addr)
        code += "li %s, 0x%x\n" % (INSTR_DATA_TMP_REG, instr_data)
        code += "sw %s, 0(%s)\n" % (INSTR_DATA_TMP_REG, DST_ADDR_TMP_REG)
        code += "\n"
    
    return code

def generate_feature_switcher():
    code = ""
    
    code += "%s:\n" % RESULTS_PATCH_SUBROUTINE_NAME
    code += generate_feature_switcher_subroutine(RESULTS_PATCHED_ADDRS_DICT)
    code += "\n"
    
    code += "%s:\n" % RESULTS_UNPATCH_SUBROUTINE_NAME
    code += generate_feature_switcher_subroutine(RESULTS_ORIG_ADDRS_DICT)
    code += "\n"
    
    return code

def main(argv):
    code = generate_feature_switcher()
    sys.stdout.write(code)
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
