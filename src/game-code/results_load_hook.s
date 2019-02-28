#
# results_load_hook.s
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 800610F8
beq     $t2, 0x7, ddr_results_load_fast
beq     $t2, 0x8, ddr_results_load_slow
b       ddr_results_load_hook_break

ddr_results_load_fast:
li      $s0, 0x1a4
b       ddr_results_load_hook_break

ddr_results_load_slow:
li      $s0, 0x45
b       ddr_results_load_hook_break

ddr_results_load_hook_break:
li      $t1, 0x80061184
jr      $t1
