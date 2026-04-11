# MILESTONE-SS-COMPLETE.md — 100% SIL Translation, No Exceptions

**Goal:** Every single line of v311.sil (all 12,293 lines) has a corresponding C translation
in src/silly/. No stubs. No skipped sections. No excuses. BLOCKS included.

**Rule:** Translation cannot be blocked by runtime concerns. We write C. It either
runs correctly or it doesn't — that is a testing problem. Translation is not testing.

---

## What "100%" means

v311.sil has four categories of content:

| Category | Lines | Treatment |
|----------|-------|-----------|
| EQU constants | throughout | `#define` in types.h — ✅ done |
| DESCR data declarations (§24) | 10481–12293 | `sil_data_init()` — ✅ partially done |
| Labeled PROC blocks (non-BLOCKS) | ~5000 lines | C functions in sil_*.c — mostly done, gaps below |
| BLOCKS feature | 7035–10207 (+269 inline) | new file: sil_blocks.c — ⬜ not started |

---

## Group A — Non-BLOCKS gaps (fix first, small)

### A1. Platform stub signature mismatches (platform.c vs io.c)
io.c has the correct extern declarations (matches SIL). platform.c stubs have wrong sigs.

| XCALL | io.c expects | platform.c has | Fix |
|-------|-------------|----------------|-----|
| `XCALL_IO_OPENI` | `RESULT_t(DESCR_t, SPEC_t*, SPEC_t*, DESCR_t*)` | `void(DESCR_t, SPEC_t*)` | Fix platform.c |
| `XCALL_IO_OPENO` | `RESULT_t(DESCR_t, SPEC_t*, SPEC_t*)` | `void(DESCR_t, SPEC_t*)` | Fix platform.c |
| `XCALL_IO_SEEK` | `RESULT_t(DESCR_t, DESCR_t, DESCR_t)` | `void(DESCR_t, DESCR_t)` | Fix platform.c |

### A2. LOAD_fn (extern.c)
Written this session but does not compile — missing extern declarations:
- `extern RESULT_t STREAM_fn(SPEC_t*, SPEC_t*, DESCR_t*, int*);`
- `extern DESCR_t VARATB;`
- `extern DESCR_t LODCL;`
- Move `spec_eq_rparen` before `LOAD_fn`, remove `static`

### A3. Compiler re-entry path (func.c)
SIL lines 6492–6551. All called functions exist. No runtime blocker.

| Block | SIL lines | What it does |
|-------|-----------|-------------|
| `RECOMJ/RECOMT/RECOM1/RECOM2/RECOMF/RECOMN/RECOMZ/RECOMQ` | 6492–6531 | Shared compiler re-entry: allocate code block, call CMPILE_fn loop, append END, SPLIT |
| `CODER_fn` | 6530–6533 | `CODE(S)`: VARVAL + branch to RECOMJ |
| `CONVE_fn` | 6534–6543 | Convert to EXPRESSION: SCL=2 + branch to RECOMJ |
| `CONVEX` | 6544–6551 | Called from RECOMJ when SCL=1: EXPR + TREPUB + set E type + RECOMZ |

### A4. DEFFNC_fn (define.c)
SIL lines 4310–4470. ~80 SIL lines. INTERP_fn exists. No runtime blocker.
Full argument-binding save/restore + INTERP call.
Labels: DEFF1..DEFF20, DEFFF, DEFFC, DEFFN, DEFFNR, DEFFGO, DEFFVX, DEFFS1, DEFFS2.

---

## Group B — BLOCKS feature (new file: sil_blocks.c)

### B1. New constants (add to types.h)
```c
#define BL_TYPE  44   /* BLOCKS block diagram data type */
/* BLOCKS block-field offsets */
#define ORG_    DESCR
#define REG_    (2*DESCR)
#define TOP_    DESCR
#define FIRST_  (3*DESCR)
#define ELEMENT_ (2*DESCR)
#define NAME_   (2*DESCR)
#define ID_     DESCR
#define BL_     (2*DESCR)
#define FRAME_  (3*DESCR)
#define ARRAY_  (4*DESCR)
/* edge/node data types */
#define AEDGDT  40
#define EDGDT   41
#define TNDT    42
#define SBDT    43
/* block organization codes */
#define SER_  1
#define PAR_  2
#define OVY_  3
#define MERGE_ 4
#define IT_   5
#define REP_  6
#define NODE_ 7
#define DEF_  8
#define PHY_  9
```

### B2. New source file: sil_blocks.c
86 PROC blocks → 86 C functions, all named `BLOCKNAME_fn()`.
3,173 SIL lines → estimated ~2,000 lines of C.

Functions (in SIL order):
`ADD_NP_fn`, `AF_MERGE_fn`, `AFRAME_fn`, `B_PB_fn`,
`BMORG4_fn/BMORG5_fn/BMORG6_fn/BMORG7_fn`, `BCOPY_fn`, `BHEAD_fn`,
`BLAND_fn`, `BLANK_fn`, `HEIGHT_fn`, `WIDTH_fn`, `DEPTH_fn`,
`BLS2_fn`, `BLOCKSIZ_fn`, `BLS1_fn`, `BLOKVAL_fn`,
`FRONT_fn`, `VER_fn`, `HOR_fn`, `BOX_fn`, `BOXIN_fn`, `BTAIL_fn`,
`CAE_fn`, `BCHAR_fn`, `CIR_fn`, `CLASS_fn`, `COAG_fn`,
`COMPFR_fn`, `DISTR_fn`, `DUMP_B_fn`, `DUMP_A_fn`, `DUP_fn`, `DUPE_fn`,
`E_ATTACH_fn`, `EMB_PHY_fn`, `FICOM_fn`, `FIX_fn`, `FIXINL_fn`,
`FORCING_fn`, `F_JOIN_fn`, `HOR_REG_fn`, `VER_REG_fn`, `NORM_REG_fn`,
`GR1_fn`, `IDENT_SB_fn`, `INIT_SUB_fn`, `INSERT_fn`,
`JE_LONGI_fn`, `JE_ORTHO_fn`, `JOIN_fn`, `LOC_fn`, `LRECL_fn`, `CC_fn`,
`LSOHN_fn`, `MIDREG_fn`, `MINGLE_fn`, `MORE_fn`, `NRMZ_REG_fn`, `N_REG_fn`,
`PAR_fn`, `SER_fn`, `OVY_fn`, `MERGE_fn`, `OPS1_fn`, `CCATB_fn`,
`PAR_CONG_fn`, `PRE_SUF_fn`, `PRINTB_fn`, `NEW_PAGE_fn`,
`P_BLOCK_fn`, `NP_BLOCK_fn`, `REPL_fn`, `SLAB_fn`, `SUBBLOCK_fn`,
`STRIP_F_fn`, `T_LEAF_fn`, `IT_fn`, `REP_fn`, `NODE_fn`,
`UDCOM_fn`, `DEF_fn`, `UNITS_fn`, `WARNING_fn`

### B3. Inline BLOCKS additions to existing functions (269 lines)
Add the `.IF BLOCKS` branches into the already-translated functions:

| Function | What BLOCKS adds |
|----------|-----------------|
| `BEGIN` (main.c/interp.c) | Print BLOCKS version title |
| `BINOP_fn` | BL-enabled operator table dispatch (BINOP6/BINOP7) |
| `CMPILE_fn` | `AEQLC BLOKCL,0` jump for BLOCKS-enabled parse path |
| `CONCAT` in expr/asgn | `VEQLC XPTR,BL` and `VEQLC YPTR,BL` type checks |
| `DMPK1_fn` | String quoting path for DMPKV/DMPK2/DMPK3 |
| `KEYT_fn` / `KEYN` | String value quoting |
| Various data entries | `BLOKCL` keyword, `BL` type in type tables |

### B4. Registration
Register all 86 BLOCKS functions in `init_syntab()` alongside existing functions.
Add `BLOKCL` keyword (enables BLOCKS feature when non-zero).

---

## Order of work

### Phase 1 — Non-BLOCKS gaps (do NOW)
1. ~~**A1**~~ ✅ `67460124` — fix 3 platform stub signatures
2. **A2** — fix LOAD_fn compile errors
3. **A3** — translate RECOMJ+CODER+CONVE+CONVEX
4. **A4** — translate DEFFNC_fn

### Phase 2 — BLOCKS (LAST, after FWD & BWD passes complete)
⚠️ Do NOT start until M-SS-BLOCK-FORWARD and M-SS-BLOCK-BACKWARD both finish.
5. B1 constants, B2 sil_blocks.c, B3 inline additions, B4 registration

### OLD order (replaced):

1. **A1** — fix 3 platform stub signatures (10 min)
2. **A2** — fix LOAD_fn compile errors (15 min)
3. **A3** — translate RECOMJ+CODER+CONVE+CONVEX (~30 SIL lines → ~60 lines C)
4. **A4** — translate DEFFNC_fn (~80 SIL lines → ~150 lines C)
5. **B1** — add BLOCKS constants to types.h
6. **B2** — create sil_blocks.c, translate all 86 PROC blocks one at a time
7. **B3** — add 269 inline BLOCKS lines to existing functions
8. **B4** — register BLOCKS functions

---

## Gate

Zero stubs. Zero `return FAIL` one-liners that represent untranslated SIL.
Build clean: 0 errors, 0 warnings.
Every labeled block in v311.sil has a corresponding named C function.
Every `.IF BLOCKS` line has corresponding C code in the right place.

