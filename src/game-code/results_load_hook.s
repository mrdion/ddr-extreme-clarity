#
# results_load_hook.s
#
# written by zanneth <root@zanneth.com>
#

# struct ddr_player_clarity_stats_t
# {
#     uint32_t chart_step_time;         [00 32-bits]
#     uint32_t player_step_game_time;   [04 32-bits]
#     uint32_t fast_count;              [08 32-bits]
#     uint32_t slow_count;              [12 32-bits]
# }
#
# total size = 16 bytes
# one instance per player

# jump to me from 800610F8

li      $t1, 0x801fffd0                 # clarity stats struct location
bne     $a1, 4, ddr_results_load_verify # if a1 != 4, we are player 1
addiu   $t1, 16                         # t1 += sizeof(struct ddr_player_clarity_stats_t)

ddr_results_load_verify:
beq     $t2, 7, ddr_results_load_fast   # if t2 == 7, it's our added "fast" sprite
beq     $t2, 8, ddr_results_load_slow   # if t2 == 8, it's our added "slow" sprite 
b       ddr_results_load_break          # otherwise, not ours. bail!!

ddr_results_load_fast:
lw      $s0, 8($t1)                     # s0 is the number to display, s0 = fast_count
b       ddr_results_load_break

ddr_results_load_slow:
lw      $s0, 12($t1)                    # s0 is the number to display, s0 = slow_count
b       ddr_results_load_break

ddr_results_load_break:
li      $t1, 0x80061184                 # load original jump location
jr      $t1                             # jump to original location
