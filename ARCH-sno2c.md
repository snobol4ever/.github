# ARCH-sno2c.md — sno2c Compiler Implementation

`sno2c` is TINY's implementation of the SNOBOL4 frontend targeting C.
It is NOT a language — it is the compiler that translates SNOBOL4 → C.

*Language spec → FRONTEND-SNOBOL4.md. C backend arch → BACKEND-C.md. Session state → TINY.md.*

---

## Source Layout

```
src/sno2c/
  lex.c           Hand-rolled lexer — flat sno_charclass[256]
  parse.c         Hand-rolled parser — parse_expr() + parse_pat_expr()
  emit.c          Statement emitter — DEFINE bodies, goto resolution, setjmp guards
  emit_byrd.c     Pattern emitter — Byrd box C functions (Technique 1)
  emit_cnode.c    Expression IR + pretty-printer
  emit_cnode.h    CNode type definitions
  snoc.h/sno2c.h  AST + IR node types
  main.c          Driver
src/runtime/snobol4/
  snobol4.c       Core runtime (SIL execution model)
  mock_includes.c
  snobol4_pattern.c
  mock_engine.c   Stub — beauty_full_bin links this, NOT engine.c
```

Build: `make -C src/sno2c` → produces `src/sno2c/sno2c`

---

## Hand-Rolled Parser (replaced Bison, Session 53)

Bison had 20 SR + 139 RR conflicts. Root cause: `*snoWhite` misparsed as function
call inside `FENCE(...)`. LALR(1) state merging structural — unfixable.

Key invariant: `STAR IDENT` in `parse_pat_atom()` is always `E_DEREF(E_VAR)`.
`*foo (bar)` = concat(deref(foo), grouped(bar)) — two sequential atoms, no lookahead.

Resume order when `hand-rolled-parser` sprint resumes (after M-BEAUTY-FULL):
1. `lex.c` (~200 lines) — `sno_charclass[256]` table
2. `parse.c` (~500 lines) — `parse_expr()` and `parse_pat_expr()` separate functions
3. Update Makefile — remove bison/flex
4. Smoke tests: 0/21 → 21/21

Stash `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

---

## CNode IR — emit_cnode.c (M-CNODE ✅ `ac54bd2`)

Solves: streaming printers make irrevocable formatting decisions with no lookahead.

Three phases (same as beauty.sno's pp/qq split):
- **Build:** `build_expr()` → CNode tree. No output.
- **Measure:** `cn_flat_width(n, limit)` — early exit. The "qq" lookahead.
- **Print:** `pp_cnode()` — inline if fits, multiline+indent if not.

```c
typedef enum { CN_RAW, CN_CALL, CN_SEQ } CNodeKind;
typedef struct CNode {
    CNodeKind kind;
    const char *text;
    struct CNode **args; int nargs;
    struct CNode *left, *right;
} CNode;
```
Column budget: 120 chars. Arena allocator per statement.

---

## Three-Column Generated C Format

```
Col 1  Label   chars  0..17
Col 2  Stmt    chars 18..59
Col 3  Goto    chars 60+
```
Macros: `PLG(label,goto)`, `PL(label,goto,stmt)`, `PS(goto,cond)`, `PG(goto)`.
`emit_pretty.h` shared by emit.c and emit_byrd.c.
emit_byrd.c uses 3-column ✅. emit.c still uses raw `E(...)` — fix after M-BEAUTY-FULL.

---

## Artifact Snapshot Protocol

End of every session touching sno2c, emit*.c, or runtime/:
```bash
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c
LAST=$(ls artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1)
md5sum $LAST /tmp/beauty_tramp_candidate.c
# CHANGED → cp /tmp/beauty_tramp_candidate.c artifacts/beauty_tramp_sessionN.c
# SAME    → update artifacts/README.md "no change" note only
```
README records: session N, date, md5, line count, compile status, active bug.

---

## SIL Naming (Session 84–85, canonical)

| Category | Names |
|----------|-------|
| Types | `DESCR_t`, `DTYPE_t` |
| Fields | `.v` (type), `.a` (address), `.f` (flags) |
| Values | `NULVCL`, `STRVAL()`, `INTVAL()`, `FAILDESCR`, `IS_FAIL_fn()` |
| Vars | `NV_GET_fn`, `NV_SET_fn` |
| Functions | `APLY_fn`, `DEFINE_fn`, `CONC_fn`, `FNCEX_fn`, `MAKE_TREE_fn` |
| Stack | `NPUSH_fn`, `NPOP_fn`, `NINC_fn`, `PUSH_fn`, `POP_fn`, `TOP_fn` |
| Pattern | `XCHR` (lit), `XARBN` (arbno), `XNME` (`.`), `XDNME`/`XFNME` (`$`) |
| Expr IR | `E_MPY`, `E_OR`, `E_NAM`, `E_DOL`, `E_FNC` |

Intentional lowercase (domain primitives): `eq/ne/lt/le`, `add/sub/mul`, `ident/differ`
Known bug: `ARRAY_VAL` uses `.a`, should be `.arr` — `snobol4.h:399`, dormant.
