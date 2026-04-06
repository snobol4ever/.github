# MILESTONE-V311-C.md — Faithful C Rewrite of v311.sil

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-06
**Status:** DESIGN — milestone ladder for scrip runtime ground-up rewrite

---

## The Goal

Rewrite every subsystem of v311.sil as pure functional C.

**Rules:**
- All SIL symbol names kept verbatim (`SCBSCL`, `OCICL`, `NAMICL`, `XPTR`, etc.)
- Low-level layout kept: `DESCR_t`, `SPEC_t`, `STRING_t` structs as in SIL
- Control flow: `if`/`while`/`for`/`switch` — **zero gotos**, zero `BRANCH`
- Each SIL PROC boundary becomes a C function with real parameters and return value
- RCALL chains become real C call chains — the C stack IS the SIL stack
- `RRTURN ,n` becomes `return n` (or typed enum)
- Boehm GC replaces `BLOCK`/`GC`/`GCM`/`SPLIT` entirely
- Where whole subsystems have better replacements (regex, hash libs), use them
- The generated `snobol4.c` is the reference for semantics — never the source

**What this is NOT:**
- Not a mechanical goto-to-if paste job
- Not a new language design — SIL names and SIL semantics, C control flow

---

## Source Reference

```
v311.sil sections (Table of Contents, line 582):
  1.  Linkage and Equivalences
  2.  Program Initialization
  3.  Compilation and Interpreter Invocation
  4.  Support Procedures        AUGATL CODSKP DTREP FINDEX
  5.  Storage Allocation / GC   BLOCK GENVAR GNVARI CONVAR GNVARS GC GCM SPLIT
  6.  Compilation Procedures    BINOP CMPILE ELEMNT EXPR FORWRD NEWCRD TREPUB UNOP
  7.  Interpreter Executive     BASE GOTG GOTL GOTO INIT INTERP INVOKE
  8.  Argument Evaluation       ARGVAL EXPVAL EXPEVL EVAL INTVAL PATVAL VARVAL VARVUP VPXPTR XYARGS
  9.  Arithmetic + Predicates   ADD DIV EXPOP MPY SUB EQ GE GT LE LT NE REMDR INTGER MNS PLS
  10. Pattern-Valued Functions   ANY BREAKX BREAK NOTANY SPAN LEN POS RPOS RTAB TAB ARBNO ATOP NAM DOL OR
  11. Pattern Matching           SCAN SJSR SCNR BRKC BRKX NNYC SPNC ANYC BRKXF LNTH POSI RPSI RTB TB
                                 ARBN FARB ATP BAL CHR STAR DSAR FNCE NME ENME DNME ENMI SUCE
  12. Defined Functions          DEFINE DEFFNC
  13. External Functions         LOAD UNLOAD LNKFNC
  14. Arrays / Tables / Data     ARRAY ASSOC DATDEF PROTO FREEZE THAW ITEM DEFDAT FIELD RSORT SSORT
  15. Input and Output           READ PRINT BKSPCE ENDFIL REWIND SET DETACH PUTIN PUTOUT
  16. Tracing                    TRACE STOPTR FENTR FENTR2 KEYTR TRPHND VALTR FNEXT2
  17. Other Operations           ASGN CONCAT IND KEYWRD LIT NAME NMD STR
  18. Other Predicates           DIFFER FUNCTN IDENT LABEL LEQ LGE LGT LLE LLT LNE NEG QUES
                                 CHAR LPAD RPAD
  19. Other Functions            APPLY ARG LOCAL FIELDS CLEAR CMA COLECT COPY CNVRT DATE DT DMP DUMP
                                 DUPL OPSYN RPLACE REVERS SIZE TIME TRIM VDIFFR
  20. Common Code
  21. Termination                END FTLEND SYSCUT
  22. Error Handling
  23. Data                       (all static tables, pair lists, descriptors)
```

---

## The Data Structures (Section 1 — kept verbatim)

These are NOT replaced. They are the SIL DESCR/SPEC/STRING layout in C.
Every milestone reads and writes them the same way as v311.sil.

```c
/* DESCR — the universal SIL value cell (v311.sil: ATTRIB, LNKFLD, BCDFLD, etc.) */
typedef struct {
    union { intptr_t i; double f; void *ptr; } a;  /* A field */
    unsigned char f;                                 /* F field — flags: FNC TTL STTL MARK PTR FRZN */
    unsigned int  v;                                 /* V field — type/size (24 bits in SIL) */
} DESCR_t;
#define DESCR ((int)sizeof(DESCR_t))

/* SPEC — string specifier (two adjacent DESCRs) */
typedef struct {
    intptr_t     l;   /* length */
    unsigned int o;   /* offset */
    void        *a;   /* base address */
    unsigned int v;   /* type (always S=1) */
} SPEC_t;
#define SPEC ((int)sizeof(SPEC_t))

/* STRING storage block (BCDFLD layout) */
typedef struct {
    DESCR_t title;        /* [0]: TTL flag set, V=byte-length of string */
    DESCR_t attrib;       /* [1]: label/attribute slot */
    DESCR_t link;         /* [2]: hash chain link */
    char    data[];       /* [3+]: string bytes (CPD bytes per DESCR) */
} STRING_t;

/* Flags — verbatim from v311.sil / snotypes.h */
#define FNC   01    /* function/code bit */
#define TTL   02    /* title (block header) */
#define STTL  04    /* string title */
#define MARK  010   /* GC mark */
#define PTR   020   /* pointer flag */
#define FRZN  040   /* frozen table */

/* Data type codes — verbatim from v311.sil lines 900–915 */
#define DT_S     1   /* STRING */
#define DT_B     2   /* BLOCK (internal) */
#define DT_P     3   /* PATTERN */
#define DT_A     4   /* ARRAY */
#define DT_T     5   /* TABLE */
#define DT_I     6   /* INTEGER */
#define DT_R     7   /* REAL */
#define DT_C     8   /* CODE */
#define DT_N     9   /* NAME */
#define DT_K    10   /* KEYWORD */
#define DT_E    11   /* EXPRESSION */
#define DATSTA 100   /* first user datatype */
```

---

## Milestone Ladder

### V311-C0 — Headers: EQUs, Types, Data Layout ⬜

**SIL source:** Section 1 (lines 835–960)\
**Output:** `src/runtime/sil/v311_types.h`\
**Gate:** `gcc -Wall -c v311_types.h` (no warnings)

What goes in:
- All `EQU` constants verbatim: `ATTRIB`, `LNKFLD`, `BCDFLD`, `FATHER`, `LSON`, `RSIB`,
  `CODE`, `ESASIZ`, `FBKLSZ`, `CARDSZ`, `CNODSZS`, `DATSIZ`, `EXTSIZ`, `NAMLSZ`,
  `NODESZ`, `OBSFT`, `OBSIZ`, `OBARY`, `OCASIZ`, `SPDLSZ`, `STSIZE`, etc.
- All type codes (above)
- `DESCR_t`, `SPEC_t`, `STRING_t` structs
- Pattern function indexes: `XANYC=1` through `XFNCE=35`, `XSUCF=36`
- `sil_macros.h` (already designed in MILESTONE-RT-SIL-MACROS.md) — include here

---

### V311-C1 — Storage Allocator (Section 5, minus GC) ⬜

**SIL source:** `BLOCK`, `GENVAR`, `GNVARI`, `GENVUP`, `CONVAR`, `GNVARS`\
**Output:** `src/runtime/sil/alloc.c` + `alloc.h`\
**Gate:** compiles; `GENVAR_fn` converts a `SPEC_t` to an allocated `STRING_t*`

SIL → C translation:

```c
/* BLOCK: allocate a block of n bytes, return ptr to its DESCR_t header */
/* In SIL: checks size limit, bumps FRSGPT, calls GC if full */
/* In C: GC_malloc(DESCR + n) — Boehm handles the rest */
DESCR_t *BLOCK_fn(intptr_t n);

/* GENVAR: convert specifier → interned STRING_t in GC heap */
/* SIL: LOCA1 path + GNVARI for empty string */
/* In C: look up or allocate STRING_t; return DESCR_t pointing to it */
DESCR_t GENVAR_fn(const SPEC_t *sp);

/* CONVAR: convert descriptor to variable (ensure it has heap storage) */
DESCR_t CONVAR_fn(DESCR_t d);

/* GNVARS: GENVAR for a C string (convenience) */
DESCR_t GNVARS_fn(const char *s, int len);
```

**Boehm replaces:** `GC`, `GCM`, `SPLIT`, `FRSGPT`, `TLSGP1`, `HDSGPT`,
`PRMDX`, `PRMPTR`, `OBLIST`, `OBEND` — none of these exist in the new code.
`GC_malloc` / `GC_malloc_atomic` are the only allocation calls.

---

### V311-C2 — Symbol Table (Section 23 hash bins) ⬜

**SIL source:** `OBSIZ` bin array, `LNKFLD` chaining, `ATTRIB`/`BCDFLD` layout\
**Output:** `src/runtime/sil/symtab.c` + `symtab.h`\
**Gate:** `FINDEX_fn` finds or inserts a name; `AUGATL_fn` augments a pair list

SIL → C translation:

```c
/* Symbol table: OBSIZ (8192) bins, chained by LNKFLD in STRING_t */
/* SIL: hash by OBSFT-bit shift of string bytes */
/* C: same algorithm, but chain pointers are GC_malloc'd STRING_t* */
#define OBSIZ (1 << OBSFT)   /* 8192 bins, verbatim from v311.sil */

typedef struct SymBin {
    STRING_t *head;   /* first STRING_t in this hash bucket */
} SymBin_t;

extern SymBin_t OBLIST[OBSIZ + 3];   /* verbatim name from v311.sil */

/* FINDEX: find or create symbol in hash table */
/* SIL: FINDEX uses HASH fn + LNKFLD chain walk */
STRING_t *FINDEX_fn(const char *name, int len);

/* AUGATL: augment attribute list — append (key,val) DESCR pair */
/* SIL: allocates pair, links into list at ATTRIB slot */
void AUGATL_fn(DESCR_t *atl, DESCR_t key, DESCR_t val);

/* CODSKP: skip code nodes in object code block */
/* SIL: walks CMBSCL/OCICL advancing past non-FNC descriptors */
void CODSKP_fn(DESCR_t *base, intptr_t *offset);
```

---

### V311-C3 — Arithmetic and Predicates (Section 9) ⬜

**SIL source:** `ADD`, `DIV`, `EXPOP`, `MPY`, `SUB`, `REMDR`, `INTGER`, `MNS`, `PLS`,
`EQ`, `GE`, `GT`, `LE`, `LT`, `NE`\
**Output:** `src/runtime/sil/arith.c` + `arith.h`\
**Gate:** all 14 functions compile; unit test `2 + 3 = 5`, `3.0 / 2 = 1.5`

SIL → C translation — the `ARITH` dispatch is a `switch` on type:

```c
/* ADD_fn: SNOBOL4 + operator — integer, real, or FAIL */
/* SIL ARITH: SELBRA on type pair (I/R × I/R) → ADDFN */
DESCR_t ADD_fn(DESCR_t a, DESCR_t b);
DESCR_t SUB_fn(DESCR_t a, DESCR_t b);
DESCR_t MPY_fn(DESCR_t a, DESCR_t b);
DESCR_t DIV_fn(DESCR_t a, DESCR_t b);   /* Error 2 on div-by-zero */
DESCR_t EXPOP_fn(DESCR_t a, DESCR_t b); /* exponentiation */
DESCR_t REMDR_fn(DESCR_t a, DESCR_t b); /* remainder */
DESCR_t INTGER_fn(DESCR_t a);           /* INTEGER(x) coerce */
DESCR_t MNS_fn(DESCR_t a);             /* unary minus */
DESCR_t PLS_fn(DESCR_t a);             /* unary plus — NOT identity, coerces */

/* Numeric predicates — return NULVCL on success, FAILDESCR on failure */
/* SIL: ARITH dispatch → ACOMPC/RCOMP → RETNUL or FAIL */
DESCR_t EQ_fn(DESCR_t a, DESCR_t b);
DESCR_t NE_fn(DESCR_t a, DESCR_t b);
DESCR_t GT_fn(DESCR_t a, DESCR_t b);
DESCR_t GE_fn(DESCR_t a, DESCR_t b);
DESCR_t LT_fn(DESCR_t a, DESCR_t b);
DESCR_t LE_fn(DESCR_t a, DESCR_t b);
```

Internal `ARITH` dispatch (replaces SIL SELBRA on type pair):

```c
/* Type coercion matrix — mirrors SIL ARITH SELBRA table */
static DESCR_t arith_coerce(DESCR_t d) {
    if (IS_INT(d)) return d;
    if (IS_REAL(d)) return d;
    /* string → try integer, then real */
    DESCR_t r;
    if (SPCINT_fn(&r, d.a.ptr, d.v)) return r;
    if (SPREAL_fn(&r, d.a.ptr, d.v)) return r;
    return FAILDESCR;   /* Error 1: illegal data type */
}
```

---

### V311-C4 — Argument Evaluation (Section 8) ⬜

**SIL source:** `ARGVAL`, `EXPVAL`, `EXPEVL`, `EVAL`, `INTVAL`, `PATVAL`,
`VARVAL`, `VARVUP`, `VPXPTR`, `XYARGS`\
**Output:** `src/runtime/sil/argval.c` + `argval.h`\
**Gate:** `VARVAL_fn` returns STRING descriptor; `INTVAL_fn` coerces to INTEGER

SIL → C translation:

```c
/* ARGVAL: evaluate next argument from object code stream */
/* SIL: advances OCICL, handles FNC bit → INVOKE */
DESCR_t ARGVAL_fn(void);

/* VARVAL: coerce argument to STRING */
/* SIL: ARGVAL → type switch → GENVAR (string structs) or FAIL */
DESCR_t VARVAL_fn(DESCR_t d);

/* INTVAL: coerce argument to INTEGER */
/* SIL: ARGVAL → SPCINT (parse) or RLINT (real→int) or FAIL */
DESCR_t INTVAL_fn(DESCR_t d);

/* PATVAL: coerce argument to PATTERN */
/* SIL: if STRING, compile to pattern node; if PATTERN, pass through */
DESCR_t PATVAL_fn(DESCR_t d);

/* VARVUP: VARVAL + uppercase — used by function name lookup */
DESCR_t VARVUP_fn(DESCR_t d);

/* EXPVAL: execute EXPRESSION-typed value with full state save/restore */
/* SIL: saves 14 DESCRs + 4 SPECs, sets new OCBSCL, calls INVOKE loop */
/* C: saves interpreter state struct, runs nested sm_interp(), restores */
DESCR_t EXPVAL_fn(DESCR_t expr_d);

/* EXPEVL: EXPVAL returning by NAME (for NMD NAMEXN path) */
DESCR_t EXPEVL_fn(DESCR_t expr_d);

/* XYARGS: evaluate two arguments for binary ops */
void XYARGS_fn(DESCR_t *x, DESCR_t *y);
```

**Key insight:** `EXPVAL` in C is a function that saves a small struct, calls
`sm_interp(inner_prog)`, restores the struct, and returns — no stack juggling.
The SIL's 14-DESCR save block maps to:

```c
typedef struct {
    DESCR_t  OCBSCL, OCICL;      /* code base + offset */
    DESCR_t  PATBCL, PATICL;     /* pattern base + offset */
    DESCR_t  WPTR, XCL, YCL, TCL;
    DESCR_t  MAXLEN, LENFCL;
    DESCR_t  PDLPTR, PDLHED;     /* pattern history list */
    DESCR_t  NAMICL, NHEDCL;     /* naming list */
    SPEC_t   HEADSP, TSP, TXSP, XSP;
} InterpState_t;

#define INTERP_STATE_DEPTH 64    /* max EXPVAL nesting */
static InterpState_t state_stack[INTERP_STATE_DEPTH];
static int           state_top = 0;
```

---

### V311-C5 — Pattern-Valued Functions (Section 10) ⬜

**SIL source:** `ANY`, `BREAKX`, `BREAK`, `NOTANY`, `SPAN`, `LEN`, `POS`,
`RPOS`, `RTAB`, `TAB`, `ARBNO`, `ATOP`, `NAM`, `DOL`, `OR`\
**Output:** `src/runtime/sil/patval.c` + `patval.h`\
**Gate:** `ANY_fn("aeiou", 5)` returns a PATTERN descriptor; `OR_fn(p1,p2)` builds ALT node

SIL → C translation — each becomes a function that allocates a pattern node:

```c
/* Pattern node — mirrors SIL NODESZ = 4*DESCR */
typedef struct PatNode {
    struct PatNode *next;         /* successor in sequence (RSIB) */
    int             kind;         /* XANYC, XBRKC, XLNTH, etc. */
    union {
        struct { const char *s; int len; } cset;   /* ANY/BREAK/SPAN/NOTANY */
        intptr_t                            n;      /* LEN/POS/RPOS/TAB/RTAB */
        struct PatNode                     *alt;    /* OR right branch */
        struct PatNode                     *body;   /* ARBNO inner pattern */
        const char                         *var;    /* NAM/DOL capture var */
    } u;
} PatNode_t;

DESCR_t ANY_fn(const char *cset, int len);       /* XANYC */
DESCR_t BREAK_fn(const char *cset, int len);     /* XBRKC */
DESCR_t BREAKX_fn(const char *cset, int len);    /* XBRKX */
DESCR_t NOTANY_fn(const char *cset, int len);    /* XNNYC */
DESCR_t SPAN_fn(const char *cset, int len);      /* XSPNC */
DESCR_t LEN_fn(intptr_t n);                      /* XLNTH */
DESCR_t POS_fn(intptr_t n);                      /* XPOSI */
DESCR_t RPOS_fn(intptr_t n);                     /* XRPSI */
DESCR_t TAB_fn(intptr_t n);                      /* XTB */
DESCR_t RTAB_fn(intptr_t n);                     /* XRTB */
DESCR_t ARBNO_fn(DESCR_t inner_pat);             /* XARBN */
DESCR_t ATOP_fn(const char *var);               /* XATP — cursor capture */
DESCR_t NAM_fn(const char *var, DESCR_t pat);   /* XNME — conditional assign */
DESCR_t DOL_fn(const char *var, DESCR_t pat);   /* XDNME — immediate assign */
DESCR_t OR_fn(DESCR_t left, DESCR_t right);     /* XOR — alternation */
```

---

### V311-C6 — Pattern Matching Engine (Section 11) ⬜

**SIL source:** `SCAN`, `SJSR`, `SCNR`, `BRKC`, `BRKX`, `NNYC`, `SPNC`, `ANYC`,
`BRKXF`, `LNTH`, `POSI`, `RPSI`, `RTB`, `TB`, `ARBN`, `FARB`, `ATP`, `BAL`,
`CHR`, `STAR`, `DSAR`, `FNCE`, `NME`, `ENME`, `DNME`, `ENMI`, `SUCE`\
**Output:** `src/runtime/sil/scan.c` + `scan.h`\
**Gate:** `SCAN_fn` matches `"HELLO"` against `ANY("AEIOU") LEN(3)` in `"HELLO WORLD"`

This is the heart. The SIL pattern stack (`PDLPTR`/`PDLHED`) maps to the C call stack
via recursive descent + `setjmp`/`longjmp` for backtracking.

```c
/* SCAN: outermost match loop — Section 11 entry point */
/* SIL: loops SCNR over subject, advancing cursor on failure */
/* C: returns match result + sets cursor and captured variables */

typedef struct {
    const char *subject;   /* HEADSP / TXSP */
    int         len;       /* LENFCL */
    int         cursor;    /* PDLPTR cursor position */
    int         anchor;    /* &ANCHOR keyword */
} ScanState_t;

typedef struct {
    int         matched;       /* 1 = success, 0 = failure */
    int         match_start;   /* position where match began */
    int         match_end;     /* position after last matched char */
} ScanResult_t;

/* SCAN: try pattern against subject, return match result */
/* Replaces SIL SCAN/SJSR/SCNR + all 27 match sub-procedures */
ScanResult_t SCAN_fn(ScanState_t *ss, PatNode_t *pat);

/* SCNR: basic scanner — one attempt at current cursor */
/* In C: match_node() — recursive on PatNode_t tree */
static int match_node(ScanState_t *ss, PatNode_t *pat, int pos, jmp_buf *fail);
```

Backtracking model — clean C:

```c
/* No SIL PDLPTR stack. C call stack IS the pattern stack. */
/* Each match_node() call corresponds to one SIL scan sub-procedure. */
/* On backtrack: the longjmp in the ARBNO/ALT handler unwinds naturally. */

static int match_node(ScanState_t *ss, PatNode_t *pat, int pos, jmp_buf *fail) {
    if (!pat) return pos;   /* end of pattern = success */
    switch (pat->kind) {
    case XANYC:  /* ANY(cset) — mirrors SIL ANYC */
        if (pos >= ss->len) longjmp(*fail, 1);
        if (!strchr(pat->u.cset.s, ss->subject[pos])) longjmp(*fail, 1);
        return match_node(ss, pat->next, pos + 1, fail);
    case XBRKC:  /* BREAK(cset) — mirrors SIL BRKC */
        while (pos < ss->len && !strchr(pat->u.cset.s, ss->subject[pos])) pos++;
        return match_node(ss, pat->next, pos, fail);
    case XLNTH:  /* LEN(n) — mirrors SIL LNTH */
        if (pos + pat->u.n > ss->len) longjmp(*fail, 1);
        return match_node(ss, pat->next, pos + pat->u.n, fail);
    /* ... all 27 kinds ... */
    case XOR: {  /* OR — mirrors SIL FARB/ARBN alternation */
        jmp_buf alt_fail;
        if (!setjmp(alt_fail))
            return match_node(ss, pat->u.alt, pos, &alt_fail);   /* try left */
        return match_node(ss, pat->next, pos, fail);              /* try right */
    }
    /* ... */
    }
}
```

---

### V311-C7 — Naming List / NMD (Section 17 partial + Section 11 NME/ENME/DNME) ⬜

**SIL source:** `NMD`, `NMD1`–`NMD5`, `NMDIC`, `NAMEXN`, `NME`, `ENME`, `DNME`, `ENMI`\
**SIL globals:** `NAMICL`, `NHEDCL`, `NBSPTR`\
**Output:** `src/runtime/sil/nmd.c` + `nmd.h`\
**Gate:** `.VAR` capture assigns correctly on success; discards on failure

Already designed in MILESTONE-RT-RUNTIME.md §RUNTIME-4. Full struct and API there.
This milestone writes it from the v311.sil text, not from the existing partial.

---

### V311-C8 — Assignment and Other Operations (Section 17) ⬜

**SIL source:** `ASGN`, `ASGNV`, `ASGNVV`, `ASGNVP`, `ASGNC`, `ASGNIC`,
`CONCAT`, `IND`, `KEYWRD`, `LIT`, `NAME`, `STR`\
**Output:** `src/runtime/sil/asgn.c` + `asgn.h`\
**Gate:** `X = 'hello'` assigns; `OUTPUT = X` fires output hook; `$X` indirect works

```c
/* ASGN: assignment with full SIL hook chain */
/* Steps: subject fetch → K-type route → value fetch → INPUT check →
          PUTDC write → OUTPUT hook → TRACE hook → return value */
DESCR_t ASGN_fn(DESCR_t *subject, DESCR_t value);

/* CONCAT: string concatenation — APDSP equivalent */
DESCR_t CONCAT_fn(DESCR_t a, DESCR_t b);

/* IND: $X indirect reference — DESCR(name→STRING→lookup) */
DESCR_t IND_fn(DESCR_t name_d);

/* KEYWRD: &KW access — route to keyword global by name */
DESCR_t KEYWRD_fn(const char *kw_name);
DESCR_t KEYWRD_SET_fn(const char *kw_name, DESCR_t val);

/* NAME: .X → DT_N descriptor (lvalue reference) */
DESCR_t NAME_fn(const char *varname);
```

---

### V311-C9 — Predicates and String Functions (Sections 18–19 partial) ⬜

**SIL source:** `DIFFER`, `FUNCTN`, `IDENT`, `LABEL`, `LEQ`–`LNE`, `NEG`, `QUES`,
`CHAR`, `LPAD`, `RPAD`\
`APPLY`, `ARG`, `LOCAL`, `FIELDS`, `CLEAR`, `CMA`, `COPY`, `DUPL`,
`OPSYN`, `RPLACE`, `REVERS`, `SIZE`, `TRIM`, `VDIFFR`\
**Output:** `src/runtime/sil/predicates.c` + `src/runtime/sil/strfunc.c`\
**Gate:** `DIFFER('a','b')` succeeds; `IDENT('x','x')` succeeds; `SIZE('hello')=5`

All are straightforward C functions. SIL names kept verbatim.

---

### V311-C10 — Arrays, Tables, Data Objects (Section 14) ⬜

**SIL source:** `ARRAY`, `ASSOC`, `DATDEF`, `PROTO`, `ITEM`, `DEFDAT`, `FIELD`,
`RSORT`, `SSORT`\
**Output:** `src/runtime/sil/array.c` + `src/runtime/sil/table.c`\
**Gate:** `ARRAY('3')` allocates 3-element array; `TABLE()` creates empty hash table;
`DATA('node(left,right)')` registers constructor

```c
/* Array block layout — mirrors SIL ARRBLK */
typedef struct {
    DESCR_t title;        /* header: TTL, V=total_bytes */
    DESCR_t prototype;    /* PROTO descriptor */
    DESCR_t lo, hi;       /* bounds (lo2,hi2 for 2D) */
    int     ndim;         /* dimension count */
    DESCR_t data[];       /* elements */
} ARBLK_t;

DESCR_t ARRAY_fn(const char *bounds_spec);   /* ARRAY('lo:hi') */
DESCR_t ASSOC_fn(intptr_t init, intptr_t inc); /* TABLE(n,m) */
DESCR_t ITEM_fn(DESCR_t array_or_table, DESCR_t *subscripts, int nsub);
void    DATDEF_fn(const char *spec);         /* DATA('T(f1,f2)') */
DESCR_t DEFDAT_fn(const char *typename, DESCR_t *args, int nargs);
DESCR_t FIELD_fn(DESCR_t obj, const char *fieldname);
```

---

### V311-C11 — Defined and External Functions (Sections 12–13) ⬜

**SIL source:** `DEFINE`, `DEFFNC`, `LOAD`, `UNLOAD`, `LNKFNC`\
**Output:** `src/runtime/sil/define.c` + `src/runtime/sil/load.c`\
**Gate:** `DEFINE('f(x)y')` registers; `f('hello')` calls body; `LOAD` via dlopen

```c
/* Function descriptor block — FBKLSZ = 10*DESCR */
typedef struct {
    DESCR_t title;         /* block header */
    DESCR_t name;          /* function name (STRING) */
    DESCR_t entry;         /* code entry DESCR (FNC bit set) */
    DESCR_t nparams;       /* formal parameter count */
    DESCR_t nlocals;       /* local variable count */
    DESCR_t params[5];     /* inline param/local name slots */
} FNBLK_t;

void    DEFINE_fn(const char *spec, const char *entry_label);
DESCR_t DEFFNC_fn(const char *name, DESCR_t *args, int nargs);
DESCR_t LOAD_fn(DESCR_t proto_d, DESCR_t lib_d);   /* dlopen/dlsym */
void    UNLOAD_fn(DESCR_t proto_d);
DESCR_t LNKFNC_fn(const char *proto, void *sym);   /* wire loaded symbol */
```

---

### V311-C12 — I/O (Section 15) ⬜

**SIL source:** `READ`, `PRINT`, `BKSPCE`, `ENDFIL`, `REWIND`, `SET`, `DETACH`,
`PUTIN`, `PUTOUT`\
**Output:** `src/runtime/sil/io.c` + `io.h`\
**Gate:** `INPUT` reads a line; `OUTPUT = x` prints; file association works

Thin wrappers over `io_read`/`io_print` from the existing lib — the SIL I/O
layer is already well-translated in csnobol4's `lib/`. Keep function names.

---

### V311-C13 — Tracing (Section 16) ⬜

**SIL source:** `TRACE`, `STOPTR`, `FENTR`, `FENTR2`, `KEYTR`, `TRPHND`, `VALTR`, `FNEXT2`\
**Output:** `src/runtime/sil/trace.c` + `trace.h`\
**Gate:** `TRACE('X','VALUE')` fires on assignment to X

```c
void    TRACE_fn(const char *var, const char *type);   /* register trace */
void    STOPTR_fn(const char *var, const char *type);  /* remove trace */
DESCR_t TRPHND_fn(DESCR_t trace_entry);               /* invoke handler */
void    FENTR_fn(const char *fname);   /* function entry trace */
void    KEYTR_fn(const char *kw);      /* keyword trace */
void    VALTR_fn(const char *var, DESCR_t old_val, DESCR_t new_val); /* value trace */
```

---

### V311-C14 — Interpreter Executive (Section 7) ⬜

**SIL source:** `BASE`, `GOTG`, `GOTL`, `GOTO`, `INIT`, `INTERP`, `INVOKE`\
**Output:** `src/runtime/sil/interp.c` + `interp.h`\
**Gate:** `INTERP_fn` executes a compiled program object-code block

This is `sm_interp.c` — the SM dispatch loop. But written from v311.sil directly,
not from the existing tree-walk. Each SIL proc maps exactly:

```c
/* INTERP: main interpreter loop — v311.sil line ~2488 */
/* SIL: loop: OCICL += DESCR; fetch; if FNC → INVOKE; else handle fail/goto */
/* C: while loop over SM_Program; switch on SM_Op */
void INTERP_fn(SM_Program *prog);

/* INVOKE: dispatch one instruction descriptor */
/* SIL: INVK1 = BRANIC (cast A field to func ptr, call it) */
/* C: call function pointer from INVOKE_table[instr.op] */
DESCR_t INVOKE_fn(const SM_Instr *instr);

/* GOTO: goto by label offset */
/* SIL: GOTO advances OCICL to offset */
void GOTO_fn(SM_Program *prog, int *pc, intptr_t offset);

/* GOTL: goto by label name (looks up in label table) */
/* SIL: GOTL uses FINDEX to find label's code address */
int GOTL_fn(SM_Program *prog, const char *label);

/* GOTG: computed goto :(X) — SIL BRANIC */
/* C: SM_JUMP_INDIR — PC = code block address from descriptor */
void GOTG_fn(SM_Program *prog, int *pc, DESCR_t code_d);

/* INIT: statement initialization (SIL line ~2447) */
/* Resets fail pointer, saves OCBSCL/OCICL, sets FRTNCL */
void INIT_fn(void);
```

---

### V311-C15 — Initialization and Termination (Sections 2, 21, 22) ⬜

**SIL source:** `BEGIN`, `INIT` (program), `END`, `END0`, `FTLEND`, `FTLEN2`,
`ENDALL`, `SYSCUT`, `AERROR` + all error handlers\
**Output:** `src/runtime/sil/main.c`\
**Gate:** program starts, runs, exits cleanly with correct statistics

```c
void BEGIN_fn(void);    /* system init: Boehm GC, symbol table, builtins */
void END_fn(void);      /* normal termination: print stats, flush I/O */
void FTLEND_fn(int errcode, const char *msg);  /* fatal error: print + exit */
void SYSCUT_fn(void);   /* abnormal termination (signal) */

/* Error dispatch — replaces SIL AERROR + INTR* + COMP* labels */
/* C: enum + longjmp from error site to nearest recovery handler */
typedef enum {
    ERR_ILLEGAL_TYPE   =  1,
    ERR_DIVIDE_ZERO    =  2,
    ERR_ARRAY_BOUNDS   =  3,
    ERR_UNDEF_FUNC     =  5,
    ERR_STACK_OVERFLOW = 13,
    /* ... all SIL error codes verbatim ... */
} SnoError_t;

void sno_error(SnoError_t code, const char *msg);  /* longjmp to handler */
```

---

### V311-C16 — Static Data (Section 23) ⬜

**SIL source:** All data definitions — pair lists, switches, constants, pointers to patterns,
function descriptors, function table, string storage bin list, system arrays, stack,
primitive patterns, error messages, formats\
**Output:** `src/runtime/sil/data.c` + `data.h`\
**Gate:** all global DESCRs initialized; `NULVCL`, `FAILDESCR`, keyword globals present

This is the hardest to get exactly right. Every named global in v311.sil must appear
as a named C variable. Names verbatim:

```c
extern DESCR_t NULVCL;    /* null/empty string descriptor */
extern DESCR_t FAILDESCR; /* canonical failure descriptor */
extern DESCR_t XPTR, YPTR, ZPTR;   /* scratch pointer DESCRs */
extern DESCR_t WPTR, TPTR;
extern DESCR_t XCL, YCL, ZCL, WCL, TCL;  /* scratch count DESCRs */
extern DESCR_t XSPPTR, YSPPTR;     /* specifier pointer DESCRs */
extern SPEC_t  XSP, YSP, ZSP, WSP; /* scratch specifiers */
extern SPEC_t  TXSP, TSP, TEXTSP, NEXTSP, HEADSP, LNBFSP;
extern DESCR_t OCBSCL, OCICL;      /* object code base + index */
extern DESCR_t CMBSCL, CMOFCL;     /* compiler base + offset */
extern DESCR_t PATBCL, PATICL;     /* pattern base + index */
extern DESCR_t PDLPTR, PDLHED;     /* pattern history list */
extern DESCR_t NAMICL, NHEDCL;     /* naming list */
extern DESCR_t STKHED, STKEND;     /* stack bounds (Boehm-allocated) */
extern DESCR_t FRSGPT, TLSGP1;     /* free store pointers (stub — Boehm) */
/* ... all ~200 named globals ... */
```

---

## Dependency Order

```
V311-C0  (types/equates)
  └─ V311-C1  (allocator — Boehm wrappers)
       └─ V311-C2  (symbol table)
            ├─ V311-C3  (arithmetic)   ← standalone after C0
            ├─ V311-C4  (argval)       ← needs C1,C2,C3
            │    └─ V311-C5  (pattern constructors)
            │         └─ V311-C6  (pattern matching engine)
            │              └─ V311-C7  (naming list)
            ├─ V311-C8  (assignment)   ← needs C2,C4
            ├─ V311-C9  (predicates)   ← needs C2,C4
            ├─ V311-C10 (arrays/tables)← needs C1,C2
            ├─ V311-C11 (define/load)  ← needs C2,C4
            ├─ V311-C12 (I/O)          ← standalone after C0
            ├─ V311-C13 (tracing)      ← needs C8
            └─ V311-C14 (interp loop)  ← needs all above
                 └─ V311-C15 (init/main)
                      └─ V311-C16 (static data) ← woven through all
```

---

## Output Location

`one4all/src/runtime/sil/` — new directory, one `.c`/`.h` pair per milestone.
The Makefile gains a `sil` object group compiled alongside the existing runtime.

---

## Relationship to Existing Work

| Existing component | Replaced by | V311-C milestone |
|---|---|---|
| `snobol4.c` (argval + builtins) | `argval.c` + `predicates.c` + `strfunc.c` | C4, C9 |
| `stmt_exec.c` (BB-DRIVER) | remains; calls `SCAN_fn` from C6 | C6 |
| `sm_interp.c` (SM dispatch) | `interp.c` INTERP_fn | C14 |
| `snobol4.c` INVOKE table | `define.c` + `interp.c` INVOKE_fn | C11, C14 |
| Boehm GC (already used) | Boehm GC (unchanged) | C1 |
| `sil_macros.h` (already written) | extended by C0 types | C0 |

The existing `--interp` tree-walk path remains as the reference oracle until
V311-C14 is complete and passes PASS=178. Then `--interp` delegates to `INTERP_fn`.

---

## NOW (planning session — no sprint yet)

| Milestone | Estimated sessions | Blocker |
|---|---|---|
| V311-C0 | 1 | none |
| V311-C1 | 1 | C0 |
| V311-C2 | 1 | C1 |
| V311-C3 | 1 | C0 |
| V311-C4 | 2 | C1,C2,C3 |
| V311-C5 | 1 | C4 |
| V311-C6 | 2–3 | C5 ← hardest |
| V311-C7 | 1 | C6 |
| V311-C8 | 1 | C2,C4 |
| V311-C9 | 1 | C2,C4 |
| V311-C10 | 2 | C1,C2 |
| V311-C11 | 2 | C2,C4 |
| V311-C12 | 1 | C0 |
| V311-C13 | 1 | C8 |
| V311-C14 | 2 | all above |
| V311-C15 | 1 | C14 |
| V311-C16 | 1 | C0 (woven throughout) |

**Total: ~22–25 sessions to full faithful rewrite.**

---

*MILESTONE-V311-C.md — planning session 2026-04-06, Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Source: v311.sil (CSNOBOL4 2.3.3, Phil Budne 2022). Target: pure functional C, zero gotos.*
