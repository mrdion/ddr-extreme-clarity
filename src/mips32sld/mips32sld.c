/*
 * mips32sld
 * mips32sld.c
 *
 * static loader to create injectable DSOs for MIPS32
 * root@zanneth.com
 */

#include <assert.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifdef __APPLE__
#include <libelf/libelf.h>
#else
#include <libelf.h>
#endif

#include "got.h"
#include "mips_elf.h"

typedef struct
{
    // the ELF file being processed
    Elf      *elf;
    
    // the ".text" section of the binary
    Elf_Scn  *text_section;
    
    // the symbol table section of the binary
    Elf_Scn  *symtab_section;
    
    // the relocation section of the binary, where all the relocation entries
    // are stored
    Elf_Scn  *rel_section;
    
    // the section for the GOT being added to the binary
    Elf_Scn  *got_section;
    
    // the data for the GOT, where virtual addresses are added
    SLDGOT   *got;
    
    // the target virtual address into which the payload will be loaded
    uintptr_t target_vaddr;
} SLDRelocationContext;

// -----------------------------------------------------------------------------

static void print_usage(const char *progname)
{
    printf("usage: %s -a target-address elf-file\n", progname);
}

static bool parse_args(int argc, 
                       const char **argv,
                       const char **out_elf_file_path,
                       uintptr_t *out_target_addr)
{
    bool valid = (
        argc >= 4 &&
        strcmp(argv[1], "-a") == 0 &&
        out_elf_file_path != NULL &&
        out_target_addr != NULL
    );
    
    if (valid) {
        sscanf(argv[2], "%lx", out_target_addr);
        *out_elf_file_path = argv[3];
    }
    
    return valid;
}

static bool validate_elf(Elf *elf)
{
    const char *ehdr_ident = elf_getident(elf, NULL);
    return (
        ehdr_ident[0] == 0x7f &&
        ehdr_ident[1] == 'E' &&
        ehdr_ident[2] == 'L' &&
        ehdr_ident[3] == 'F'
    );
}

static bool extract_sections(Elf *elf,
                             Elf_Scn **out_text_section,
                             Elf_Scn **out_symtab_section,
                             Elf_Scn **out_rel_section)
{
    // get section index of string table
    size_t shstrndx = 0;
    int err = elf_getshdrstrndx(elf, &shstrndx);
    if (err != 0) {
        return false;
    }
    
    // find the sections we're interested in
    Elf_Scn *cur_section = NULL;
    Elf_Scn *text_section = NULL;
    Elf_Scn *symtab_section = NULL;
    Elf_Scn *rel_section = NULL;
    
    while ((cur_section = elf_nextscn(elf, cur_section)) != NULL) {
        const Elf32_Shdr *section_hdr = elf32_getshdr(cur_section);
        if (section_hdr) {
            const char *section_name = elf_strptr(elf, 
                                                  shstrndx, 
                                                  section_hdr->sh_name);
            
            if (strcmp(section_name, ".text") == 0) {
                text_section = cur_section;
            } else if (strcmp(section_name, ".symtab") == 0) {
                symtab_section = cur_section;
            } else if (strcmp(section_name, ".rel.text") == 0) {
                rel_section = cur_section;
            }
        }
    }
    
    // store output
    if (out_text_section)   { *out_text_section = text_section; }
    if (out_symtab_section) { *out_symtab_section = symtab_section; }
    if (out_rel_section)    { *out_rel_section = rel_section; }
    
    return (
        text_section != NULL &&
        symtab_section != NULL &&
        rel_section != NULL
    );
}

static bool initialize_got_section(Elf *elf, 
                                   Elf_Scn **out_got_section,
                                   const char **out_errmsg)
{
    const char *errmsg = NULL;
    Elf_Scn *got_section = NULL;
    
    do {
        // create section and data for global offset table
        got_section = elf_newscn(elf);
        if (!got_section) {
            errmsg = "failed to create section for GOT";
            break;
        }
        
        Elf_Data *got_section_data = elf_newdata(got_section);
        if (!got_section_data) {
            errmsg = "failed to allocate data for the GOT section";
            break;
        }
        
        got_section_data->d_align = 4;
        got_section_data->d_off = 0LL;
        got_section_data->d_buf = NULL; // filled in later after GOT populated
        got_section_data->d_type = ELF_T_ADDR;
        got_section_data->d_version = EV_CURRENT;
        
        // setup section header for GOT
        Elf32_Shdr *got_shdr = elf32_getshdr(got_section);
        if (!got_shdr) {
            errmsg = "failed to get section header for newly created GOT section";
            break;
        }
        
        got_shdr->sh_name = 12; // TODO
        got_shdr->sh_type = SHT_PROGBITS;
        got_shdr->sh_flags = SHF_ALLOC;
        got_shdr->sh_entsize = 0;
        
        // recalculate memory structures to compute GOT section offset
        off_t updated_img_size = elf_update(elf, ELF_C_NULL);
        if (updated_img_size == -1) {
            errmsg = "failed to recompute ELF memory structures after adding GOT";
            break;
        }
    } while (0);
    
    if (out_got_section) { *out_got_section = got_section; }
    if (out_errmsg) { *out_errmsg = errmsg; }
    
    return (errmsg == NULL);
}

static bool parse_and_apply_relocations(const SLDRelocationContext *ctx)
{
    if (!ctx) return false;
    
    const Elf32_Shdr *got_shdr = elf32_getshdr(ctx->got_section);
    const Elf32_Addr got_vaddr = ctx->target_vaddr + got_shdr->sh_offset;
    
    // fetch text section data
    Elf32_Shdr *text_shdr = elf32_getshdr(ctx->text_section);
    Elf_Data *text_data = elf_getdata(ctx->text_section, NULL);
    
    // fetch symtab entries to prepare for querying
    const Elf32_Shdr *symtab_shdr = elf32_getshdr(ctx->symtab_section);
    const Elf_Data *symtab_data = elf_getdata(ctx->symtab_section, NULL);
    const Elf32_Sym *symtab_entries = (Elf32_Sym *)symtab_data->d_buf;
    
    // fetch relocation data from the context
    const Elf32_Shdr *rel_shdr = elf32_getshdr(ctx->rel_section);
    const size_t rel_num_entries = rel_shdr->sh_size / rel_shdr->sh_entsize;
    const Elf_Data *rel_data = elf_getdata(ctx->rel_section, NULL);
    const Elf32_Rel *rel_entries = (Elf32_Rel *)rel_data->d_buf;
    
    // parse relocation entries
    uint32_t prev_hi16_computed_word = 0;
    for (unsigned i = 0; i < rel_num_entries; ++i) {
        const Elf32_Rel *rel = &rel_entries[i];
        const unsigned symtab_idx = ELF32_R_SYM(rel->r_info);
        const unsigned rel_type = ELF32_ST_TYPE(rel->r_info);
        const Elf32_Sym *sym = &symtab_entries[symtab_idx];
        const char *sym_name = elf_strptr(ctx->elf, symtab_shdr->sh_link, sym->st_name);
        Elf_Scn *rel_section = elf_getscn(ctx->elf, sym->st_shndx);
        Elf32_Shdr *rel_shdr = elf32_getshdr(rel_section);
        
        // perform the calculation
        uint32_t calculation = 0;
        if (strcmp(sym_name, "_gp_disp") == 0) {
            /* compute the offset from the image address of this relocation
            to where the GOT will be loaded in memory. */
            calculation = (
                got_vaddr - (
                    ctx->target_vaddr +
                    text_shdr->sh_offset +
                    rel->r_offset
                )
            );
        } else {
            // compute virtual address of loaded symbol
            calculation = (
                ctx->target_vaddr + 
                rel_shdr->sh_offset +
                sym->st_value
            );
        }
        
        // perform the relocation
        uint16_t relocation_data = 0x0;
        switch (rel_type) {
            case R_MIPS_HI16:
                // store upper 16 bits of the calculation
                relocation_data = (calculation & 0xffff0000) >> 16;
                prev_hi16_computed_word = calculation;
                break;
            
            case R_MIPS_LO16:
                // MIPS ABI specifies that a LO16 must be preceded by a HI16
                relocation_data = (prev_hi16_computed_word & 0xffff);
                break;
                
            case R_MIPS_GOT16:
            case R_MIPS_CALL16: {
                uint32_t ahl = calculation;
                
                if (rel_type == R_MIPS_GOT16) {
                    /* R_MIPS_GOT16 relocations contain an addend that must be
                       computed from a paired R_MIPS_LO16 relocation */
                    const Elf32_Rel *low_rel = &rel_entries[i + 1];
                    if (ELF32_ST_TYPE(low_rel->r_info) == R_MIPS_LO16) {
                        ++i; // skip LO16
                    }
                }
                
                // store the address in the GOT and compute the offset
                const uint32_t got_idx = sld_got_append_addr(ctx->got, ahl);
                const uint32_t got_off = got_idx * sizeof(Elf32_Addr);
                relocation_data = (uint16_t)got_off;
            } break;
                
            default:
                break;
        }
        
        // apply relocation to the text section data
        *(uint16_t *)(text_data->d_buf + rel->r_offset) = relocation_data;
    }
    
    // update GOT section with data appended to the GOT
    Elf_Data *got_section_data = elf_getdata(ctx->got_section, NULL);
    got_section_data->d_buf = sld_got_get_buffer(ctx->got);
    got_section_data->d_size = sld_got_get_count(ctx->got) * sizeof(Elf32_Addr);
    
    return true;
}

static bool relocate_elf(const char *elf_file_path, uintptr_t target_vaddr)
{
    const char *errmsg = NULL;
    bool success = false;
    
    Elf *elf = NULL;
    SLDGOT *got = NULL;
    
    int in_fd = -1;
    
    do {
        // validate and initialize libelf (required)
        if (elf_version(EV_CURRENT) == EV_NONE) {
            errmsg = "libelf library out-of-date";
            break;
        }
        
        // open input file
        in_fd = open(elf_file_path, O_RDWR);
        if (in_fd == -1) {
            errmsg = "file does not exist";
            break;
        }
        
        // begin parsing the ELF file
        elf = elf_begin(in_fd, ELF_C_RDWR, NULL);
        if (!elf) {
            errmsg = "failed to parse ELF file";
            break;
        }
        
        // verify that it's a valid ELF file
        success = validate_elf(elf);
        if (!success) {
            errmsg = "file is not a valid ELF file";
            break;
        }
        
        // find and extract the sections that we need from the object file
        Elf_Scn *text_section = NULL;
        Elf_Scn *symtab_section = NULL;
        Elf_Scn *rel_section = NULL;
        success = extract_sections(elf, &text_section, &symtab_section, &rel_section);
        if (!success) {
            errmsg = "failed to find required sections for relocation";
            break;
        }
        
        // allocate and initialize the GOT buffer
        got = sld_got_create();
        
        // create section and data for global offset table
        Elf_Scn *got_section = NULL;
        success = initialize_got_section(elf, &got_section, &errmsg);
        if (!success) {
            break;
        }
        
        // parse relocation entries and apply the relocations
        SLDRelocationContext ctx = {
            .elf            = elf,
            .text_section   = text_section,
            .symtab_section = symtab_section,
            .rel_section    = rel_section,
            .got_section    = got_section,
            .got            = got,
            .target_vaddr   = target_vaddr
        };
        success = parse_and_apply_relocations(&ctx);
        if (!success) {
            errmsg = "failed to parse and apply relocation entries to the object file";
            break;
        }
        
        // mark the program header as dirty, since we modified the ELF data
        elf_flagphdr(elf, ELF_C_SET, ELF_F_DIRTY);
        
        // write changes back to ELF file
        off_t updated_img_size = elf_update(elf, ELF_C_WRITE);
        if (updated_img_size == -1) {
            errmsg = "failed to write data back to ELF file";
            break;
        }
    } while (0);
    
    // cleanup
    if (elf != NULL) { elf_end(elf); }
    if (got != NULL) { sld_got_destroy(got); }
    if (in_fd != -1) { close(in_fd); }
    
    // print error message, if any
    if (errmsg) {
        fprintf(stderr, "%s\n", errmsg);
    }
    
    return (errmsg == NULL);
}

int main(int argc, const char **argv)
{
    bool        success = false;
    const char *elf_file_path = NULL;
    uintptr_t   target_vaddr = 0x0;
    
    if (argc >= 2) {
        success = parse_args(argc, argv, &elf_file_path, &target_vaddr);
        
        if (success) {
            success = relocate_elf(elf_file_path, target_vaddr);
        } else {
            print_usage(argv[0]);
        }
    } else {
        print_usage(argv[0]);
    }
    
    return (success ? EXIT_SUCCESS : EXIT_FAILURE);
}
