#
# results_load_hook.s
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

# jump to me from 80061154
# need to return to either 8006115C, 80061174 or 8006112C

li      $t1, 0x801fffd0                 # clarity stats struct location
bne     $a1, 4, ddr_results_load_verify # if a1 != 4, we are player 1
addiu   $t1, 24                         # t1 += sizeof(struct ddr_player_clarity_stats_t)

ddr_results_load_verify:
beq     $t2, 7, ddr_results_load_fast   # if t2 == 7, it's our added "fast" sprite
beq     $t2, 8, ddr_results_load_slow   # if t2 == 8, it's our added "slow" sprite
beq     $t2, 9, ddr_results_load_score  # if t2 == 9, redirect control flow to "score" branch
b       ddr_results_load_return_default # otherwise, not ours. bail!!

ddr_results_load_fast:
lw      $s0, 8($t1)                     # s0 is the number to display, s0 = fast_count
b       ddr_results_load_return_fast_slow

ddr_results_load_slow:
lw      $s0, 16($t1)                    # s0 is the number to display, s0 = slow_count
b       ddr_results_load_return_fast_slow

ddr_results_load_return_fast_slow:
li      $t1, 0x8006112C                 # redirect control flow back through code
                                        # that handles normal numerical results
jr      $t1                             # jump

ddr_results_load_score:
li      $t1, 0x8006115C                 # load address of "score" branch
jr      $t1                             # jump

ddr_results_load_return_default:
li      $t1, 0x80061174                 # load address of instruction after patch
jr      $t1                             # jump
