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
li $t1, 0x801fffe0      # somewhere in RAM
sw $t2, 0($t1)          # store player step in game time
sw $v1, 4($t1)          # store chart step in game time

li $t1, 0x80077638      # load original jump location
jr $t1                  # jump to original branch location
