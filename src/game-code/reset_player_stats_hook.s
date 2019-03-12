#
# reset_player_stats_hook.s
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

# jump to me from 80076490

li      $t1, 0x801fffd0     # RAM location of clarity stats
li      $t2, 2              # number of players

ddr_reset_player_stats_hook_loop:
sw      $0, 0($t1)          # chart_step_time = 0
sw      $0, 4($t1)          # player_step_time = 0
sw      $0, 8($t1)          # fast_count = 0
sw      $0, 16($t1)         # slow_count = 0

addiu   $t1, 24             # t1 = ptr to next player's stats struct
addiu   $t2, -1             # t2--
bne     $t2, 0, ddr_reset_player_stats_hook_loop

jr      $ra                 # jump to original location
