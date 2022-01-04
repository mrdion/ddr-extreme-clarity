#
# results_load_hook.s
#
# hook into the routine that runs when loading the score value for a particular
# score entry on the results screen. this code assumes that `results_main_hook`
# already executed and performed the correct runtime patching of the code that
# draws the results screen. this code previously inserted two new score entries
# for "FAST" and "SLOW", and when we are loading a value for one of these, load
# it from the clarity stats struct in RAM instead of from the player stats.
#
# the tricky thing about this particular hook is that we need to carefully
# redirect execution flow depending on what we loaded (or didn't load).
# otherwise, incorrect values will be loaded for various parameters that direct
# how the results screen is drawn and the game will crash.
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
# need to return to either 8006115C, 80061174, 8006112C, or 800610C0

li      $t1, 0x80079ca0  # PRO mode enabled? (skip money score calculation?)
lw      $t1, 0($t1)
bgtz    $t1, ddr_results_load_return_default # skip if PRO mode is off

li      $t1, 0x800F0048     # load ptr to global game mode
lb      $t3, 0($t1)         # load game mode into $t2
bne     $t3, 0, ddr_results_load_return_default # don't do anything if we're not in normal mode

lw      $t3, 0xd0($sp)                  # t3 = ptr to ddr mode info
lw      $t3, 0x18($t3)                  # t3 = results mode type (0 if regular, 1 if total)

li      $t1, 0x801fffd0                 # clarity stats struct location
bne     $a1, 4, ddr_results_load_verify # if a1 != 4, we are player 1
addiu   $t1, 24                         # t1 += sizeof(struct ddr_player_clarity_stats_t)

ddr_results_load_verify:
beq     $t2, 7, ddr_results_load_fast   # if t2 == 7, it's our added "fast" sprite
beq     $t2, 8, ddr_results_load_slow   # if t2 == 8, it's our added "slow" sprite
beq     $t2, 9, ddr_results_load_score  # if t2 == 9, redirect control flow to "score" branch
b       ddr_results_load_return_default # otherwise, not ours. bail!!

# ------------------------------------------------------------------------------

ddr_results_load_fast:
beq     $t3, 1, ddr_results_load_fast_total # if t3 == 1, we're showing the total results screen

lw      $s0, 8($t1)                     # s0 is the number to display, s0 = fast_count
b       ddr_results_load_return_fast_slow

ddr_results_load_fast_total:
lw      $s0, 12($t1)                    # s0 is the number to display, s0 = total_fast_count
b       ddr_results_load_return_fast_slow_total

# ------------------------------------------------------------------------------

ddr_results_load_slow:
beq     $t3, 1, ddr_results_load_slow_total # if t3 == 1, we're showing the total results screen

lw      $s0, 16($t1)                    # s0 is the number to display, s0 = slow_count
b       ddr_results_load_return_fast_slow

ddr_results_load_slow_total:
lw      $s0, 20($t1)                    # s0 is the number to display, s0 = total_slow_count   
b       ddr_results_load_return_fast_slow_total

ddr_results_load_score:
li      $t1, 0x8006115C                 # load address of "score" branch
jr      $t1                             # jump

# ------------------------------------------------------------------------------

ddr_results_load_return_fast_slow:
li      $t1, 0x8006112C                 # redirect control flow back through code
                                        # that handles normal numerical results
jr      $t1                             # jump

ddr_results_load_return_fast_slow_total:
li      $t1, 0x800610C0                 # redirect control flow back through code
                                        # that handles the total results path
jr      $t1                             # jump

ddr_results_load_return_default:
beq     $t2, $v0, ddr_results_load_score # this is the original instruction that we patched

ddr_results_load_return_one_digit:
li      $t1, 0x80061174                 # load address of instruction after patch
jr      $t1                             # jump
