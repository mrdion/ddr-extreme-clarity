#
# vertex_hook.s
#
# hooks into the end of the function that computes the vertex coordinates used
# by all sprites in the gameplay screen.
#
# since we may have modified the texture coordinates in a previous hook
# (texcoord_hook) to show the combo+early/late indicator sprite rather than just
# the regular combo indicator, we have to increase the size of the drawing
# rectangle as well. this is because our custom sprite that includes the
# "FAST" and "SLOW" text is significantly larger than the regular combo sprite.
#
# this code is a little bit more complicated than simply just overwriting new
# vertex coordinates into the POLY_FT4 struct, since DDR EXTREME uses the vertex
# coordinates to animate the "burst" effect of the combo indicator when the
# player steps. therefore, we have to do arithmetic to grow the drawing
# rectangle rather than just overwriting it.
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 0x8005B6FC
lhu     $t0, 0x16($v0)   # tpage
bne     $t0, 0x8ff, ddr_polyft4_set_vertex_break

lbu     $t0, 0xd($v0)    # tex_v0
beq     $t0, 0x9d, ddr_polyft4_set_vertex_write_to_sprite # "FAST" sprite?
beq     $t0, 0xb9, ddr_polyft4_set_vertex_write_to_sprite # "SLOW" sprite?
b       ddr_polyft4_set_vertex_break # not ours. BAIL!!

ddr_polyft4_set_vertex_write_to_sprite:
lh      $t0, 0xa($v0)    # t0 = poly_ft4.y0
sub     $t0, $t0, 0xe    # move y0 up to render larger sprite
sh      $t0, 0xa($v0)    # overwrite poly_ft4.y0

lh      $t0, 0x10($v0)   # t0 = poly_ft4.x1
add     $t0, $t0, 0xa    # move x1 right to render larger sprite
sh      $t0, 0x10($v0)   # overwrite poly_ft4.x1

lh      $t0, 0x12($v0)   # t0 = poly_ft4.y1
sub     $t0, $t0, 0xe    # move y1 up to render larger sprite
sh      $t0, 0x12($v0)   # overwrite poly_ft4.y1

lh      $t0, 0x20($v0)   # t0 = poly_ft4.x3
add     $t0, $t0, 0xa    # move x3 right to render larger sprite
sh      $t0, 0x20($v0)   # overwrite poly_ft4.x3

ddr_polyft4_set_vertex_break:
jr      $ra
