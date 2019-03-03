#
# results_load_hook.s
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 800610F8

beq     $t2, 7, ddr_results_load_fast   # if t2 == 7, it's our added "fast" sprite
beq     $t2, 8, ddr_results_load_slow   # if t2 == 8, it's our added "slow" sprite 
b       ddr_results_load_hook_break     # otherwise, not ours. bail!!

ddr_results_load_fast:
li      $s0, 0x1a4                      # s0 is the number to display
b       ddr_results_load_hook_break

ddr_results_load_slow:
li      $s0, 0x45                       # s0 is the number to display
b       ddr_results_load_hook_break

ddr_results_load_hook_break:
li      $t1, 0x80061184                 # load original jump location
jr      $t1                             # jump to original location
