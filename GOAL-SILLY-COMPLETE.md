# GOAL-SILLY-COMPLETE — Complete Silly SNOBOL4 (100% Translation, No Stubs)

**Repo:** one4all (`src/silly/`)
**Done when:** Every labeled block in v311.sil (all 12,293 lines) has a faithful C
translation in src/silly/. Zero stubs. Zero bare `return FAIL` one-liners representing
untranslated SIL. Build clean: 0 errors, 0 warnings. BLOCKS included.

---

## What this goal is

The forward and backward sweep goals (GOAL-SILLY-SWEEP-FORWARD/BACKWARD) verify
correctness block by block. THIS goal is orthogonal: it tracks completeness — making
sure every SIL block is actually translated (not a stub or missing). Both must finish
for Silly SNOBOL4 to be complete.

**⛔ Do NOT start Phase 2 (BLOCKS) until GOAL-SILLY-SWEEP-FORWARD and
GOAL-SILLY-SWEEP-BACKWARD are both complete.**

---

## Gap analysis methodology (2026-04-11)

Three angles were used to produce this list — each catches different classes of gap:

1. **SIL PROC labels** — every `LABEL PROC` in v311.sil lines 955–10208 (excluding §24 data)
2. **Oracle functions** — every `NAME(ret_t retval)` in snobol4.c (generated C ground truth)
3. **Code-path coverage** — each candidate checked against silly source: `_fn`, `do_NAME`,
   lowercase helper, or inline fold into an enclosing function

Items confirmed covered by fold/inline are NOT listed below even if they lack a `_fn`.
See "Confirmed NOT missing" table at bottom.

---

## Setup

See `REPO-one4all.md` Session Start. Build gate (run before every commit):

```bash
cd /home/claude/one4all
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be empty
```

Key paths:
```
/home/claude/work/snobol4-2.3.3/v311.sil      # SIL spec (12293 lines)
/home/claude/work/snobol4-2.3.3/snobol4.c     # generated C ground truth
/home/claude/one4all/src/silly/                # our translation
```

Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`

```bash
git -c user.name="LCherryholmes" -c user.email="lcherryh@yahoo.com" \
    commit -m "SILLY-COMPLETE Xn: <description>"
```

---

## Phase 1 — Non-BLOCKS gaps (10 steps)

### Group A — Compiler re-entry cluster (func.c)

SIL §19 lines 6492–6551. All called functions already exist (CMPILE_fn, SPLIT_fn,
EXPR_fn, TREPUB_fn). Previously mislabelled "M19 blocker" — that was wrong.

Three-way: v311.sil 6492–6551 · snobol4.c 8841–8955

| Step | Block(s) | SIL | oracle | What |
|------|----------|-----|--------|------|
| A1 | `RECOMP` | 6492–6494 | 8841–8847 | Sets SCL=1, falls into RECOMJ |
| A2 | `RECOMJ/RECOMT/RECOM1/RECOM2/RECOMF/RECOMN/RECOMZ/RECOMQ` | 6495–6531 | 8848–8939 | Compiler re-entry: alloc code block, run CMPILE loop, SPLIT |
| A3 | `CODER_fn` (replace stub) | 6530–6533 | 8911–8920 | VARVAL + fall into RECOMJ |
| A4 | `CONVE_fn` (replace stub) + `CONVEX` | 6534–6551 | 8921–8955 | SETAC SCL,2 + RECOMJ; EXPR+TREPUB+E-type |

- [ ] A1: Translate RECOMP
- [ ] A2: Translate RECOMJ cluster + RECOMZ (~80 lines C)
- [ ] A3: Replace CODER_fn stub
- [ ] A4: Replace CONVE_fn stub + add CONVEX

### Group B — DEFFNC_fn (define.c)

SIL §12 lines 4310–4470. ~80 SIL lines → ~150 lines C. INTERP_fn already exists.
Internal labels: DEFF1..DEFF20, DEFFF, DEFFC, DEFFN, DEFFNR, DEFFGO, DEFFVX,
DEFFS1, DEFFS2.

Three-way: v311.sil 4310–4470 · snobol4.c 5530–5665

- [ ] B1: Replace DEFFNC_fn stub — full argument-binding save/restore + INTERP call

### Group C — CONVV (func.c)

SIL §19 ~line 6675. Oracle snobol4.c ~8040–8060 (21 lines).
String-to-string conversion in CNVRT_fn — currently that path returns FAIL.

Three-way: v311.sil CONVV block · snobol4.c CONVV ~8040–8060

- [ ] C1: Translate CONVV and wire into CNVRT_fn STRING→STRING path

### Group D — Platform XCALL stubs (platform.c)

| Step | Function | What |
|------|----------|------|
| D1 | `XCALL_IO_FILE` | Attach/detach file to I/O unit by name (§15 ~5350) |
| D2 | `XCALL_XINCLD` | Open include file, push onto input stack (§15 ~5380) |
| D3 | `XCALL_GETPMPROTO` | Get prototype string for LOAD (§13 ~4490) |
| D4 | `LOAD2_fn` (replace stub) | dlopen/dlsym dynamic symbol load |

- [ ] D1: Implement XCALL_IO_FILE
- [ ] D2: Implement XCALL_XINCLD
- [ ] D3: Implement XCALL_GETPMPROTO
- [ ] D4: Replace LOAD2_fn stub — dlopen/dlsym

---

## Phase 1 — Full step checklist

- [ ] A1: RECOMP (func.c)
- [ ] A2: RECOMJ cluster + RECOMZ (func.c)
- [ ] A3: CODER_fn stub → real (func.c)
- [ ] A4: CONVE_fn stub → real + CONVEX (func.c)
- [ ] B1: DEFFNC_fn stub → full translation (define.c)
- [ ] C1: CONVV + wire into CNVRT_fn (func.c)
- [ ] D1: XCALL_IO_FILE (platform.c)
- [ ] D2: XCALL_XINCLD (platform.c)
- [ ] D3: XCALL_GETPMPROTO (platform.c)
- [ ] D4: LOAD2_fn stub → dlopen/dlsym (platform.c)

---

## Phase 2 — BLOCKS feature (new file: sil_blocks.c)

**⛔ Do NOT start until GOAL-SILLY-SWEEP-FORWARD AND GOAL-SILLY-SWEEP-BACKWARD
are both complete.**

v311.sil lines 7038–10208 (3,171 lines). Oracle snobol4.c has 133 BLOCKS functions
(starting at snobol4.c line 9685). Plus 269 lines of `.IF BLOCKS` inline additions
in existing functions.

### Phase 2 Steps

- [ ] E1: Add BLOCKS constants to types.h
- [ ] E2: Create sil_blocks.c skeleton
- [ ] E3–E135: Translate all 133 BLOCKS functions, one per commit, three-way sync
- [ ] E136: Add inline `.IF BLOCKS` branches to 7 existing functions
- [ ] E137: Register all BLOCKS functions in init_syntab(); add BLOKCL keyword

### BLOCKS constants (E1)

```c
#define BL_TYPE  44
#define ORG_     DESCR
#define REG_     (2*DESCR)
#define TOP_     DESCR
#define FIRST_   (3*DESCR)
#define ELEMENT_ (2*DESCR)
#define NAME_    (2*DESCR)
#define ID_      DESCR
#define BL_      (2*DESCR)
#define FRAME_   (3*DESCR)
#define ARRAY_   (4*DESCR)
#define AEDGDT   40
#define EDGDT    41
#define TNDT     42
#define SBDT     43
#define SER_     1
#define PAR_     2
#define OVY_     3
#define MERGE_   4
#define IT_      5
#define REP_     6
#define NODE_    7
#define DEF_     8
#define PHY_     9
```

### BLOCKS functions (E3–E135)

Use oracle snobol4.c lines 9685+ as ground truth. 133 functions in order:

```
ADD_NP   AF_MERGE  AFRAME   B_PB     BMORG4   BMORG5   BMORG6   BMORG7
BCOPY    BHEAD     BLAND    BLANK    HEIGHT   WIDTH    DEPTH    BLS2
BLOCKSIZ BLS1      BLOKVAL  FRONT    VER      HOR      BOX      BOXIN
BTAIL    CAE       BCHAR    CIR      CLASS    COAG     COMPFR   DISTR
DUMP_B   DUMP_A    DUP      DUPE     E_ATTACH EMB_PHY  FICOM    FIX
FIXINL   FORCING   F_JOIN   HOR_REG  VER_REG  NORM_REG GR1      IDENT_SB
INIT_SUB INSERT    JE_LONGI JE_ORTHO JOIN     LOC      LRECL    CC
LSOHN    MIDREG    MINGLE   MORE     NRMZ_REG N_REG    PAR      SER
OVY      MERGE     OPS1     CCATB    PAR_CONG PRE_SUF  PRINTB   NEW_PAGE
P_BLOCK  NP_BLOCK  REPL     SLAB     SUBBLOCK STRIP_F  T_LEAF   IT
REP      NODE      UDCOM    DEF      UNITS    WARNING
```

### Inline `.IF BLOCKS` additions (E136)

| Existing function | What BLOCKS adds |
|-------------------|-----------------|
| `BEGIN_fn` / `INIT_fn` (main.c) | Print BLOCKS version title |
| `BINOP_fn` (expr.c) | BL-type operator dispatch (BINOP6/BINOP7) |
| `CMPILE_fn` (cmpile.c) | `AEQLC BLOKCL,0` for BLOCKS-enabled parse path |
| `CONCAT_fn` (asgn.c) | `VEQLC XPTR,BL` and `VEQLC YPTR,BL` type checks |
| `DMPK1_fn` (func.c) | String-quoting path DMPKV/DMPK2/DMPK3 |
| `KEYT_fn` (platform.c) | String value quoting for keyword dump |
| `data_init()` (data.c) | `BLOKCL` keyword; BL type in type tables |

---

## Confirmed NOT missing (three-angle verification)

| Oracle name | Covered by | Verification |
|-------------|-----------|--------------|
| `LOCA1` | `GENVAR_fn` arena.c:141 | LOCA2/LOCA5/LOCA7 loops all present with comments |
| `KEYN` | `KEYWRD_fn` asgn.c | KNATL lookup path inline |
| `KEYC` | `KEYWRD_fn` asgn.c | INVOKE+dispatch before KEYN path |
| `RPAD0` | `rpad_common()` pred.c | 3-arg RPAD path: SCL push + full body |
| `STOPTP` | `STOPTR_fn` trace.c:139 | CALL-type lookup inline with comment |
| `TRPRT` | `VALTR_fn` trace.c | mstime+format print inline |
| `TRI2` | `VALTR_fn` trace.c | APDSP+fall path inline |
| `TRV` | `VALTR_fn` trace.c:418 | `goto vxovr` path inline |
| `VALTR1` | `VALTR_fn` trace.c | BLEQSP append path |
| `VALTR2` | `VALTR_fn` trace.c | IND path inline |
| `VALTR3` | `VALTR_fn` trace.c:375 | LOCSP XSP,XPTR path |
| `VALTR4` | `VALTR_fn` trace.c | TRACSP reset path |
| `DEFDT` | `VALTR_fn` trace.c:377 | LOCSP XSP,ZPTR branch |
| `VXOVR`/`FXOVR` | `VALTR_fn` trace.c:436 | `goto vxovr` label, prints PRTOVF |
| `FENTR3` | `FENTR_fn` trace.c | PROTSP/FILENM build path |
| `FNEXT1` | `FNEXT2_fn` trace.c | TRLVSP/LVLCL append |
| `EXPVJN` | `EXPVAL_fn` argval.c:228 | POP+fall to EXPVJ2 |
| `EXPVJ2` | `EXPVAL_fn` argval.c | Full OCBSCL/PATICL state push |
| `FORJRN` | `FORWRD_fn` forwrd.c:103 | BRTYPE=stype, return OK |
| `ELEILI` | `ELEMNT_fn` expr.c:150 | QLITYP/ELEICH dispatch |
| `ELEMN9` | `ELEMNT_fn` expr.c | STYPE switch (QLITYP/ILITYP) |
| `EXPR2` | `EXPR_fn` expr.c | BINOP dispatch on EXOPCL |
| `ENDFIL` | `ENDFL_fn` io.c:158 | Same function, SIL name vs silly name mismatch |
| `SALF`/`SALT`/`SCOK` | scan.c macros | longjmp branch targets, not callable fns |
| `SCIN1` | `do_SCIN1A` scan.c:300 | Same function, name variant |
| `SORT1` | `RSORT_fn` arrays.c | WCL=INCL initializer inline |
| `CHARZ` | scan.c | CHARCL push + ABNSND branch inline |
| `NAM5` | patval.c | Pattern-name dispatch folded in |
| `PATNOD` | patval.c | LNODSZ alloc in pat_alloc |
| `SETXIT` | `SETEXIT_fn` trace.c | Full translation (SETXIT→SETEXIT name) |
| `TRACEP` | `tracep()` trace.c | Lowercase helper, full translation |
| `FORRUN` | `forrun()` forwrd.c | Lowercase helper, full translation |
| `ARG1` | data.c | Global DESCR `ARG1CL` (data, not a proc) |

---

## Current build state

**Build:** ✅ clean (0 errors, 0 warnings) as of session start 2026-04-11
**HEAD:** one4all `43ac7934`

---

## Done when

1. Phase 1: all 10 steps ✅. Build clean.
2. Phase 2: all 137 steps (E1–E137) ✅. Build clean.
3. `grep -rn "return FAIL; /\* TODO\|return FAIL; /\* STUB" src/silly/*.c` — empty.
4. Every `NAME(ret_t retval)` in snobol4.c lines 1–9684 has implementation in src/silly/.
5. Every `NAME(ret_t retval)` in snobol4.c lines 9685+ has `_fn` in sil_blocks.c.
