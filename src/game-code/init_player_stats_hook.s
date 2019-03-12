#
# init_player_stats_hook.s
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

# jump to me from 80025DF0

li      $t1, 0x801fffd0     # RAM location of clarity stats
li      $t2, 12             # 6 words (24 bytes) per player that we need to clear

ddr_init_player_stats_loop:
sw      $0, 0($t1)          # zero out word in stats struct
addiu   $t1, 4              # t1 = ptr to next field
addiu   $t2, -1             # t2--
bne     $t2, $0, ddr_init_player_stats_loop

jr      $ra                 # jump to original location
