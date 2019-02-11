/*
 * mips32sld
 * got.h
 *
 * static loader to create injectable DSOs for MIPS32
 * root@zanneth.com
 */

#ifndef __GOT_H__
#define __GOT_H__

#ifdef __APPLE__
#include <libelf/libelf.h>
#else
#include <libelf.h>
#endif

#include <stdint.h>

typedef struct SLDGOT SLDGOT;

extern SLDGOT*     sld_got_create(void);
extern void        sld_got_destroy(SLDGOT *got);

extern Elf32_Addr* sld_got_get_buffer(SLDGOT *got);
extern size_t      sld_got_get_count(SLDGOT *got);

// returns the index of the newly appended address in the GOT
extern uint32_t    sld_got_append_addr(SLDGOT *got, Elf32_Addr addr);

#endif // __GOT_H__
