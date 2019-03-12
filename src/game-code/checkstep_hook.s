#
# checkstep_hook.s
#
# hooks into a specific place in the game code where a step is evaluated.
#
# this code grabs values stored in registers t1 and v2 and stores them
# somewhere in RAM to be accessed later by other hooks. it also computes whether
# the player stepped early or late and increments the respective counter if
# necessary.
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

# jump to me from 0x80077618

li      $t1, 0x801fffd0      # somewhere in RAM

slt     $t4, $t2, $v1        # t4 = 1 if player stepped early
sub     $t5, $t2, $v1        # t5 = time between step and chart
abs     $t5, $t5             # t5 = abs(t5)

bne     $s2, 0x80104450, ddr_checkstep_hook_check # if s2 != 0x80104450, we are player 1
addiu   $t1, 24              # t1 += sizeof(struct ddr_player_clarity_stats_t)

ddr_checkstep_hook_check:
sw      $v1, 0($t1)          # player.chart_step_time = $v1
sw      $t2, 4($t1)          # player.player_step_time = $t2

blt     $t5, 3, ddr_checkstep_hook_break # marvelous (don't increment early/late)

addiu   $t1, 8               # t1 = &(player.fast_count)
bgtz    $t4, ddr_checkstep_hook_increment
addiu   $t1, 8               # t1 = &(player.slow_count)

ddr_checkstep_hook_increment:
lw      $t4, 0($t1)          # t4 = fast/slow count
addiu   $t4, 1               # ++t4
sw      $t4, 0($t1)          # store new count back into stats struct

lw      $t4, 4($t1)          # t4 = total fast/slow count
addiu   $t4, 1               # ++t4
sw      $t4, 4($t1)          # store new total count back into stats struct

ddr_checkstep_hook_break:
li      $t1, 0x80077638      # load original jump location
jr      $t1                  # jump to original branch location
