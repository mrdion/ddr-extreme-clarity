TARGET    		:= clarity.bin
SRCS      		:= init_player_stats_hook.s \
				   reset_player_stats_hook.s \
				   checkstep_hook.s \
				   texcoord_hook.s \
				   vertex_hook.s \
				   results_load_hook.s \
				   results_texcoord_hook.s \
				   results_main_hook.s \
				   music_select_init_hook.s

BUILD_DIR 		:= ./build
OBJS      		:= ${SRCS:%.s=${BUILD_DIR}/%.o}
BINS      		:= ${SRCS:%.s=${BUILD_DIR}/%.bin}

CC              = mips-img-elf-gcc
CCFLAGS         = -Os -nostartfiles -nostdlib -march=r3000 -EL -fPIC -mabicalls

OBJCOPY         = mips-img-elf-objcopy
OBJCOPYFLAGS    = -j .text -O binary

MANIFEST_SCRIPT = ./genmanifest.sh

.PHONY: all clean
all:: ${TARGET}

${BUILD_DIR}/%.o: %.s
	@mkdir -p ${BUILD_DIR}
	${CC} ${CCFLAGS} -o $@ -c $<

${BUILD_DIR}/%.bin: ${BUILD_DIR}/%.o
	${OBJCOPY} ${OBJCOPYFLAGS} $< $@

${TARGET}: ${BINS}
	${MANIFEST_SCRIPT} $^ > ${BUILD_DIR}/manifest.json
	cat $^ > ${BUILD_DIR}/$@
	rm -f $^

clean:: 
	-rm -rf ${BUILD_DIR}