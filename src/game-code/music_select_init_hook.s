#
# music_select_init_hook.s
#
# hook into the routine that runs before showing the music select screen. in 
# event mode, write '1' instead of '0' into the current stage address so that we
# are always at second stage.
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 80027C64

li      $t1, 0x800f003b # event mode?
lb      $t1, 0($t1)
beqz    $t1, ddr_game_state_init_break

li      $t1, 0x800f0030
li      $t2, 0x00010003
sw      $t2, 0($t1)

li      $t2, 1
sb      $t2, 4($t1)

li      $t2, 0
sb      $t2, 5($t1)
sb      $t2, 6($t1)

ddr_game_state_init_break:
jr      $ra             # jump to original location
