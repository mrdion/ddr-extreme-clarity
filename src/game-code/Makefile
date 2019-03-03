TARGET    		:= clarity.bin
SRCS      		:= checkstep_hook.s texcoord_hook.s vertex_hook.s results_load_hook.s results_texcoord_hook.s init_player_stats_hook.s
BUILD_DIR 		:= ./build
OBJS      		:= ${SRCS:%.s=${BUILD_DIR}/%.o}
BINS      		:= ${SRCS:%.s=${BUILD_DIR}/%.bin}

CC              = mips-mti-elf-gcc
CCFLAGS         = -Os -nostartfiles -nostdlib -march=r3000 -EL -fPIC -mabicalls

OBJCOPY         = mips-mti-elf-objcopy
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