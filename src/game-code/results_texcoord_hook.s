#
# results_texcoord_hook.s
#
# hook into the drawing code that configures each sprite for the score entry
# list (e.g. "032", "MARVELOUS", "049", "PERFECT"). the main results screen code
# uses arithmetic to draw the next icon in the spritesheet based on the index of
# which one we are drawing. since we had to place our "FAST" and "SLOW" graphics
# in arbitrary places within the spritesheet, we have to correct the texture
# coordinates for these particular sprites before they are sent to the draw
# graph.
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 8006C9DC

li      $t1, 0x800F0048     # load ptr to global game mode
lb      $t2, 0($t1)         # load game mode into $t2
bne     $t2, 0, ddr_results_texcoord_break # don't do anything if we're not in normal mode

lhu     $t3, 0xe($a1)       # t3 = CLUT ID
bne     $t3, 0xfec0, ddr_results_texcoord_break # not our sprite. bail!!

lw      $t2, 0x64($sp)      # sp+0x64 = current judgment sprite index (1-based)
beq     $t2, 8, ddr_results_texcoord_fast_row
beq     $t2, 9, ddr_results_texcoord_slow_row
b       ddr_results_texcoord_break  # not our sprite. bail!!

ddr_results_texcoord_fast_row:
li      $t1, 0x60       # t1 = 96
sb      $t1, 0xc($a1)   # SPRT.tex_u0 = t1 (must be even)

li      $t1, 0x3f       # t1 = 63
sb      $t1, 0xd($a1)   # SPRT.tex_v0 = t1 (doesn't have to be even)

li      $t1, 0x15       # t1 = 21
sb      $t1, 0x12($a1)  # SPRT.h = t1

b       ddr_results_texcoord_break

ddr_results_texcoord_slow_row:
li      $t1, 0x60       # t1 = 96
sb      $t1, 0xc($a1)   # SPRT.tex_u0 = t1
sb      $t1, 0xd($a1)   # SPRT.tex_v0 = t1

ddr_results_texcoord_break:
jr      $ra             # jump to original location
