# MILESTONES.md — silly-snobol4 Faithful C Rewrite of v311.sil

**Source:** CSNOBOL4 2.3.3, `v311.sil` (Phil Budne, 2022-02-17), 12,293 lines
**Target:** Pure functional C, self-contained in this folder, nothing else referenced
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Started:** 2026-04-06

---

## Ground Rules

1. **SIL names verbatim.** Every label, global, procedure, and constant from
   v311.sil keeps its exact name. `SCBSCL`, `OCICL`, `NAMICL`, `XPTR`, `FINDEX`,
   `AUGATL`, `DTREP`, `KNLIST`, `MSG1`…`MSG39` — all identical.

2. **Same data structures.** `DESCR`, `SPEC`, `STRING` layout is the SIL layout
   in C structs. No "improvements". The on-memory bit patterns are identical.

3. **32-bit clean on 64-bit platform.** `int_t = int32_t`. Pointer fields in
   DESCR hold 32-bit values (offsets into a managed arena, not raw pointers).
   This is fine: the SIL was designed for 32-bit word machines. We use a 128 MB
   arena allocated at startup; all addresses fit in 32 bits.

4. **New control flow.** Zero gotos. Zero computed BRANCHes. `if`/`while`/
   `for`/`switch` only. Each SIL PROC boundary is a real C function with real
   typed parameters and a typed return value. RCALL → C function call. RRTURN
   → return. Multiple exits (RRTURN ,1 / ,2 / ,3) → enum return code or
   out-parameter.

5. **Same messages.** `MSG1`…`MSG39` and `EMSG1`…`EMSG14` verbatim strings.
   Format strings verbatim. Error codes verbatim.

6. **BLOCKS section skipped.** Lines 7038–10208 of v311.sil (3,304 lines,
   `#ifdef BLOCKS`) — no corpus tests use it, skip entirely.

7. **One folder.** `silly-snobol4/` contains every source file. No external
   headers except `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<math.h>`,
   `<stdint.h>`, `<setjmp.h>`, `<signal.h>`.

8. **Compile-first.** Each milestone gate is `gcc -Wall -Wextra -std=c99 -m32 -c`.
   Nothing needs to link or run until all milestones complete.

---

## The 32-bit Arena Model

Rather than raw pointers, `DESCR.a` holds a 32-bit arena offset.
One flat arena of 128 MB is `mmap`'d at startup. All "pointers" in the
SIL code are offsets from `arena_base`. This faithfully models the original
SIL address arithmetic (`SUM`, `INCRA`, `DECRA` on A-field values).

```c
/* sil_types.h */
static char *arena_base;          /* set once at startup */
#define ARENA_SIZE  (128 * 1024 * 1024)

typedef int32_t  int_t;           /* SIL integer / address field */
typedef float    real_t;          /* SIL real (32-bit) */

/* DESCR — the universal SIL cell */
typedef struct {
    int_t  a;     /* A field: integer value, arena offset, or real bits */
    int8_t f;     /* F field: FNC TTL STTL MARK PTR FRZN */
    int_t  v;     /* V field: data type code or size (24-bit in SIL; int32 here) */
} DESCR;

#define DESCR_SZ  ((int)sizeof(DESCR))   /* = 9 bytes packed, or 12 aligned */

/* SPEC — string specifier (two adjacent DESCRs in SIL) */
typedef struct {
    int_t  l;     /* length */
    int_t  o;     /* offset into string block */
    int_t  a;     /* arena offset of STRING block */
    int_t  v;     /* type (always S=1 for real strings) */
} SPEC;

#define SPEC_SZ  ((int)sizeof(SPEC))

/* Convenience: raw pointer from arena offset */
#define A2P(off)  ((void*)(arena_base + (off)))
#define P2A(ptr)  ((int_t)((char*)(ptr) - arena_base))
```

---

## File Map

```
silly-snobol4/
  MILESTONES.md         ← this file (updated each milestone)
  sil_types.h           ← M0: DESCR, SPEC, all EQU constants, flags, type codes
  sil_data.c / .h       ← M1: all named globals from §23 (Data)
  sil_arena.c / .h      ← M2: arena allocator replacing BLOCK/GC/GCM/SPLIT
  sil_strings.c / .h    ← M3: STRING block ops, GENVAR, GNVARI, CONVAR, GNVARS
  sil_symtab.c / .h     ← M4: OBLIST hash table, FINDEX, AUGATL, CODSKP, DTREP
  sil_arith.c / .h      ← M5: ADD/SUB/MPY/DIV/REMDR/EXPOP/MNS/PLS/EQ/…/NE
  sil_argval.c / .h     ← M6: ARGVAL/VARVAL/INTVAL/PATVAL/VARVUP/EXPVAL/XYARGS
  sil_patval.c / .h     ← M7: ANY/BREAK/BREAKX/NOTANY/SPAN/LEN/POS/…/OR + PatNode
  sil_scan.c / .h       ← M8: SCAN/SJSR/SCNR + all 27 match sub-procedures
  sil_nmd.c / .h        ← M9: NMD/NMD1-5/NMDIC/NAMEXN naming list
  sil_asgn.c / .h       ← M10: ASGN/ASGNV/CONCAT/IND/KEYWRD/NAME/STR
  sil_pred.c / .h       ← M11: DIFFER/IDENT/FUNCTN/LABEL/LEQ-LNE/NEG/QUES/CHAR/LPAD/RPAD
  sil_func.c / .h       ← M12: APPLY/ARG/LOCAL/FIELDS/CLEAR/COPY/DUPL/OPSYN/…/VDIFFR
  sil_arrays.c / .h     ← M13: ARRAY/ASSOC/DATDEF/ITEM/DEFDAT/FIELD/RSORT/SSORT
  sil_define.c / .h     ← M14: DEFINE/DEFFNC
  sil_load.c / .h       ← M15: LOAD/UNLOAD/LNKFNC
  sil_io.c / .h         ← M16: READ/PRINT/BKSPCE/ENDFIL/REWIND/SET/DETACH/PUTIN/PUTOUT
  sil_trace.c / .h      ← M17: TRACE/STOPTR/FENTR/FENTR2/KEYTR/TRPHND/VALTR/FNEXT2
  sil_compiler.c / .h   ← M18: BINOP/CMPILE/ELEMNT/EXPR/FORWRD/NEWCRD/TREPUB/UNOP
  sil_interp.c / .h     ← M19: BASE/GOTG/GOTL/GOTO/INIT/INTERP/INVOKE
  sil_errors.c / .h     ← M20: all error handlers, FTLTST/FTLEND/FTLERR + messages
  sil_main.c            ← M21: BEGIN/INIT program/END/SYSCUT + main()
  Makefile              ← updated each milestone
```

---

## Milestone M0 — Types, Equates, Flags `sil_types.h`

**Source:** v311.sil lines 829–953 (§1 Linkage and Equivalences)
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_types.h -o /dev/null` (no warnings)
**Status:** ⬜

### What goes in

Every `EQU` from §1, verbatim name and value:

```c
/* v311.sil §1: Constants */
#define ATTRIB   (2*DESCR_SZ)   /* offset of label in string structure */
#define LNKFLD   (3*DESCR_SZ)   /* offset of link in string structure */
#define BCDFLD   (4*DESCR_SZ)   /* offset of string in string structure */
#define FATHER   (DESCR_SZ)     /* offset of father in code node */
#define LSON     (2*DESCR_SZ)   /* offset of left son in code node */
#define RSIB     (3*DESCR_SZ)   /* offset of right sibling in code node */
#define CODE     (4*DESCR_SZ)   /* offset of code in code node */
#define ESASIZ   50             /* limit on syntactic errors */
#define FBKLSZ   (10*DESCR_SZ)  /* size of function descriptor block */
#define ARRLEN   20             /* limit on array print image */
#define CARDSZ   1024           /* width of compiler input */
#define STNOSZ   8              /* length of statement number field */
#define DSTSZ    (2*STNOSZ)     /* space for left and right numbering */
#define CNODSZS  (4*DESCR_SZ)   /* size of code node */
#define DATSIZ   1000           /* limit on defined data types */
#define EXTSIZ   10             /* default allocation for tables */
#define NAMLSZ   20             /* growth quantum for name list */
#define NODESZ   (3*DESCR_SZ)   /* size of pattern node */
#define OBSFT    13             /* power of two for bin headers */
#define OBSIZ    (1<<OBSFT)     /* number of bin headers = 8192 */
#define OBARY    (OBSIZ+3)      /* total number of bins */
#define OCASIZ   1500           /* descriptors of initial object code */
#define SPDLSZ   8000           /* descriptors of pattern stack */
#define STSIZE   4000           /* descriptors of interpreter stack */
#define SPDR     (SPEC_SZ+DESCR_SZ) /* specifier plus descriptor */
#define OBOFF    (OBSIZ-2)      /* offset length in bins */
#define VLRECL   0              /* variable length record */

/* v311.sil §1: Equivalences (token type codes) */
#define ARYTYP   7    /* array reference */
#define CLNTYP   5    /* goto field */
#define CMATYP   2    /* comma */
#define CMTTYP   2    /* comment card */
#define CNTTYP   4    /* continue card */
#define CTLTYP   3    /* control card */
#define DIMTYP   1    /* dimension separator */
#define EOSTYP   6    /* end of statement */
#define EQTYP    4    /* equal sign */
#define FGOTYP   3    /* failure goto */
#define FTOTYP   6    /* failure direct goto */
#define FLITYP   6    /* literal real */
#define FNCTYP   5    /* function call */
#define ILITYP   2    /* literal integer */
#define LPTYP    1    /* left parenthesis */
#define NBTYP    1    /* nonbreak character */
#define NEWTYP   1    /* new statement */
#define NSTYTP   4    /* parenthesized expression */
#define QLITYP   1    /* quoted literal */
#define RBTYP    7    /* right bracket */
#define RPTYP    3    /* right parenthesis */
#define SGOTYP   2    /* success goto */
#define STOTYP   5    /* success direct goto */
#define UGOTYP   1    /* unconditional goto */
#define UTOTYP   4    /* unconditional direct goto */
#define VARTYP   3    /* variable */

/* v311.sil §1: Data Type Codes */
#define S_TYPE    1   /* STRING */
#define B_TYPE    2   /* BLOCK (internal) */
#define P_TYPE    3   /* PATTERN */
#define A_TYPE    4   /* ARRAY */
#define T_TYPE    5   /* TABLE */
#define I_TYPE    6   /* INTEGER */
#define R_TYPE    7   /* REAL */
#define C_TYPE    8   /* CODE */
#define N_TYPE    9   /* NAME */
#define K_TYPE   10   /* KEYWORD */
#define E_TYPE   11   /* EXPRESSION */
#define DATSTA  100   /* first user datatype */

/* v311.sil §1: Flags (F field bits) */
#define FNC   01    /* function / code pointer */
#define TTL   02    /* block title (header) */
#define STTL  04    /* string block title */
#define MARK  010   /* GC mark */
#define PTR   020   /* contains pointer */
#define FRZN  040   /* frozen table */

/* v311.sil §1: Pattern function dispatch indexes (XATP etc.) */
#define XANYC    1
#define XARBF    2
#define XARBN    3
#define XATP     4
#define XCHR     5
#define XBAL     6
#define XBALF    7
#define XBRKC    8
#define XBRKX    9
#define XBRKXF  10
#define XDNME   11
#define XDNME1  12
#define XEARB   13
#define XDSAR   14
#define XENME   15
#define XENMI   16
#define XFARB   17
#define XFNME   18
#define XLNTH   19
#define XNME    20
#define XNNYC   21
#define XONAR   22
#define XONRF   23
#define XPOSI   24
#define XRPSI   25
#define XRTB    26
#define XFAIL   27
#define XSALF   28
#define XSCOK   29
#define XSCON   30
#define XSPNC   31
#define XSTAR   32
#define XTB     33
#define XRTNL3  34
#define XFNCE   35
#define XSUCF   36

/* Sizes in arena offsets (= byte offsets since char arena) */
#define CPD   DESCR_SZ          /* chars per descriptor */
```

---

## Milestone M1 — All Named Globals `sil_data.c / sil_data.h`

**Source:** v311.sil lines 10481–12293 (§23 Data), plus scattered global declarations
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_data.c` (no warnings)
**Status:** ⬜

### What goes in

Every named `DESCR`, `SPEC`, `STRING`, `FORMAT`, `REAL`, `ARRAY` at file scope,
verbatim name, appropriate C type.

Example mapping:

| SIL | C |
|-----|---|
| `TRIMCL DESCR 0,0,I` | `DESCR TRIMCL = {0, 0, I_TYPE};` |
| `TRAPCL DESCR 0,0,I` | `DESCR TRAPCL = {0, 0, I_TYPE};` |
| `XPTR   DESCR 0,0,0` | `DESCR XPTR   = {0, 0, 0};` |
| `TEXTSP SPEC  ...`   | `SPEC  TEXTSP;` |
| `MSG1   STRING 'Illegal data type'` | `const char MSG1[] = "Illegal data type";` |

Major named global families:

- **Scratch DESCRs:** `XPTR YPTR ZPTR WPTR TPTR XCL YCL ZCL WCL TCL TMVAL SCL AXPTR`
- **Scratch SPECs:** `XSP YSP ZSP WSP TSP TXSP TEXTSP NEXTSP HEADSP LNBFSP XSPPTR YSPPTR`
- **Interpreter registers:** `OCBSCL OCICL CMBSCL CMOFCL PATBCL PATICL OCBSVC`
- **Pattern stack:** `PDLPTR PDLHED PDLEND SCBSCL NBSPTR`
- **Naming list:** `NAMICL NHEDCL`
- **Keywords (KNLIST):** `TRIMCL TRAPCL EXLMCL OUTSW MLENCL INSW GCTRCL FULLCL TRACL FTLLCL ERRLCL DMPCL RETCOD CASECL ANCCL ABNDCL`
- **Read-only keywords (KVLIST):** `ERRTYP ERRTXT ARBPAT BALPAT FNCPAT ABOPAT FALPAT FILENM LNNOCL LSFLNM LSLNCL REMPAT SUCPAT FALCL LSTNCL RETPCL STNOCL ALVHVL EXNOCL LVLCL LCASVL UCASVL PARMVL DIGSVL` + `&PI` as `real_t PI_val`
- **Error messages:** `MSG1`…`MSG39` `EMSG1`…`EMSG14` `ILCHAR ILLBIN ILLBRK ILLDEC ILLEOS ILLINT OPNLIT`
- **Format strings:** `FTLCF SUCCF LISTF GCFMT` and others verbatim from v311.sil
- **Pair lists:** `DTLIST KNLIST KVLIST FNLIST INITLS PRMPTR PRMDX BKLTCL`
- **Arena pointers:** `FRSGPT TLSGP1 HDSGPT MVSGPT OBLIST OBEND STKHED STKEND`
- **Flags/switches:** `INICOM LISTCL EXECCL BANRCL ESAICL VARSYM INSW OUTSW FULLCL`
- **Counters:** `LNNOCL CMOFCL GCNO FALCL EXNOCL STNOCL LVLCL ERRLCL FTLLCL`
- **Pattern primitives:** `ARBPAT BALPAT FNCPAT ABOPAT FALPAT REMPAT SUCPAT` (pattern-node DESCRs)
- **Function table:** `FNLIST` array of function-block DESCRs
- **System stack:** `STKCOD` array (`STSIZE` DESCRs) + `STKPTR`
- **Pattern history list:** `PDLIST` array (`SPDLSZ` DESCRs)
- **Object code block:** `OCLIST` array (`OCASIZ` DESCRs)
- **Units:** `INPUT OUTPUT PUNCH` DESCRs

---

## Milestone M2 — Arena Allocator `sil_arena.c / sil_arena.h`

**Source:** v311.sil §5 lines 1219–1553: `BLOCK`, `GC`, `GCM`, `SPLIT`
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_arena.c`
**Status:** ⬜

### Design

The SIL storage model: one flat heap (`FRSGPT`…`TLSGP1`) with a mark-compact
GC. We keep the same arena but use a **simple bump allocator** + Boehm GC
(or mark-compact reimplementation in M2b).

```c
/* sil_arena.h */

/* arena_init: called once from BEGIN — sets arena_base, FRSGPT, TLSGP1 */
void arena_init(void);

/* BLOCK: allocate n bytes, return arena offset of the new block header */
/* Mirrors SIL BLOCK proc — sets title DESCR (TTL flag, V=size), returns ptr */
int32_t BLOCK(int32_t n);

/* GENVAR: convert SPEC to interned STRING block — mirrors SIL GENVAR */
/* Returns arena offset of STRING_block header DESCR */
int32_t GENVAR(SPEC *sp);

/* GNVARI: GENVAR for empty/null string */
int32_t GNVARI(void);

/* GENVUP: GENVAR + uppercase the string */
int32_t GENVUP(SPEC *sp);

/* CONVAR: get/allocate space for variable — mirrors SIL CONVAR */
int32_t CONVAR(DESCR *d);

/* GNVARS: GENVAR from raw C string */
int32_t GNVARS(const char *s, int len);

/* GC: garbage collect — mark-compact, return amount freed */
/* Mirrors SIL GC proc signature: input = required bytes, output = freed bytes */
int32_t GC(int32_t required);
```

**GC implementation:** faithful mark-compact matching SIL GC/GCM/SPLIT logic,
rewritten as clean C loops (no gotos). The SIL GC has three passes:
1. Mark — walk all live roots via `PRMPTR`/`PRMDX` table + bin list
2. Compute forward addresses — sliding compaction
3. Update pointers — rewrite all PTR-flagged DESCRs
4. Compact — `memmove` live blocks to new positions

Each SIL pass (GCT/GCBA1/GCBA2/GCLAD/GCLAP/GCLAM) becomes a C `while` loop.

---

## Milestone M3 — String Operations `sil_strings.c / sil_strings.h`

**Source:** v311.sil §5 GENVAR family + §4 DTREP + string helpers in §23
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_strings.c`
**Status:** ⬜

```c
/* String block layout in arena (mirrors SIL BCDFLD, ATTRIB, LNKFLD) */
/* At arena offset `base`:
     [0..DESCR_SZ-1]     : title DESCR  (f=STTL|TTL, v=string_length)
     [DESCR_SZ..2*DS-1]  : attrib DESCR (label slot)
     [2*DS..3*DS-1]      : link DESCR   (hash chain, a=next bucket offset)
     [3*DS..3*DS+len-1]  : string bytes (BCDFLD)                        */

/* Access macros (arena offsets) */
#define STR_TITLE(base)   ((DESCR*)A2P(base))
#define STR_ATTRIB(base)  ((DESCR*)A2P((base)+ATTRIB))
#define STR_LINK(base)    ((DESCR*)A2P((base)+LNKFLD))
#define STR_DATA(base)    ((char*)A2P((base)+BCDFLD))
#define STR_LEN(base)     (STR_TITLE(base)->v)

/* Spec accessors */
#define SP_PTR(sp)   ((char*)A2P((sp)->a) + (sp)->o)
#define SP_LEN(sp)   ((sp)->l)

/* apdsp: append sp2 onto sp1 buffer — mirrors SIL APDSP */
void apdsp(SPEC *base, const SPEC *str);

/* remsp: sp1 = sp2 minus leading match of sp3 — mirrors SIL REMSP */
void remsp(SPEC *result, const SPEC *src, const SPEC *remove);

/* subsp: substring — mirrors SIL SUBSP */
void subsp(SPEC *result, const SPEC *src, DESCR *args);

/* trimsp: trim trailing blanks — mirrors SIL TRIMSP */
void trimsp(SPEC *result, const SPEC *src);

/* lexcmp: lexicographic compare — mirrors SIL LEXCMP */
int lexcmp(const SPEC *a, const SPEC *b);

/* spcint: parse integer from spec — mirrors SIL SPCINT */
/* Returns 1 on success (sets *out), 0 on failure */
int spcint(DESCR *out, const SPEC *sp);

/* spreal: parse real from spec — mirrors SIL SPREAL */
int spreal(DESCR *out, const SPEC *sp);

/* realst: format real to spec — mirrors SIL REALST */
void realst(SPEC *out, DESCR *d);

/* intspc: format integer to spec — mirrors SIL INTSPC */
void intspc(SPEC *out, DESCR *d);

/* DTREP: produce data type name — mirrors SIL DTREP proc */
/* Returns SPEC* pointing to type name string */
SPEC *DTREP(DESCR *d, SPEC *result_buf);
```

---

## Milestone M4 — Symbol Table `sil_symtab.c / sil_symtab.h`

**Source:** v311.sil §4 AUGATL, CODSKP, FINDEX
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_symtab.c`
**Status:** ⬜

```c
/* OBLIST: the 8192-bin hash table — array of DESCR (arena offset in .a) */
/* Declared in sil_data.c as: DESCR OBLIST[OBARY]; */

/* hash: compute hash bin index — mirrors SIL hash algorithm */
/* (sum of chars, shifted right by OBSFT, masked to OBSIZ-1) */
int hash(const SPEC *sp);

/* FINDEX: find or create function descriptor block for name */
/* Mirrors SIL FINDEX proc exactly */
/* Returns arena offset of function descriptor block */
int32_t FINDEX(SPEC *name_sp);

/* AUGATL: augment attribute list — append (key, val) DESCR pair */
/* Mirrors SIL AUGATL proc */
/* a1ptr=list head, a2ptr=key DESCR, a3ptr=val DESCR, a4ptr=new-pair arena off */
void AUGATL(int32_t *list_head, DESCR *key, DESCR *val);

/* CODSKP: skip over code nodes in object code block */
/* Mirrors SIL CODSKP — advances OCICL past n non-FNC descriptors */
void CODSKP(int32_t base, int32_t *offset, int n);

/* locapt: locate in attribute list by key */
/* Mirrors SIL LOCAPT — returns pointer to value DESCR or NULL */
DESCR *locapt(int32_t atl_off, DESCR *key_descr);

/* locapv: locate in value list */
DESCR *locapv(int32_t atl_off, DESCR *key_descr);
```

---

## Milestone M5 — Arithmetic and Predicates `sil_arith.c / sil_arith.h`

**Source:** v311.sil §9 lines 2923–3118
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_arith.c`
**Status:** ⬜

### ARITH dispatch table

SIL uses `SELBRA` on a type-pair index to dispatch arithmetic. In C this is a
`switch` on `(left_type * 16 + right_type)` after coercing to numeric.

```c
/* Return conventions throughout arith.c:
   - Success: fill *result, return 1
   - Failure: return 0  (FAIL — no result)
   - Error:   call sil_error(code), does not return  */

typedef enum { FAIL=0, OK=1 } SilResult;

SilResult ADD(DESCR *result, DESCR *a, DESCR *b);
SilResult SUB(DESCR *result, DESCR *a, DESCR *b);
SilResult MPY(DESCR *result, DESCR *a, DESCR *b);
SilResult DIV(DESCR *result, DESCR *a, DESCR *b);   /* error 2 on zero */
SilResult EXPOP(DESCR *result, DESCR *a, DESCR *b); /* a**b */
SilResult REMDR(DESCR *result, DESCR *a, DESCR *b); /* remainder */
SilResult INTGER(DESCR *result, DESCR *a);          /* INTEGER(x) */
SilResult MNS(DESCR *result, DESCR *a);             /* unary minus */
SilResult PLS(DESCR *result, DESCR *a);             /* unary plus (coerces) */

/* Numeric predicates: succeed (result=NULVCL) or fail */
SilResult EQ(DESCR *result, DESCR *a, DESCR *b);
SilResult NE(DESCR *result, DESCR *a, DESCR *b);
SilResult GT(DESCR *result, DESCR *a, DESCR *b);
SilResult GE(DESCR *result, DESCR *a, DESCR *b);
SilResult LT(DESCR *result, DESCR *a, DESCR *b);
SilResult LE(DESCR *result, DESCR *a, DESCR *b);

/* Internal: coerce DESCR to numeric (integer or real) */
/* Mirrors SIL ARITH's INTVAL/SPREAL calls */
static SilResult arith_coerce(DESCR *out, DESCR *d);
```

---

## Milestone M6 — Argument Evaluation `sil_argval.c / sil_argval.h`

**Source:** v311.sil §8 lines 2679–2922: ARGVAL EXPVAL EXPEVL EVAL INTVAL PATVAL VARVAL VARVUP VPXPTR XYARGS
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_argval.c`
**Status:** ⬜

```c
/* The interpreter state saved/restored by EXPVAL */
typedef struct {
    DESCR OCBSCL, OCICL;    /* code base + index */
    DESCR PATBCL, PATICL;   /* pattern base + index */
    DESCR WPTR, XCL, YCL, TCL;
    DESCR MAXLEN, LENFCL;
    DESCR PDLPTR, PDLHED;
    DESCR NAMICL, NHEDCL;
    SPEC  HEADSP, TSP, TXSP, XSP;
} Interp_state;

#define EXPVAL_DEPTH  64
static Interp_state expval_stack[EXPVAL_DEPTH];
static int         expval_top = 0;

/* ARGVAL: fetch next argument from object code stream */
/* Mirrors SIL ARGVAL: advances OCICL, handles FNC bit → calls INVOKE */
SilResult ARGVAL(DESCR *result);

/* VARVAL: coerce DESCR to STRING */
SilResult VARVAL(DESCR *result, DESCR *d);

/* INTVAL: coerce DESCR to INTEGER */
SilResult INTVAL(DESCR *result, DESCR *d);

/* PATVAL: coerce DESCR to PATTERN */
SilResult PATVAL(DESCR *result, DESCR *d);

/* VARVUP: VARVAL + uppercase */
SilResult VARVUP(DESCR *result, DESCR *d);

/* VPXPTR: fetch and evaluate indirect (for array subscripts) */
SilResult VPXPTR(DESCR *result);

/* XYARGS: evaluate two arguments for binary operators */
void XYARGS(DESCR *x, DESCR *y);

/* EXPVAL: execute EXPRESSION type with full state save/restore */
/* Mirrors SIL EXPVAL's 14-DESCR + 4-SPEC push */
SilResult EXPVAL(DESCR *result, DESCR *expr_d);

/* EXPEVL: EXPVAL returning by name (NAMEXN path in NMD) */
SilResult EXPEVL(DESCR *result, DESCR *expr_d);
```

---

## Milestone M7 — Pattern-Valued Functions `sil_patval.c / sil_patval.h`

**Source:** v311.sil §10 lines 3119–3322: ANY BREAKX BREAK NOTANY SPAN LEN POS RPOS RTAB TAB ARBNO ATOP NAM DOL OR
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_patval.c`
**Status:** ⬜

### Pattern node in arena

```c
/* Pattern node — NODESZ = 3*DESCR_SZ in SIL §1 */
/* Layout at arena offset base:
     [0]         : kind DESCR (v = XANYC / XBRKC / etc.)
     [DESCR_SZ]  : data DESCR (cset offset, integer n, or sub-pat offset)
     [2*DESCR_SZ]: next DESCR (next node in sequence, 0=end)            */

#define PAT_KIND(base)  (&((DESCR*)A2P(base))[0])
#define PAT_DATA(base)  (&((DESCR*)A2P(base))[1])
#define PAT_NEXT(base)  (&((DESCR*)A2P(base))[2])

/* allocate a pattern node in arena; return its offset */
static int32_t pat_alloc(int kind, int32_t data_a, int32_t data_v);

/* Pattern-valued functions — each returns arena offset of PatNode */
/* or 0 on FAIL (invalid arg) */
int32_t ANY(SPEC *cset_sp);
int32_t BREAK(SPEC *cset_sp);
int32_t BREAKX(SPEC *cset_sp);
int32_t NOTANY(SPEC *cset_sp);
int32_t SPAN(SPEC *cset_sp);
int32_t LEN(DESCR *n_d);        /* error if n < 0 */
int32_t POS(DESCR *n_d);
int32_t RPOS(DESCR *n_d);
int32_t RTAB(DESCR *n_d);
int32_t TAB(DESCR *n_d);
int32_t ARBNO(int32_t inner_pat);
int32_t ATOP(SPEC *var_sp);     /* cursor capture (@VAR) */
int32_t NAM(SPEC *var_sp, int32_t pat);  /* conditional assign (.VAR) */
int32_t DOL(SPEC *var_sp, int32_t pat);  /* immediate assign ($VAR) */
int32_t OR(int32_t left, int32_t right); /* alternation */

/* LPRTND: make ARBNO predecessor node (ONAR kind) */
int32_t LPRTND(int32_t inner_pat);
```

---

## Milestone M8 — Pattern Matching Engine `sil_scan.c / sil_scan.h`

**Source:** v311.sil §11 lines 3323–4239: SCAN SJSR SCNR + 27 sub-procedures
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_scan.c`
**Status:** ✅ committed one4all `c762e496` (hardest milestone)

### Design: C call stack replaces PDLPTR

The SIL pattern stack (`PDLPTR`/`PDLHED`, `SPDLSZ=8000` DESCRs) is the explicit
backtrack stack. In C it becomes the call stack via recursion + `setjmp`/`longjmp`.
Every SIL scan sub-procedure becomes a C function. Backtracking is a `longjmp`.

```c
/* Scan state — mirrors SIL globals used during matching */
typedef struct {
    const char *subject;   /* HEADSP / SP_PTR(&TXSP) */
    int32_t     sublen;    /* LENFCL */
    int32_t     cursor;    /* PDLPTR current position */
    int32_t     anchor;    /* ANCCL (0=unanchored) */
    jmp_buf    *fail_jmp;  /* current failure continuation */
} Scan_ctx;

/* SCAN: outer loop — try pattern at each position in subject */
/* Returns 1 on match (fills match_start, match_end), 0 on failure */
int SCAN(Scan_ctx *ctx, int32_t pat_off,
         int32_t *match_start, int32_t *match_end);

/* SCNR: try pattern at current cursor position */
/* Mirrors SIL SCNR — returns 1 on match, 0 on failure */
static int SCNR(Scan_ctx *ctx, int32_t pat_off);

/* Each SIL scan sub-procedure becomes one C function */
/* They call SCNR recursively for the successor node */
/* On failure: longjmp(*ctx->fail_jmp, 1) */
static int ANYC(Scan_ctx *ctx,  int32_t pat_off); /* XANYC */
static int BRKC(Scan_ctx *ctx,  int32_t pat_off); /* XBRKC */
static int BRKX(Scan_ctx *ctx,  int32_t pat_off); /* XBRKX */
static int BRKXF(Scan_ctx *ctx, int32_t pat_off); /* XBRKXF */
static int NNYC(Scan_ctx *ctx,  int32_t pat_off); /* XNNYC */
static int SPNC(Scan_ctx *ctx,  int32_t pat_off); /* XSPNC */
static int LNTH(Scan_ctx *ctx,  int32_t pat_off); /* XLNTH */
static int POSI(Scan_ctx *ctx,  int32_t pat_off); /* XPOSI */
static int RPSI(Scan_ctx *ctx,  int32_t pat_off); /* XRPSI */
static int TB(Scan_ctx *ctx,    int32_t pat_off); /* XTB   */
static int RTB(Scan_ctx *ctx,   int32_t pat_off); /* XRTB  */
static int ARBN(Scan_ctx *ctx,  int32_t pat_off); /* XARBN */
static int FARB(Scan_ctx *ctx,  int32_t pat_off); /* XFARB */
static int ONAR(Scan_ctx *ctx,  int32_t pat_off); /* XONAR */
static int ATP(Scan_ctx *ctx,   int32_t pat_off); /* XATP  */
static int BAL(Scan_ctx *ctx,   int32_t pat_off); /* XBAL  */
static int BALF(Scan_ctx *ctx,  int32_t pat_off); /* XBALF */
static int CHR(Scan_ctx *ctx,   int32_t pat_off); /* XCHR  */
static int STAR(Scan_ctx *ctx,  int32_t pat_off); /* XSTAR */
static int DSAR(Scan_ctx *ctx,  int32_t pat_off); /* XDSAR */
static int FNCE(Scan_ctx *ctx,  int32_t pat_off); /* XFNCE */
static int NME(Scan_ctx *ctx,   int32_t pat_off); /* XNME  */
static int ENME(Scan_ctx *ctx,  int32_t pat_off); /* XENME */
static int DNME(Scan_ctx *ctx,  int32_t pat_off); /* XDNME */
static int ENMI(Scan_ctx *ctx,  int32_t pat_off); /* XENMI */
static int SUCE(Scan_ctx *ctx,  int32_t pat_off); /* XSUCF */
static int SCOK(Scan_ctx *ctx,  int32_t pat_off); /* XSCOK */
static int SCON(Scan_ctx *ctx,  int32_t pat_off); /* XSCON */
static int FAIL_box(Scan_ctx *ctx, int32_t pat_off); /* XFAIL */

/* Dispatch table indexed by XANYC..XSUCF */
static int (*scan_dispatch[])(Scan_ctx*, int32_t) = {
    NULL,    /* 0 unused */
    ANYC, FARB, ARBN, ATP,  CHR,  BAL,  BALF, BRKC,
    BRKX, BRKXF, DNME, DNME, ONAR, DSAR, ENME, ENMI,
    FARB, NME,  LNTH, NME,  NNYC, ONAR, ONRF, POSI,
    RPSI, RTB,  FAIL_box, SALF, SCOK, SCON, SPNC,
    STAR, TB,   RTNL3, FNCE, SUCE
};

/* SJSR: scan-and-replace — after match, do replacement */
/* Mirrors SIL SJSR */
int SJSR(Scan_ctx *ctx, int32_t pat_off, SPEC *repl_sp,
         SPEC *result_subject);
```

---

## Milestone M9 — Naming List `sil_nmd.c / sil_nmd.h`

**Source:** v311.sil §11 NME/ENME/DNME/ENMI + §17 NMD/NMD1-5/NMDIC/NAMEXN
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_nmd.c`
**Status:** ✅ committed one4all `05a53465`

```c
/* Naming list entry — mirrors SIL NBSPTR/NAMICL pair-list layout */
typedef struct {
    SPEC   substr;      /* captured substring specifier */
    DESCR  target;     /* target variable DESCR (DT_S, DT_K, or DT_E) */
} Name_entry;

#define NAM_MAX  256
static Name_entry  nam_buf[NAM_MAX];
static int       NHEDCL_idx = 0;   /* save point (mirrors SIL NHEDCL) */
static int       NAMICL_idx = 0;   /* current top (mirrors SIL NAMICL) */

/* NAM_push: called from NME/DNME/ENME/ENMI during match */
void NAM_push(SPEC *substr, DESCR *target);

/* NAM_save: save current top → return cookie (mirrors NHEDCL snapshot) */
int NAM_save(void);

/* NMD: commit all captures since cookie — mirrors SIL NMD proc */
/* Walks buf[cookie..top], assigns each to its target variable */
void NMD(int cookie);

/* NAM_discard: on pattern failure — restore to cookie */
void NAM_discard(int cookie);

/* NMDIC: keyword assignment through SPCINT — mirrors SIL NMDIC */
/* target is DT_K type; coerce substr to integer */
static void NMDIC(SPEC *substr, DESCR *kw_target);

/* NAMEXN: EXPRESSION variable assignment — mirrors SIL NAMEXN */
/* target is DT_E type; evaluate substr as expression, assign */
static void NAMEXN(SPEC *substr, DESCR *expr_target);
```

---

## Milestone M10 — Assignment and Core Operations `sil_asgn.c / sil_asgn.h`

**Source:** v311.sil §17 lines 5828–6101: ASGN ASGNV ASGNVV ASGNVP ASGNC ASGNIC CONCAT IND KEYWRD LIT NAME NMD STR
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_asgn.c`
**Status:** ✅ committed one4all `1ec81e7e`

```c
/* ASGN: full assignment with all SIL hooks */
/* Steps (from v311.sil ASGN):
   1. Fetch subject (FNC→INVOKE if needed)
   2. K-type → ASGNIC
   3. Fetch value (FNC→INVOKE if needed)
   4. INPUT assoc check (INSW / LOCAPV / PUTIN)
   5. PUTDC: write value to subject slot
   6. OUTPUT assoc check → PUTOUT
   7. TRACE value check → TRPHND
   8. Return value (for embedded assign)                          */
SilResult ASGN(DESCR *subject, DESCR *value, DESCR *result);

/* ASGNIC: keyword assignment — coerce value through INTVAL */
SilResult ASGNIC(DESCR *kw_descr, DESCR *value);

/* CONCAT: string concatenation — mirrors SIL CONCAT */
SilResult CONCAT(DESCR *result, DESCR *a, DESCR *b);

/* IND: $X indirect reference */
SilResult IND(DESCR *result, DESCR *name_d);

/* KEYWRD: &KW lookup — returns DESCR by keyword name */
SilResult KEYWRD(DESCR *result, SPEC *kw_name_sp);

/* NAME: .X → DT_N descriptor pointing at variable's storage */
SilResult NAME(DESCR *result, SPEC *var_name_sp);

/* LIT: push literal value (integer, real, or string) */
/* Mirrors SIL LIT proc */
SilResult LIT(DESCR *result, DESCR *literal_d);

/* STR: unevaluated expression — wrap DESCR in CODE type */
SilResult STR(DESCR *result, DESCR *code_d);
```

---

## Milestone M11 — Predicates `sil_pred.c / sil_pred.h`

**Source:** v311.sil §18 lines 6102–6321
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_pred.c`
**Status:** ✅ committed one4all `bcee98ac`

```c
/* All predicates: return OK (result=NULVCL) or FAIL */
SilResult DIFFER(DESCR *result, DESCR *a, DESCR *b);
SilResult IDENT(DESCR *result, DESCR *a, DESCR *b);
SilResult FUNCTN(DESCR *result, DESCR *a);           /* FUNCTION(X) */
SilResult LABEL(DESCR *result, DESCR *a);            /* LABEL(X) */
SilResult NEG(DESCR *result, DESCR *a);              /* ~X negation predicate */
SilResult QUES(DESCR *result, DESCR *a);             /* ?X */
SilResult LEQ(DESCR *result, DESCR *a, DESCR *b);   /* string <= */
SilResult LGE(DESCR *result, DESCR *a, DESCR *b);   /* string >= */
SilResult LGT(DESCR *result, DESCR *a, DESCR *b);   /* string >  */
SilResult LLE(DESCR *result, DESCR *a, DESCR *b);   /* string <= */
SilResult LLT(DESCR *result, DESCR *a, DESCR *b);   /* string <  */
SilResult LNE(DESCR *result, DESCR *a, DESCR *b);   /* string != */
SilResult CHAR(DESCR *result, DESCR *n_d);           /* CHAR(n) */
SilResult LPAD(DESCR *result, DESCR *s, DESCR *n);  /* LPAD(s,n) */
SilResult RPAD(DESCR *result, DESCR *s, DESCR *n);  /* RPAD(s,n) */
```

---

## Milestone M12 — Other Functions `sil_func.c / sil_func.h`

**Source:** v311.sil §19 lines 6322–7037
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_func.c`
**Status:** ⬜

```c
SilResult APPLY(DESCR *result, DESCR *fname, DESCR *args, int nargs);
SilResult ARG(DESCR *result, DESCR *fname, DESCR *n);
SilResult LOCAL(DESCR *result, DESCR *fname, DESCR *n);
SilResult FIELDS(DESCR *result, DESCR *typename_d);
SilResult CLEAR(DESCR *result);
SilResult CMA(DESCR *result, DESCR *a, DESCR *b);   /* string compare */
SilResult COLECT(DESCR *result);                      /* COLLECT() — force GC */
SilResult COPY(DESCR *result, DESCR *a);
SilResult CNVRT(DESCR *result, DESCR *val, DESCR *type_name); /* CONVERT */
SilResult DATE(DESCR *result, DESCR *opt_fmt);
SilResult DT(DESCR *result, DESCR *a);               /* DATATYPE(X) */
SilResult DMP(DESCR *result, DESCR *a);              /* DUMP level */
SilResult DUMP(DESCR *result, DESCR *a);
SilResult DUPL(DESCR *result, DESCR *s, DESCR *n);  /* DUPL(s,n) */
SilResult OPSYN(DESCR *result, DESCR *a, DESCR *b, DESCR *type_d);
SilResult RPLACE(DESCR *result, DESCR *s, DESCR *p, DESCR *r);
SilResult REVERS(DESCR *result, DESCR *s);
SilResult SIZE(DESCR *result, DESCR *s);
SilResult TIME(DESCR *result);
SilResult TRIM(DESCR *result, DESCR *s);
SilResult VDIFFR(DESCR *result, DESCR *a, DESCR *b);/* VDIFFER */
```

---

## Milestone M13 — Arrays, Tables, Data Objects `sil_arrays.c / sil_arrays.h`

**Source:** v311.sil §14 lines 4644–5267
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_arrays.c`
**Status:** ⬜

```c
/* Array block in arena:
     title DESCR (TTL, V=total_bytes)
     prototype DESCR
     lo DESCR, hi DESCR  (lo2, hi2 for 2D)
     ndim DESCR
     data DESCRs[...]                          */

/* Table block in arena:
     title DESCR (TTL+FRZN for frozen, V=total_bytes)
     init DESCR (initial size)
     inc  DESCR (increment)
     bin  DESCRs[init*2] (key/val pairs, chained)  */

SilResult ARRAY(DESCR *result, DESCR *bounds_d);      /* ARRAY('lo:hi') */
SilResult ASSOC(DESCR *result, DESCR *init, DESCR *inc); /* TABLE(n,m) */
SilResult ITEM(DESCR *result, DESCR *arr_d, DESCR *subs, int nsubs);
SilResult DATDEF(DESCR *result, DESCR *spec_d);       /* DATA('T(f1,f2)') */
SilResult PROTO(DESCR *result, DESCR *typename_d);    /* PROTOTYPE(X) */
SilResult FREEZE(DESCR *result, DESCR *table_d);
SilResult THAW(DESCR *result, DESCR *table_d);
SilResult DEFDAT(DESCR *result, DESCR *typename_d, DESCR *args, int nargs);
SilResult FIELD(DESCR *result, DESCR *obj, DESCR *fieldname_d);
SilResult RSORT(DESCR *result, DESCR *arr_d, DESCR *fcmp_d);
SilResult SSORT(DESCR *result, DESCR *arr_d, DESCR *fcmp_d);
```

---

## Milestone M14 — Defined Functions `sil_define.c / sil_define.h`

**Source:** v311.sil §12 lines 4240–4470: DEFINE DEFFNC
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_define.c`
**Status:** ⬜

```c
/* Function block in arena: FBKLSZ = 10*DESCR_SZ
     [0]   title DESCR (TTL, V=FBKLSZ)
     [1]   name  DESCR (STRING arena offset)
     [2]   entry DESCR (FNC bit, A=code-block offset)
     [3]   nparams DESCR (integer)
     [4]   nlocals DESCR (integer)
     [5..9] param/local name DESCRs (up to 5 inline; overflow → augmented list) */

/* DEFINE: register user-defined function */
/* Parses spec 'fname(p1,p2)l1,l2' — mirrors SIL DEFINE proc exactly */
SilResult DEFINE(DESCR *result, DESCR *spec_d, DESCR *entry_label_d);

/* DEFFNC: invoke a user-defined function */
/* Sets up new stack frame with params/locals, runs body, handles RETURN */
/* Mirrors SIL DEFFNC proc + call_user_function logic */
SilResult DEFFNC(DESCR *result, int32_t fnblk_off, DESCR *args, int nargs);

/* Function table lookup by name */
int32_t fn_lookup(SPEC *name_sp);   /* returns fnblk arena offset or 0 */
```

---

## Milestone M15 — External Functions `sil_load.c / sil_load.h`

**Source:** v311.sil §13 lines 4471–4643: LOAD UNLOAD LNKFNC
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_load.c`
**Status:** ⬜

```c
/* LOAD: load external function via dlopen/dlsym */
/* Mirrors SIL LOAD proc — parses prototype, opens library, links symbol */
SilResult LOAD(DESCR *result, DESCR *proto_d, DESCR *lib_d);

/* UNLOAD: unregister external function */
SilResult UNLOAD(DESCR *result, DESCR *proto_d);

/* LNKFNC: wire loaded function symbol into function table */
/* Mirrors SIL LNKFNC — sets FNC bit in function entry DESCR */
SilResult LNKFNC(int32_t fnblk_off, void *sym);
```

---

## Milestone M16 — I/O `sil_io.c / sil_io.h`

**Source:** v311.sil §15 lines 5268–5465: READ PRINT BKSPCE ENDFIL REWIND SET DETACH PUTIN PUTOUT
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_io.c`
**Status:** ⬜

```c
/* Unit descriptor — mirrors SIL INPUT/OUTPUT unit DESCRs */
typedef struct {
    FILE   *fp;
    int     mode;     /* IO_READ / IO_WRITE */
    int     eof;
    char   *fmt;      /* FORMAT string if any */
} Unit;

#define MAX_UNITS  32
static Unit units[MAX_UNITS];

SilResult READ(DESCR *result, DESCR *unit_d, SPEC *buf_sp);   /* INPUT */
SilResult PRINT(DESCR *unit_d, DESCR *fmt_d, SPEC *str_sp);  /* OUTPUT */
SilResult BKSPCE(DESCR *unit_d);
SilResult ENDFIL(DESCR *unit_d);
SilResult REWIND(DESCR *unit_d);
SilResult SET(DESCR *result, DESCR *unit_d, DESCR *pos_d);
SilResult DETACH(DESCR *var_d);
SilResult PUTIN(DESCR *result, DESCR *var_d, SPEC *val_sp);  /* input assoc trigger */
SilResult PUTOUT(DESCR *var_d, SPEC *val_sp);                 /* output assoc trigger */
```

---

## Milestone M17 — Tracing `sil_trace.c / sil_trace.h`

**Source:** v311.sil §16 lines 5466–5827
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_trace.c`
**Status:** ⬜

```c
SilResult TRACE(DESCR *result, DESCR *var_d, DESCR *type_d, DESCR *tag_d);
SilResult STOPTR(DESCR *result, DESCR *var_d, DESCR *type_d);
void      FENTR(SPEC *fname_sp);            /* function entry trace */
void      FENTR2(SPEC *fname_sp);           /* alternate entry trace */
void      KEYTR(SPEC *kw_name_sp);          /* keyword trace */
DESCR     TRPHND(DESCR *trace_entry_d);     /* invoke trace handler */
void      VALTR(SPEC *var_sp, DESCR *old_d, DESCR *new_d); /* value trace */
void      FNEXT2(SPEC *fname_sp);           /* function exit trace */
```

---

## Milestone M18 — Compiler `sil_compiler.c / sil_compiler.h`

**Source:** v311.sil §6 lines 1554–2519: BINOP CMPILE ELEMNT EXPR FORWRD NEWCRD TREPUB UNOP
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_compiler.c`
**Status:** ⬜ (large — ~965 SIL lines → ~1500 C lines)

The compiler is the most complex single unit. Key functions:

```c
/* CMPILE: compile one statement — top-level compiler entry */
/* Mirrors SIL CMPILE: reads from TEXTSP, emits to CMBSCL/CMOFCL */
/* Returns: COMP3 (error), XLATNX (continue), or falls through to XLATP */
typedef enum { CMPILE_OK, CMPILE_ERR, CMPILE_CONT } CmpResult;
CmpResult CMPILE(void);

/* NEWCRD: process new card type (NEWTYP/CNTTYP/CTLTYP/CMTTYP) */
/* Returns: XLATRD (read next), or falls through */
int NEWCRD(void);

/* ELEMNT: parse one element (operand) */
/* Mirrors SIL ELEMNT: returns element type via STYPE global */
int ELEMNT(void);

/* EXPR: parse expression with precedence */
/* Mirrors SIL EXPR/EXPR1/EXPR2/EXPR7 — recursive descent */
int EXPR(int min_prec);

/* BINOP: parse binary operator */
/* Returns operator function DESCR or 0 on failure */
int32_t BINOP(void);

/* UNOP: parse unary operator */
int32_t UNOP(void);

/* FORWRD: advance scanner past whitespace (mirrors SIL FORWRD) */
void FORWRD(void);

/* TREPUB: emit code tree to object code block */
void TREPUB(int32_t tree_root);

/* FORRUN: read next continuation line (mirrors SIL FORRUN) */
int FORRUN(void);
```

---

## Milestone M19 — Interpreter Executive `sil_interp.c / sil_interp.h`

**Source:** v311.sil §7 lines 2520–2678: BASE GOTG GOTL GOTO INIT INTERP INVOKE
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_interp.c`
**Status:** ⬜

```c
/* INVOKE dispatch table — indexed by function DESCR's A field */
/* Each entry is a C function pointer: SilResult (*fn)(DESCR *result, ...) */
typedef SilResult (*BuiltinFn)(DESCR *result, DESCR *args, int nargs);

typedef struct {
    const char *name;
    BuiltinFn   fn;
    int         min_args;
    int         max_args;
} Invoke_entry;

/* Built-in function table — mirrors SIL function pair list (FNLIST) */
extern Invoke_entry invoke_table[];
extern int         invoke_table_size;

/* INVOKE: dispatch one instruction from object code */
/* Mirrors SIL INVOKE/INVK1/INVK2:
   fetch DESCR at OCBSCL+OCICL; if FNC → call its function;
   else it's a data descriptor → return as argument value */
SilResult INVOKE(DESCR *result);

/* INTERP: main interpreter loop — mirrors SIL INTERP/INTRP0 */
/* Loops calling INVOKE until non-FNC DESCR or special exit */
void INTERP(void);

/* INIT: statement initialization */
/* Mirrors SIL INIT: saves FRTNCL, resets state for new statement */
void INIT(void);

/* GOTO: goto by integer offset in current code block */
void GOTO(int32_t offset);

/* GOTL: goto by label name — lookup in symbol table */
/* Returns 0 if label found (sets OCICL), 1 if not found */
int GOTL(SPEC *label_sp);

/* GOTG: computed goto :(X) — mirrors SIL GOTG/BRANIC */
/* d is a CODE descriptor; sets OCBSCL+OCICL to its code block */
void GOTG(DESCR *code_d);

/* BASE: set up new code base for function call */
void BASE(int32_t code_block_off);
```

---

## Milestone M20 — Error Handling `sil_errors.c / sil_errors.h`

**Source:** v311.sil §22 lines 10337–10480 + message strings from §23
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 -c sil_errors.c`
**Status:** ⬜

```c
/* Error codes — verbatim from v311.sil AERROR/INTR1/UNDF etc. */
typedef enum {
    ERR_ILLEGAL_TYPE    =  1,   /* INTR1   "Illegal data type" */
    ERR_ARITH           =  2,   /* AERROR  "Error in arithmetic operation" */
    ERR_ARRAY_REF       =  3,   /* NONARY  "Erroneous array or table reference" */
    ERR_NULL_STRING     =  4,   /* NONAME  "Null string in illegal context" */
    ERR_UNDEF_FUNC      =  5,   /* UNDF    "Undefined function or operation" */
    ERR_BAD_PROTO       =  6,   /* PROTER  "Erroneous prototype" */
    ERR_UNKNOWN_KW      =  7,   /* UNKNKW  "Unknown keyword" */
    ERR_VAR_MISSING     =  8,   /* NEMO    "Variable not present where required" */
    ERR_ENTRY_NOTLABEL  =  9,   /* UNDFFE  "Entry point of function not label" */
    ERR_ILLEGAL_ARG     = 10,   /* INTR30  "Illegal argument to primitive function" */
    ERR_READ            = 11,   /* COMP5   "Reading error" */
    ERR_BAD_UNIT        = 12,   /* UNTERR  "Illegal i/o unit" */
    ERR_TOO_MANY_TYPES  = 13,   /* INTR27  "Limit on defined data types exceeded" */
    ERR_NEG_NUMBER      = 14,   /* LENERR  "Negative number in illegal context" */
    ERR_STRING_OVERFLOW = 15,   /* INTR8   "String overflow" */
    ERR_PAT_OVERFLOW    = 16,   /* INTR31  "Overflow during pattern matching" */
    ERR_SYSTEM          = 17,   /* COMP3   "Error in SNOBOL4 system" */
    ERR_RETURN_LVL0    = 18,   /* MAIN1   "Return from level zero" */
    ERR_GOTO_FAIL       = 19,   /* INTR5   "Failure during goto evaluation" */
    ERR_NO_STORAGE      = 20,   /* ALOC2   "Insufficient storage to continue" */
    ERR_STACK_OVERFLOW  = 21,   /* OVER    "Stack overflow" */
    ERR_STLIMIT         = 22,   /* EXEX    "Limit on statement execution exceeded" */
    ERR_OBJ_TOO_LARGE   = 23,   /* SIZERR  "Object exceeds size limit" */
    ERR_BAD_GOTO        = 24,   /* INTR4   "Undefined or erroneous goto" */
    ERR_BAD_ARGCOUNT    = 25,   /* ARGNER  "Incorrect number of arguments" */
    ERR_COMP_LIMIT      = 26,   /* COMP9   "Limit on compilation errors exceeded" */
    ERR_BAD_END         = 27,   /* COMP7   "Erroneous END statement" */
    ERR_COMP_STMT       = 28,   /* EROR    "Execution of statement with compile error" */
    ERR_BAD_INCLUDE     = 29,   /*         "Erroneous INCLUDE statement" */
    ERR_CANT_INCLUDE    = 30,   /*         "Cannot open INCLUDE file" */
    ERR_BAD_LINE        = 31,   /*         "Erroneous LINE statement" */
    ERR_NO_END          = 32,   /* COMP1   "Missing END statement" */
    ERR_OUTPUT          = 33,   /*         "Output error" */
    ERR_USER_INT        = 34,   /* USRINT  "User interrupt" */
    ERR_NOT_IN_SETEXIT  = 35,   /* CNTERR  "Not in a SETEXIT handler" */
    ERR_CANT_CONTINUE   = 39,   /* CFTERR  "Cannot CONTINUE from FATAL error" */
} SNOBOL4_error;

/* Error message strings — verbatim from v311.sil MSG1..MSG39 */
extern const char *MSG[];   /* MSG[1]..MSG[39] */

/* Compiler error messages — EMSG1..EMSG14 */
extern const char *EMSG[];

/* FTLEND: fatal error — print message, exit */
/* Mirrors SIL FTLEND: prints FTLCF format, then exits */
void FTLEND(SNOBOL4_error code) __attribute__((noreturn));

/* FTLTST: non-fatal error — may continue via &ERRLIMIT / SETEXIT */
/* Mirrors SIL FTLTST → FTERST chain */
void FTLTST(SNOBOL4_error code);

/* FTLERR: error with FATALLIMIT check — mirrors SIL FTLERR */
void FTLERR(SNOBOL4_error code);

/* sil_error: internal error dispatch — longjmp to recovery or call FTLTST */
void sil_error(SNOBOL4_error code);

/* Error format — verbatim from v311.sil FTLCF */
/* "%v:%d: Error %d in statement %d at level %d\n" */
#define FTLCF_FMT  "%s:%d: Error %d in statement %d at level %d\n"
#define SUCCF_MSG  "No errors detected in source program\n\n"

/* Recovery point for non-fatal errors (SETEXIT) */
extern jmp_buf error_recovery;
extern int     error_recovery_set;
```

---

## Milestone M21 — Initialization and Main `sil_main.c`

**Source:** v311.sil §2 BEGIN + §21 END/FTLEND/SYSCUT + §3 compile/invoke loop
**Gate:** `gcc -Wall -Wextra -std=c99 -m32 sil_main.c sil_*.c -lm -o snobol4` links and exits cleanly on empty input
**Status:** ⬜

```c
/* BEGIN: system initialization — mirrors SIL BEGIN proc */
static void BEGIN(void) {
    arena_init();          /* M2: 128MB arena, FRSGPT/TLSGP1 */
    sil_data_init();       /* M1: initialize all named globals */
    fn_table_init();       /* M19: register all built-in functions */
    signal(SIGINT, sigint_handler);
    /* ... matches SIL BEGIN line by line ... */
}

/* END: normal termination */
static void END(void) {
    /* print statistics, flush I/O, exit(RETCOD.a) */
}

/* SYSCUT: abnormal termination */
static void SYSCUT(void) { exit(1); }

/* main: parse args, call BEGIN, run compile/interp loop */
int main(int argc, char *argv[]) {
    /* process command-line options (matches SIL GETPARM/XCALLC GETPARM) */
    BEGIN();
    /* compile loop (§3 XLATRD/XLATRN/XLATNX) */
    /* interpret (§7 INTERP) */
    END();
}
```

---

## Makefile

```makefile
CC      = gcc
CFLAGS  = -Wall -Wextra -std=c99 -m32 -g -O0

SRCS = sil_data.c sil_arena.c sil_strings.c sil_symtab.c \
       sil_arith.c sil_argval.c sil_patval.c sil_scan.c \
       sil_nmd.c sil_asgn.c sil_pred.c sil_func.c \
       sil_arrays.c sil_define.c sil_load.c sil_io.c \
       sil_trace.c sil_compiler.c sil_interp.c \
       sil_errors.c sil_main.c

OBJS = $(SRCS:.c=.o)

snobol4: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ -lm -ldl

%.o: %.c sil_types.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o snobol4
```

---

## Milestone Status Summary

| # | File | Source section | SIL lines | Status |
|---|------|---------------|-----------|--------|
| M0 | `sil_types.h` | §1 Linkage/Equates | 124 | ✅ |
| M1 | `sil_data.c/h` | §23 Data | 1804 | ⬜ |
| M2 | `sil_arena.c/h` | §5 Storage/GC | 334 | ⬜ |
| M3 | `sil_strings.c/h` | §5 GENVAR family + §4 DTREP | ~200 | ⬜ |
| M4 | `sil_symtab.c/h` | §4 Support procs | 130 | ⬜ |
| M5 | `sil_arith.c/h` | §9 Arithmetic | 195 | ⬜ |
| M6 | `sil_argval.c/h` | §8 Arg evaluation | 243 | ⬜ |
| M7 | `sil_patval.c/h` | §10 Pattern-valued | 203 | ✅ |
| M8 | `sil_scan.c/h` | §11 Pattern matching | 916 | ✅ |
| M9 | `sil_nmd.c/h` | §11+§17 NMD | ~150 | ✅ |
| M10 | `sil_asgn.c/h` | §17 Other ops | 273 | ✅ |
| M11 | `sil_pred.c/h` | §18 Predicates | 219 | ✅ |
| M12 | `sil_func.c/h` | §19 Other functions | 715 | ✅ |
| M13 | `sil_arrays.c/h` | §14 Arrays/Tables | 623 | ✅ |
| M14 | `sil_define.c/h` | §12 Defined functions | 230 | ✅ |
| M15 | `sil_io.c/h` | §15 I/O | 197 | ✅ |
| M16 | `sil_trace.c/h` | §16 Tracing | 361 | ✅ |
| M17 | `sil_extern.c/h` | §13 External functions | 172 | ✅ |
| M18 | `sil_compiler.c/h` | §6 Compiler | 965 | ⬜ |
| M19 | `sil_interp.c/h` | §7 Interpreter | 158 | ⬜ |
| M20 | `sil_errors.c/h` | §22 Errors + §23 messages | 143+msg | ⬜ |
| M21 | `sil_main.c` | §2+§3+§21 Init/main/term | ~200 | ⬜ |

**Total SIL lines translated: ~7,564** (excludes §20 BLOCKS 3,304 lines — skipped)

---

*MILESTONES.md — initial design, 2026-04-06*
*Updated: mark each ⬜ → ✅ when gate passes. Add notes below each entry as work proceeds.*
