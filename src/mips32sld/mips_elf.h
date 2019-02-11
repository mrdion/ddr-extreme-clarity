/*
 * mips32sld
 * mips_elf.h
 *
 * static loader to create injectable DSOs for MIPS32
 * root@zanneth.com
 */

#ifndef __MIPS_ELF_H__
#define __MIPS_ELF_H__

/* MIPS relocs.  */

#define R_MIPS_NONE     0   /* No reloc */
#define R_MIPS_16       1   /* Direct 16 bit */
#define R_MIPS_32       2   /* Direct 32 bit */
#define R_MIPS_REL32    3   /* PC relative 32 bit */
#define R_MIPS_26       4   /* Direct 26 bit shifted */
#define R_MIPS_HI16     5   /* High 16 bit */
#define R_MIPS_LO16     6   /* Low 16 bit */
#define R_MIPS_GPREL16  7   /* GP relative 16 bit */
#define R_MIPS_LITERAL  8   /* 16 bit literal entry */
#define R_MIPS_GOT16    9   /* 16 bit GOT entry */
#define R_MIPS_PC16     10  /* PC relative 16 bit */
#define R_MIPS_CALL16   11  /* 16 bit GOT entry for function */
#define R_MIPS_GPREL32  12  /* GP relative 32 bit */

#define R_MIPS_SHIFT5   16
#define R_MIPS_SHIFT6   17
#define R_MIPS_64       18
#define R_MIPS_GOT_DISP 19
#define R_MIPS_GOT_PAGE 20
#define R_MIPS_GOT_OFST 21
#define R_MIPS_GOT_HI16 22
#define R_MIPS_GOT_LO16 23
#define R_MIPS_SUB      24
#define R_MIPS_INSERT_A 25
#define R_MIPS_INSERT_B 26
#define R_MIPS_DELETE   27
#define R_MIPS_HIGHER   28
#define R_MIPS_HIGHEST  29
#define R_MIPS_CALL_HI1 30
#define R_MIPS_CALL_LO16 31
#define R_MIPS_SCN_DISP 32
#define R_MIPS_REL16    33
#define R_MIPS_ADD_IMMEDIATE 34
#define R_MIPS_PJUMP    35
#define R_MIPS_RELGOT   36
#define R_MIPS_JALR     37
#define R_MIPS_TLS_DTPMOD32 38  /* Module number 32 bit */
#define R_MIPS_TLS_DTPREL32 39  /* Module-relative offset 32 bit */
#define R_MIPS_TLS_DTPMOD64 40  /* Module number 64 bit */
#define R_MIPS_TLS_DTPREL64 41  /* Module-relative offset 64 bit */
#define R_MIPS_TLS_GD       42  /* 16 bit GOT offset for GD */
#define R_MIPS_TLS_LDM      43  /* 16 bit GOT offset for LDM */
#define R_MIPS_TLS_DTPREL_HI16  44  /* Module-relative offset, high 16 bits */
#define R_MIPS_TLS_DTPREL_LO16  45  /* Module-relative offset, low 16 bits */
#define R_MIPS_TLS_GOTTPREL 46  /* 16 bit GOT offset for IE */
#define R_MIPS_TLS_TPREL32  47  /* TP-relative offset, 32 bit */
#define R_MIPS_TLS_TPREL64  48  /* TP-relative offset, 64 bit */
#define R_MIPS_TLS_TPREL_HI16 49  /* TP-relative offset, high 16 bits */
#define R_MIPS_TLS_TPREL_LO16 50  /* TP-relative offset, low 16 bits */
#define R_MIPS_GLOB_DAT     51
#define R_MIPS_COPY         126
#define R_MIPS_JUMP_SLOT    127

/* Keep this the last entry.  */
#define R_MIPS_NUM          128

#endif // __MIPS_ELF_H__
