#
# texcoord_hook.s
#
# hooks into the end of the function that computes necessary texture coordinate
# information for all sprites used in the gameplay screen.
#
# this code checks to make sure that the sprite being modified is the one that
# pertains to the combo indicator using the sprite's texture page and uv values.
# once it is confirmed that we are modifying the right sprite, the code loads
# values that were previously stored by another hook (checkstep_hook) to
# determine if the player stepped early or late. depending on the timing of the
# player's step, the code will overwrite texture coordinates to use the custom-
# designed sprites that were augmented as part of the existing gameplay
# spritesheet (gmob_25).
#
# written by zanneth <root@zanneth.com>
#

# struct ddr_player_clarity_stats_t
# {
#     uint32_t chart_step_time;         [00 32-bits]
#     uint32_t player_step_time;        [04 32-bits]
#     uint32_t fast_count;              [08 32-bits]
#     uint32_t total_fast_count;        [12 32-bits]
#     uint32_t slow_count;              [16 32-bits]
#     uint32_t total_slow_count;        [20 32-bits]
# }
#
# total size = 24 bytes
# one instance per player

# jump to me from 0x8005A5A4

li      $t0, 0x80061758  # PRO mode enabled? (marvelous timing?)
lw      $t0, 0($t0)
bne     $t0, 0x4010004, ddr_polyft4_set_texcoord_break # don't display with PRO mode off

lhu     $t0, 0x16($a1)   # tpage
bne     $t0, 0x8ff, ddr_polyft4_set_texcoord_break

lbu     $t0, 0xd($a1)    # tex_v0
bne     $t0, 0x78, ddr_polyft4_set_texcoord_break

li      $t0, 0x801fffd0  # results from checkstep_hook

lhu     $t1, 0x8($a1)    # t1 = tex_x0
bne     $t1, 0x5a, ddr_polyft4_set_texcoord_eval
addiu   $t0, 24          # t0 += sizeof(struct ddr_player_clarity_stats_t)

ddr_polyft4_set_texcoord_eval:
lw      $t2, 0($t0)      # load player chart step time into t2
lw      $t1, 4($t0)      # load player step time into t1

slt     $t3, $t1, $t2    # t3 = 1 if player stepped early

sub     $t4, $t1, $t2    # t4 = time between step and chart
abs     $t4, $t4         # abs(t4)
blt     $t4, 3, ddr_polyft4_set_texcoord_break # marvelous (don't show early/late)
bgt     $t4, 17, ddr_polyft4_set_texcoord_break # invalid step (also don't show)

li      $t2, 0x3c        # x-texcoord (right) for early/late combo sprites
bgtz    $t3, ddr_polyft4_set_texcoord_early

ddr_polyft4_set_texcoord_late:
li      $t0, 0xb9        # y-texcoord (top) for "slow" combo sprite
li      $t1, 0xd5        # y-texcoord (bottom) for "slow" combo sprite
b       ddr_polyft4_set_texcoord_write_to_sprite

ddr_polyft4_set_texcoord_early:
li      $t0, 0x9d        # y-texcoord (top) for "late" combo sprite
li      $t1, 0xb9        # y-texcoord (bottom) for "late" combo sprite

ddr_polyft4_set_texcoord_write_to_sprite:
sb      $0,  0xc($a1)    # poly_ft4.u0 = 0
sb      $t0, 0xd($a1)    # poly_ft4.v0 = 157

sb      $t2, 0x14($a1)   # poly_ft4.u1 = 60
sb      $t0, 0x15($a1)   # poly_ft4.v1 = 157

sb      $0,  0x1c($a1)   # poly_ft4.u2 = 0
sb      $t1, 0x1d($a1)   # poly_ft4.v2 = 185

sb      $t2, 0x24($a1)   # poly_ft4.u3 = 60
sb      $t1, 0x25($a1)   # poly_ft4.v3 = 185

ddr_polyft4_set_texcoord_break:
jr      $ra
