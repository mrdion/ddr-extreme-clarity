#
# results_main_hook.s
#
# there is not enough space on some types of results screens to add the two
# extra score entries that we need to show "FAST" and "SLOW". furthermore, the
# spritesheet that we replaced has valuable data on it for these types of
# results screens that we overwrote to add the "FAST" and "SLOW" UI cells. for
# example, the ONI results screen shows a password and time interval on the
# bottom, and the NONSTOP results screen sometimes shows a password depending on
# the course that was played.
#
# it's not enough to prevent our other hooks from running in these scenarios,
# because in order to trick the results screen into showing more score entries
# than what was previously possible, we have to patch numerous immediate values
# that are hardcoded in the game's binary. therefore, the only option is to
# actually patch the results screen code at runtime right before it shows up on
# screen.
#
# this hook is executed from a jump table entry that is located at 0x800D8B70,
# and does the initial preparation to show all types of results screens. we have
# to check the global game mode value to determine if we need to patch or
# unpatch the results screen.
#
# /!\ WARNING /!\
# assumes that the replacement "rslob_25.cmt" sprite got loaded at file offset
# 0x68800!
#
# written by zanneth <root@zanneth.com>
#

# overwrite the table entry at 800D8B70 with an address pointing to me

li  $t1, 0x800F0048     # t1 = ptr to global game mode
lb  $t2, 0($t1)         # t2 = global game mode
bne $t2, 0, ddr_results_unpatch_code # unpatch if mode other than normal

# ------------------------------------------------------------------------------

ddr_results_patch_code:
# patch file table entry for rslob_25.cmt
li $t1, 0x80143ab0

li $t2, 0xd1    # file offset >> 11
sw $t2, 4($t1)  # store in ft_entry.offset

sw $0, 8($t1)   # compressed flag

li $t2, 0x12e20 # file size
sw $t2, 12($t1) # store in ft_entry.length

# patch code in results screen draw loop
li $t1, 0x80061858
li $t2, 0x2942000a
sw $t2, 0($t1)

li $t1, 0x80060f7c
li $t2, 0x2404000a
sw $t2, 0($t1)

li $t1, 0x80061020
li $t2, 0x28840009
sw $t2, 0($t1)

li $t1, 0x80061270
li $t2, 0x24040009
sw $t2, 0($t1)

li $t1, 0x80061278
li $t2, 0x29420009
sw $t2, 0($t1)

li $t1, 0x80061294
li $t2, 0x29420009
sw $t2, 0($t1)

li $t1, 0x800612a4
li $t2, 0x29420009
sw $t2, 0($t1)

li $t1, 0x8006132c
li $t2, 0x29420009
sw $t2, 0($t1)

li $t1, 0x80061640
li $t2, 0x24420009
sw $t2, 0($t1)

li $t1, 0x80061648
li $t2, 0x24020009
sw $t2, 0($t1)

li $t1, 0x80061650
li $t2, 0x24020008
sw $t2, 0($t1)

li $t1, 0x80061264
li $t2, 0x245effb1
sw $t2, 0($t1)

li $t1, 0x80061630
li $t2, 0x24420001
sw $t2, 0($t1)

b  ddr_results_return

# ------------------------------------------------------------------------------

ddr_results_unpatch_code:
# patch file table entry for rslob_25.cmt
li $t1, 0x80143ab0

li $t2, 0x5ce   # file offset >> 11
sw $t2, 4($t1)  # store in ft_entry.offset

li $t2, 1       # compressed flag
sw $t2, 8($t1)  # store in ft_entry.compression_flags

li $t2, 0x3a0b  # file size
sw $t2, 12($t1) # store in ft_entry.length

# patch code in results screen draw loop
li $t1, 0x80061858
li $t2, 0x29420008
sw $t2, 0($t1)

li $t1, 0x80060f7c
li $t2, 0x24040008
sw $t2, 0($t1)

li $t1, 0x80061020
li $t2, 0x28840007
sw $t2, 0($t1)

li $t1, 0x80061270
li $t2, 0x24040007
sw $t2, 0($t1)

li $t1, 0x80061278
li $t2, 0x29420007
sw $t2, 0($t1)

li $t1, 0x80061294
li $t2, 0x29420007
sw $t2, 0($t1)

li $t1, 0x800612a4
li $t2, 0x29420007
sw $t2, 0($t1)

li $t1, 0x8006132c
li $t2, 0x29420007
sw $t2, 0($t1)

li $t1, 0x80061640
li $t2, 0x24420007
sw $t2, 0($t1)

li $t1, 0x80061648
li $t2, 0x24020007
sw $t2, 0($t1)

li $t1, 0x80061650
li $t2, 0x24020006
sw $t2, 0($t1)

li $t1, 0x80061264
li $t2, 0x245effc7
sw $t2, 0($t1)

li $t1, 0x80061630
li $t2, 0x24420017
sw $t2, 0($t1)

# ------------------------------------------------------------------------------

ddr_results_return:
li $t1, 0x800267A4
jr $t1
