/*
 * mips32sld
 * got.c
 *
 * static loader to create injectable DSOs for MIPS32
 * root@zanneth.com
 */

#include "got.h"
#include <stdlib.h>

#define INITIAL_CAPACITY 5
#define GROWTH_SIZE      5

struct SLDGOT
{
    Elf32_Addr *buffer;
    size_t      count;
    size_t      capacity;
};

static void _sld_got_resize(SLDGOT *got, size_t new_capacity);

// -----------------------------------------------------------------------------

SLDGOT* sld_got_create(void)
{
    SLDGOT *got = (SLDGOT *)malloc(sizeof(struct SLDGOT));
    got->buffer = (Elf32_Addr *)malloc(INITIAL_CAPACITY * sizeof(Elf32_Addr));
    got->count = 0;
    got->capacity = INITIAL_CAPACITY;
    
    return got;
}

void sld_got_destroy(SLDGOT *got)
{
    free(got->buffer);
    free(got);
}

Elf32_Addr* sld_got_get_buffer(SLDGOT *got)
{
    return got->buffer;
}

size_t sld_got_get_count(SLDGOT *got)
{
    return got->count;
}

uint32_t sld_got_append_addr(SLDGOT *got, Elf32_Addr addr)
{
    if (got->count >= got->capacity) {
        _sld_got_resize(got, got->capacity + GROWTH_SIZE);
    }
    
    uint32_t idx = got->count++;
    got->buffer[idx] = addr;
    
    return idx;
}

// -- internal -----------------------------------------------------------------

void _sld_got_resize(SLDGOT *got, size_t new_capacity)
{
    if (new_capacity > got->capacity) {
        Elf32_Addr *new_values = (Elf32_Addr *)malloc(new_capacity * sizeof(Elf32_Addr));
        
        for (unsigned i = 0; i < got->count; ++i) {
            new_values[i] = got->buffer[i];
        }
        
        free(got->buffer);
        got->buffer = new_values;
        got->capacity = new_capacity;
    }
}
