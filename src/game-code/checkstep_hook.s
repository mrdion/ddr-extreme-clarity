#
# checkstep_hook.s
#
# hooks into a specific place in the game code where a step is evaluated.
#
# this code grabs values stored in registers t1 and v2 and stores them
# somewhere in RAM to be accessed later by other hooks.
#
# written by zanneth <root@zanneth.com>
#

# jump to me from 0x80077618
li      $t1, 0x801fffe0      # somewhere in RAM

beq     $s2, 0x80104450, ddr_checkstep_hook_p2 # check which player we are

sw      $v1, 0($t1)          # store player 1 chart step in game time
sw      $t2, 4($t1)          # store player 1 step in game time
b       ddr_checkstep_hook_break

ddr_checkstep_hook_p2:
sw      $v1, 8($t1)          # store player 2 chart step in game time
sw      $t2, 12($t1)         # store player 2 step in game time

ddr_checkstep_hook_break:
li      $t1, 0x80077638      # load original jump location
jr      $t1                  # jump to original branch location
