# MILESTONE-RT-SIL-MACROS.md — SIL Macro Classification for SM + scrip-interp

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** DESIGN — feeds RT milestones and SM_Program instruction set
**Source:** `v311.sil` (CSNOBOL4 2.3.3, Phil Budne)

---

## The Question

SIL defines ~130 macro instructions and ~211 named procedures.
Which of these are **useful to us** — either as:

1. **SM_Program instructions** (stack machine ops in `SCRIP-SM.md`)
2. **C runtime functions** called by `scrip-interp` / SM dispatch
3. **Both** — same name, same semantics, in interpreter AND emitter

The SIL macro set IS the right model for our stack machine because
SIL was designed with exactly this property: each macro = one
portable, composable runtime operation. The SM_Program instruction
set in SCRIP-SM.md already captures the most important ones. This
doc fills in what's missing and classifies everything.

---

## Classification Key

| Tag | Meaning |
|-----|---------|
| **SM** | Should be / already is an SM_Program instruction |
| **RT** | Should be a named C runtime function (called from SM dispatch or scrip-interp) |
| **BOTH** | SM instruction that also has a C RT function implementing it |
| **SKIP** | Compiler/GC/IO internal — not useful for our runtime |
| **DONE** | Already implemented (SM or RT) |

---

## Group 1 — Descriptor Access (GETD / PUTD family)

These are the SIL memory model — read/write typed descriptors.
In our model these are C field accesses on `DESCR_t`.
Not SM instructions (too low-level) but should be C macros/inlines.

| SIL Macro | Operation | Our Equivalent | Tag |
|-----------|-----------|---------------|-----|
| `GETD d,base,off` | Load descriptor from base+off | `d = *(DESCR_t*)(base+off)` | RT macro |
| `PUTD base,off,d` | Store descriptor at base+off | `*(DESCR_t*)(base+off) = d` | RT macro |
| `GETDC d,base,off` | Load from C-struct field | field access on struct | RT macro |
| `PUTDC base,off,d` | Store to C-struct field | field access on struct | RT macro |
| `GETAC d,base,off` | Load address (pointer field) | pointer dereference | RT macro |
| `PUTAC base,off,d` | Store address | pointer store | RT macro |
| `MOVD dst,src` | Copy descriptor | `dst = src` | RT macro |
| `MOVDIC dst,doff,src,soff` | Copy descriptor indirect | struct copy | RT macro |
| `MOVV dst,src` | Copy value field only | `dst.v = src.v` | RT macro |
| `MOVA dst,src` | Copy address field | `dst.ptr = src.ptr` | RT macro |
| `MOVBLK dst,src,sz` | Copy block | `memcpy` | RT macro |

**Decision:** These become a `sil_macros.h` header of C `#define` / `static inline`.
Not SM instructions. Used by every RT function.

---

## Group 2 — Type Test and Comparison

| SIL Macro | Operation | SM? | RT? |
|-----------|-----------|-----|-----|
| `TESTF d,type,eq,ne` | Test data type flag | — | **RT** `TESTF(d,T)` → bool |
| `TESTFI d,type,off,eq,ne` | Test type at indirect | — | **RT** |
| `VEQLC d,type,t,f` | Value (type) == constant? | — | **RT** `VEQLC(d,T)` |
| `VEQL d1,d2,t,f` | Value types equal? | — | **RT** |
| `DEQL d1,d2,t,f` | Descriptors identical? | — | **RT** |
| `AEQLC d,val,t,f` | Address == constant? | — | **RT** |
| `AEQL d1,d2,t,f` | Addresses equal? | — | **RT** |
| `ACOMP d1,d2,lt,eq,gt` | Compare addresses (integers) | **SM** `SM_ACOMP` | **RT** |
| `ACOMPC d,val,lt,eq,gt` | Compare address vs constant | **SM** | **RT** |
| `LCMP` | Compare lengths | — | **RT** |
| `LCOMP` | Length compare | — | **RT** |
| `LEQLC sp,n,t,f` | Length of specifier == n? | — | **RT** |
| `RCOMP d1,d2,lt,eq,gt` | Compare reals | **SM** `SM_RCOMP` | **RT** |
| `VCMPIC d,type,off,t,f` | Type compare indirect | — | **RT** |
| `VCOMPC d,type,t,f` | Value compare constant | — | **RT** |

**SM additions from this group:** `SM_ACOMP`, `SM_RCOMP` (integer/real compare for
arithmetic predicates EQ/GT/LT/etc. — currently these are SM_CALL to builtin;
making them native SM ops eliminates dispatch overhead).

---

## Group 3 — Arithmetic on Addresses/Integers

| SIL Macro | Operation | SM? | RT? |
|-----------|-----------|-----|-----|
| `INCRA d,n` | d += n (address/integer) | **SM** `SM_INCR` | **RT** |
| `DECRA d,n` | d -= n | **SM** `SM_DECR` | **RT** |
| `SUM d,a,b` | d = a + b | **SM** `SM_ADD` (DONE) | **RT** |
| `MULT d,a,b` | d = a * b | **SM** `SM_MUL` (DONE) | **RT** |
| `MULTC d,a,c` | d = a * constant | — | **RT** |
| `DIVIDE d,a,b` | d = a / b | **SM** `SM_DIV` (DONE) | **RT** |
| `SUBTRT d,a,b` | d = a - b | **SM** `SM_SUB` (DONE) | **RT** |
| `ADDLG d,sp` | d += length of specifier | — | **RT** |
| `ADREAL d,x,y` | d = x + y (reals) | — | **RT** |
| `MPREAL d,x,y` | d = x * y (reals) | — | **RT** |
| `DVREAL d,x,y` | d = x / y (reals) | — | **RT** |
| `SBREAL d,x,y` | d = x - y (reals) | — | **RT** |
| `MNSINT d,x,br,ok` | d = -x (integer, overflow→br) | — | **RT** `NEG_I` |
| `MNREAL d,x` | d = -x (real) | — | **RT** `NEG_R` |
| `INTRL d,x` | d = (real)x (int→real) | — | **RT** `INT_TO_REAL` |
| `RLINT d,x,f,ok` | d = (int)x (real→int, fail→f) | — | **RT** `REAL_TO_INT` |
| `EXREAL d,x,y,err,ok` | d = x**y (reals) | — | **RT** `EXP_R` |

---

## Group 4 — String / Specifier Operations

These are the most directly useful group for SM instructions.
SIL specifiers = (pointer, length) pairs — our `const char*` + `slen`.

| SIL Macro | Operation | SM? | RT? |
|-----------|-----------|-----|-----|
| `LOCSP sp,d` | Get specifier from descriptor | — | **RT** `DESCR_TO_SP` |
| `GETSPC d,base,off` | Get specifier at offset | — | **RT** |
| `PUTSPC base,off,sp` | Store specifier | — | **RT** |
| `GETLG d,sp` | d = length of specifier | — | **RT** |
| `PUTLG sp,d` | Set length of specifier | — | **RT** |
| `GETSIZ d,base` | d = size of block | — | **RT** |
| `SETSIZ base,d` | Set size of block | — | **RT** |
| `SETLC sp,n` | Set length to constant | — | **RT** |
| `SETSP sp1,sp2` | Copy specifier | — | **RT** |
| `SHORTN sp,n` | Shorten specifier by n | — | **RT** |
| `FSHRTN sp,n` | Shorten from front by n | — | **RT** |
| `TRIMSP sp` | Trim trailing blanks | **SM** `SM_TRIM` | **RT** `TRIM_fn` |
| `REMSP sp1,sp2` | Remove specifier sp2 from sp1 | — | **RT** |
| `SUBSP sp,d,n` | Substring specifier | — | **RT** `SUBSTR_fn` |
| `APSP sp1,sp2` | Append sp2 to sp1 | — | **RT** |
| `APDSP sp1,sp2` | Append and deposit | — | **RT** |
| `LEXCMP` | Lexicographic compare | **SM** `SM_LCOMP` | **RT** `LGT_fn` etc. |
| `SPCINT d,sp,f,ok` | Parse integer from specifier | — | **RT** `SPCINT_fn` |
| `SPREAL d,sp,f,ok` | Parse real from specifier | — | **RT** `SPREAL_fn` |
| `REALST sp,d` | Format real to string | — | **RT** `REALST_fn` |
| `INTSP sp,d` | Format integer to string | — | **RT** `INTSP_fn` |
| `LVALUE` | Get l-value of specifier | — | **RT** |

---

## Group 5 — Control Flow (SM instructions)

These map 1:1 to SM_Program instructions already in SCRIP-SM.md.

| SIL Macro | Operation | SM Instruction | Status |
|-----------|-----------|----------------|--------|
| `BRANCH label` | Unconditional goto | `SM_JUMP` | DONE |
| `RCALL ret,proc,args,exits` | Call procedure | `SM_CALL` | DONE |
| `RRTURN ret,n` | Return by exit n | `SM_RETURN` | DONE |
| `BRANIC d,off` | Branch indirect via descriptor | `SM_JUMP_INDIR` | **ADD** |
| `SELBRA d,table` | Select branch via table index | `SM_SELBRA` | **ADD** |
| `PUSH d` | Push descriptor | `SM_PUSH_VAR` / value | DONE |
| `POP d` | Pop descriptor | `SM_POP` | DONE |
| `SPUSH sp` | Push specifier | — | **RT** |
| `SPOP sp` | Pop specifier | — | **RT** |
| `ISTACKPUSH` | Push interpreter state | `SM_STATE_PUSH` | **ADD** (for EXPVAL) |
| `PSTACK` | Push pattern stack | — | **RT** (bb_pool) |

**SM additions from this group:** `SM_JUMP_INDIR` (for `:(<CODE_VAR>)` GOTG),
`SM_SELBRA` (for type-dispatch in INTERP/ARITH), `SM_STATE_PUSH/POP` (for EXPVAL
save/restore of interpreter registers — this is the key RT-6 mechanism).

---

## Group 6 — Pattern Building (SM instructions — already in SCRIP-SM.md)

All `SM_PAT_*` instructions (DONE in SCRIP-SM.md design):

`SM_PAT_LIT`, `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_SPAN`, `SM_PAT_BREAK`,
`SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`, `SM_PAT_RTAB`,
`SM_PAT_ARB`, `SM_PAT_REM`, `SM_PAT_BAL`, `SM_PAT_FENCE`, `SM_PAT_ABORT`,
`SM_PAT_FAIL`, `SM_PAT_SUCCEED`, `SM_PAT_ALT`, `SM_PAT_CAT`, `SM_PAT_DEREF`,
`SM_PAT_CAPTURE`.

These map to the SIL runtime procs ANY, BREAK, BREAKX, NOTANY, SPAN, LEN,
POS, RPOS, RTAB, TAB, ARB, ARBNO, REM, BAL, FENCE.

---

## Group 7 — Byrd Box Construction (RT functions — DONE)

Already implemented as `bb_*.c` boxes. The SIL `NAM` / `DOL` / `SCAN`
procs are the SIL equivalents of our conditional/immediate assignment
and scan mechanics. SIL names → our names:

| SIL Proc | SIL Operation | Our BB box | Status |
|----------|--------------|-----------|--------|
| `NAM` | `.VAR` conditional assignment | `bb_capture.c` | ✅ |
| `DOL` | `$VAR` immediate assignment | `bb_capture.c` (immed) | ✅ |
| `SCAN` / `SJSR` / `SCNR` | Pattern scan loop | `BB-DRIVER` | ✅ |
| `ATOP` | `@` cursor assignment | `bb_capture.c` (cursor) | ✅ |
| `ANY` | ANY(S) | `bb_any.c` | ✅ |
| `BREAK` | BREAK(S) | `bb_break.c` | ✅ |
| `BREAKX` | BREAKX(S) | `bb_breakx.c` | ✅ |
| `NOTANY` | NOTANY(S) | `bb_notany.c` | ✅ |
| `SPAN` | SPAN(S) | `bb_span.c` | ✅ |
| `LEN` | LEN(N) | `bb_len.c` | ✅ |
| `POS` | POS(N) | `bb_pos.c` | ✅ |
| `RPOS` | RPOS(N) | `bb_rpos.c` | ✅ |
| `RTAB` | RTAB(N) | `bb_rtab.c` | ✅ |
| `TAB` | TAB(N) | `bb_tab.c` | ✅ |
| `ARBNO` | ARBNO(P) | `bb_arbno.c` | ✅ |

---

## Group 8 — Named Builtins (RT functions — map to INVOKE table)

These are SIL procedures that implement SNOBOL4 builtins.
All should be registered via `register_fn()` with SIL-matching names.
Status tracks whether our C implementation matches the SIL logic.

| SIL Proc | Builtin | Status | RT milestone |
|----------|---------|--------|-------------|
| `INTGER` | `INTEGER(X)` | ✅ `_INTEGER_` | — |
| `ADD/SUB/MPY/DIV/EXPOP` | arithmetic ops | ✅ `_b_add` etc. | — |
| `MNS` | unary `-X` | ✅ | — |
| `PLS` | unary `+X` (not identity!) | ⚠️ missing | RT-2 |
| `EQ/NE/GT/LT/GE/LE` | numeric predicates | ✅ | — |
| `LEQ/LNE/LGT/LLT/LGE/LLE` | string predicates | ✅ | — |
| `DIFFER` | `DIFFER(X,Y)` | ✅ | — |
| `IDENT` | `IDENT(X,Y)` | ✅ | — |
| `SIZE` | `SIZE(S)` | ✅ | — |
| `TRIM` | `TRIM(S)` | ✅ | — |
| `DUPL` | `DUPL(S,N)` | ✅ | — |
| `SUBSTR` | `SUBSTR(S,I,N)` | ✅ | — |
| `RPLACE` | `REPLACE(S1,S2,S3)` | ✅ | — |
| `REVERS` | `REVERSE(S)` | ✅ | — |
| `LPAD/RPAD` | `LPAD/RPAD(S,N,C)` | ✅ | — |
| `CHAR` | `CHAR(N)` | ✅ | — |
| `QUES` | `?(P)` interrogation | ✅ | — |
| `NEG` | `?(S)` — succeed if null | partial | RT-2 |
| `ARRAY` | `ARRAY(D,V)` | ✅ | — |
| `ASSOC/ASSOCE` | `TABLE(N,V)` | ✅ | — |
| `ITEM` | `ITEM(A,I[,J])` | ✅ | — |
| `COPY` | `COPY(X)` | ✅ | — |
| `APPLY` | `APPLY(F,A1,...,An)` | ✅ | — |
| `DEFINE` | `DEFINE(spec,entry)` | ✅ | — |
| `OPSYN` | `OPSYN(new,old,type)` | ✅ | — |
| `LABEL` | `LABEL(X)` | partial | RT-3 |
| `EVAL` | `EVAL(X)` | ⚠️ stub | **RT-8** |
| `CODER` | `CODE(S)` | ⚠️ stub | **RT-7** |
| `CNVRT` | `CONVERT(X,T)` | partial | **RT-7** |
| `ASGN` | `X = Y` (embedded assign) | partial | **RT-5** |
| `NAME` | `.X` NAME type | ⚠️ partial | **RT-3** |
| `IND` | `$X` indirect | ✅ | — |
| `KEYWRD` | `&KW` keyword access | partial | **RT-3** |
| `ARG` | `ARG(F,N)` | ✅ | — |
| `LOCAL` | `LOCAL(F,N)` | ✅ | — |
| `FIELD/FIELDS` | `FIELD(D,...)` | ✅ | — |
| `DATDEF` | `DATA(spec)` | ✅ | — |
| `FUNCTN` | `FUNCTION(X)` | ✅ | — |
| `SORT/RSORT` | `SORT(A[,I[,J]])` | ✅ | — |
| `COLECT` | `COLLECT(N)` | partial | — |
| `CLEAR` | internal | — | SKIP |
| `CMA` | internal | — | SKIP |
| `TRACE` | `TRACE(var,type,fn)` | ⬜ stub | **RT-5** |
| `STOPTR` | `STOPTR(var,type)` | ⬜ stub | **RT-5** |
| `DETACH` | `DETACH(X)` | ⬜ stub | future |
| `SET` | `SET(X,N)` file positioning | ⬜ | future |
| `LOAD/UNLOAD` | external functions | ⬜ | future |
| `DMP/DUMP` | `DUMP(N)` | ⬜ | future |
| `DATE` | `DATE()` | ✅ | — |
| `TIME` | `TIME()` | ✅ | — |
| `READ/PRINT` | I/O | ✅ | — |
| `BKSPCE/ENDFIL/REWIND` | file I/O | partial | future |
| `FREEZE/THAW` | serialization | ⬜ | future |
| `PROTO` | prototype | ⬜ | future |

---

## Group 9 — BLOCK-mode Operations (SNOBOL4B)

Lines 7160–10211 in v311.sil: AFRAME, BCOPY, BHEAD, BLAND, BLANK,
HEIGHT, WIDTH, DEPTH, BOX, BOXIN, BTAIL, CAE, BCHAR, CIR, CLASS,
COAG, COMPFR, DISTR, DUP, DUPE, FICOM, FIX, FIXINL, FORCING, INSERT,
JOIN, LOC, LRECL, LSOHN, MIDREG, MINGLE, MORE, PAR, SER, OVY, MERGE,
CCATB, PRINTB, REPL, SLAB, SUBBLOCK, REP, NODE, UDCOM, DEF, UNITS,
WARNING.

**Decision: SKIP for now.** SNOBOL4B block operations are a separate dialect.
None of our corpus tests use them. Revisit when M-BLOCKS milestone is active.

---

## Group 10 — Compiler Internals (SKIP)

These are SIL procedures used by the compiler itself, not the runtime.
We have our own lex/parse — these are irrelevant:

`AUGATL`, `CODSKP`, `DTREP`, `FINDEX`, `BLOCK` (allocator), `GENVAR`,
`GNVARI`, `GENVUP`, `CONVAR`, `GNVARS`, `GC` (garbage collector), `GCM`,
`SPLIT`, `BINOP`, `CMPILE`, `ELEMNT`, `ELEARG`, `EXPR`, `NULNOD`,
`FORWRD`, `FORRUN`, `FORBLK`, `FILCHK`, `NEWCRD`, `CTLADV`, `TREPUB`,
`UNOP`, `CDIAG`.

**Decision: SKIP.** These are the lex/parse/compile internals. We have
`sno4parse.c`. Never touch these.

---

## New SM Instructions Identified

Beyond what's already in SCRIP-SM.md, this analysis adds:

| New SM Op | Rationale |
|-----------|-----------|
| `SM_JUMP_INDIR` | `BRANIC` — indirect goto via CODE descriptor (`:<VAR>`) |
| `SM_SELBRA` | `SELBRA` — table-driven type dispatch in INTERP/ARITH |
| `SM_STATE_PUSH` | `ISTACKPUSH` — save interpreter registers for EXPVAL |
| `SM_STATE_POP` | Restore interpreter registers after EXPVAL |
| `SM_INCR` | `INCRA` — increment integer/address (common in INTERP loop) |
| `SM_DECR` | `DECRA` — decrement integer/address |
| `SM_LCOMP` | `LEXCMP` — string lexicographic compare (LGT/LLT/etc.) |
| `SM_RCOMP` | `RCOMP` — real numeric compare (replaces CALL to GT/LT/etc.) |
| `SM_TRIM` | `TRIMSP` — inline TRIM (very common in pattern matching) |
| `SM_ACOMP` | `ACOMP` — integer compare (replaces CALL to EQ/GT/LT/etc.) |
| `SM_SPCINT` | `SPCINT` — parse integer from string (inline, no CALL overhead) |
| `SM_SPREAL` | `SPREAL` — parse real from string |
| `SM_CONCAT` | `CONCAT` — concatenate (already `SM_CONCAT` in design — confirm DONE) |

These additions are **additive** — they don't change existing SM_Instr layout.
Add them as new enum values after the current set. SCRIP-SM.md update needed.

---

## New `sil_macros.h` — C Translation of Group 1 + 2

Create `src/runtime/snobol4/sil_macros.h`:

```c
/*
 * sil_macros.h — C translations of SIL macro instructions (Groups 1 & 2)
 *
 * Every macro here matches a SIL instruction exactly in semantics.
 * Used by: RT functions (scrip-interp), SM dispatch (sm_interp.c), emitters.
 *
 * Authors: Lon Jones Cherryholmes · Claude Sonnet 4.6
 * Date: 2026-04-04
 */

/* ── Type tests ── */
#define TESTF(d, T)       ((d).v == (T))
#define VEQLC(d, T)       ((d).v == (T))
#define DEQL(a, b)        ((a).v == (b).v && (a).ptr == (b).ptr)

/* ── Integer/address arithmetic ── */
#define INCRA(d, n)       ((d) += (n))
#define DECRA(d, n)       ((d) -= (n))

/* ── String/specifier coercions (call into RT) ── */
#define SPCINT_fn(d)      sil_spcint(d)     /* string → INTEGER or FAILDESCR */
#define SPREAL_fn(d)      sil_spreal(d)     /* string → REAL or FAILDESCR */
#define REALST_fn(d)      sil_realst(d)     /* REAL → STRING */
#define INTSP_fn(d)       sil_intsp(d)      /* INTEGER → STRING */

/* ── Type coerce chain (matches SIL VARVAL/INTVAL patterns) ── */
#define IS_INT(d)         ((d).v == DT_I)
#define IS_REAL(d)        ((d).v == DT_R)
#define IS_STR(d)         ((d).v == DT_S || (d).v == DT_SNUL)
#define IS_PAT(d)         ((d).v == DT_P)
#define IS_NAME(d)        ((d).v == DT_N)
#define IS_KW(d)          ((d).v == DT_K)
#define IS_EXPR(d)        ((d).v == DT_E)
#define IS_CODE(d)        ((d).v == DT_C)
```

---

## Relationship to RT Milestones

| RT Milestone | SIL Macros / Procs Used |
|-------------|------------------------|
| RT-1 INVOKE | `BRANIC`, `SELBRA`, `TESTF`, `VEQLC` |
| RT-2 VARVAL/INTVAL/PATVAL | `SPCINT`, `SPREAL`, `INTRL`, `RLINT`, `REALST`, `LOCSP`, `GETLG` |
| RT-3 NAME/KEYWORD | `VEQLC` (type K), `GETDC`, `PUTDC` (keyword slot), `NAME` proc |
| RT-4 NMD naming list | `GETLG`, `ACOMP`, `GETSPC`, `PUTDC`, `SPCINT` (for NMDIC) |
| RT-5 ASGN | `TESTF`, `VEQLC`, `PUTDC`, `LOCAPV`, `ACOMPC` (TRACE check) |
| RT-6 EXPVAL | `SM_STATE_PUSH/POP`, `PUSH`/`POP` (full state save/restore) |
| RT-7 CONVE/CODER | `SPCINT`, `SPREAL`, `LOCSP`, `GETLG` (string→EXPRESSION) |
| RT-8 EVAL | `VEQLC` (type dispatch), `SPCINT`, `SPREAL`, `CONVE`, `EXPVAL` |
| RT-9 INTERP | `SM_INCR`, `TESTF`, `BRANIC`, `SELBRA`, `SM_ACOMP/RCOMP` |

---

## Actions Required

### Immediate (this session)
1. **Update SCRIP-SM.md** — add `SM_JUMP_INDIR`, `SM_SELBRA`, `SM_STATE_PUSH/POP`,
   `SM_INCR`, `SM_DECR`, `SM_LCOMP`, `SM_RCOMP`, `SM_TRIM`, `SM_ACOMP`,
   `SM_SPCINT`, `SM_SPREAL` to the instruction table.
2. **Create `sil_macros.h`** — Groups 1 and 2 as C macros/inlines.
3. **Fix PLS** — unary `+X` is not identity (see GENERAL-SIL-HERITAGE.md).

### Per RT Milestone
- Each RT-N milestone reads the corresponding SIL proc from v311.sil,
  implements it as a C function with the SIL name, uses `sil_macros.h`.
- All new RT functions go in `src/runtime/snobol4/` with filename
  matching the SIL proc group (e.g. `argval.c`, `nmd.c`, `asgn.c`).

### Future (post RT-9)
- `TRACE` / `STOPTR` / `DETACH` (RT-5 stubs → full implementation)
- `FREEZE` / `THAW` (serialization)
- `LOAD` / `UNLOAD` (external function loading)
- SNOBOL4B block operations (Group 9) — separate milestone

---

## Summary — What's Useful vs What to Skip

| Group | Count | Decision |
|-------|-------|---------|
| Descriptor access macros | 11 | `sil_macros.h` — C inlines |
| Type test / compare | 15 | `sil_macros.h` + 4 new SM ops |
| Arithmetic | 17 | RT functions + 2 new SM ops |
| String / specifier | 21 | RT functions + 5 new SM ops |
| Control flow | 11 | SM instructions (mostly DONE) + 3 new |
| Pattern building | 21 | SM_PAT_* (DONE in SCRIP-SM.md) |
| Byrd box construction | 15 | bb_*.c (DONE) |
| Named builtins | ~50 | RT functions via INVOKE table |
| SNOBOL4B blocks | ~50 | SKIP |
| Compiler internals | ~25 | SKIP (we have sno4parse) |

**Total useful: ~120 of 211 procedures + 12 new SM instructions.**
The 12 new SM ops fill real gaps in the current SCRIP-SM.md design.

---

*MILESTONE-RT-SIL-MACROS.md — created sprint 95, 2026-04-04*
*Feeds: SCRIP-SM.md (new SM ops), MILESTONE-RT-RUNTIME.md (RT functions),*
*sil_macros.h (C macro translations), GENERAL-SIL-HERITAGE.md (name lineage).*
