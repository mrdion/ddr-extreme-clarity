#
# results_texcoord_hook.s
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 8006C9DC

lw      $t2, 0x64($sp)      # sp+0x64 = current judgment sprite index (1-based)
beq     $t2, 8, ddr_results_texcoord_fast_row
beq     $t2, 9, ddr_results_texcoord_slow_row
b       ddr_results_texcoord_break  # not our sprite. bail!!

ddr_results_texcoord_fast_row:
bne     $t3, 0xa8, ddr_results_texcoord_break   # bail if we're drawing a number

li      $t1, 0x60       # t1 = 96
sb      $t1, 0xc($a1)   # SPRT.tex_u0 = t1 (must be even)

li      $t1, 0x3f       # t1 = 63
sb      $t1, 0xd($a1)   # SPRT.tex_v0 = t1 (doesn't have to be even)

b       ddr_results_texcoord_break

ddr_results_texcoord_slow_row:
bne     $t3, 0xc0, ddr_results_texcoord_break   # bail if we're drawing a number

li      $t1, 0x60       # t1 = 96
sb      $t1, 0xc($a1)   # SPRT.tex_u0 = t1
sb      $t1, 0xd($a1)   # SPRT.tex_v0 = t1

ddr_results_texcoord_break:
jr      $ra             # jump to original location
