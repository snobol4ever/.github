# ARCH-scrip-cc.md — scrip-cc Compiler Implementation

`scrip-cc` is TINY's implementation of the SNOBOL4 frontend targeting C.
It is NOT a language — it is the compiler that translates SNOBOL4 → C.

*Language spec → FRONTEND-SNOBOL4.md. C backend arch → BACKEND-C.md. Session state → TINY.md.*

---

## Source Layout

```
src/scrip-cc/
  lex.c           Hand-rolled lexer — flat sno_charclass[256]
  parse.c         Hand-rolled parser — parse_expr() + parse_pat_expr()
  emit.c          Statement emitter — DEFINE bodies, goto resolution, setjmp guards
  emit_byrd.c     Pattern emitter — Byrd box C functions (Technique 1)
  emit_cnode.c    Expression IR + pretty-printer
  emit_cnode.h    CNode type definitions
  snoc.h/scrip-cc.h  AST + IR node types
  main.c          Driver
src/runtime/snobol4/
  snobol4.c       Core runtime (SIL execution model)
  mock_includes.c
  snobol4_pattern.c
  mock_engine.c   Stub — beauty_full_bin links this, NOT engine.c
```

Build: `make -C src/scrip-cc` → produces `src/scrip-cc/scrip-cc`

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

End of every session touching scrip-cc, emit*.c, or runtime/:
```bash
INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno
src/scrip-cc/scrip-cc -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c
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


---

## Multi-Backend Single-IR Optimization (noted G-8, 2026-03-29)

**scrip-cc has an optimization that gcc does not have.**

In gcc, each translation unit is compiled separately — one source file, one IR,
one backend pass. There is no notion of a single IR tree being handed to multiple
backends in one invocation.

In scrip-cc, a single invocation compiling one source file can build the IR tree
**once** and then pass it to **multiple backends** in sequence. The IR tree is
constructed once by the frontend (parse → lower → IR) and then each requested
backend (`-asm`, `-jvm`, `-net`, `-c`) walks the same in-memory tree.

**Implications for the reorg:**

1. **IR tree must be read-only after construction.** Any backend that mutates
   the tree (even "harmlessly") corrupts subsequent backends in multi-backend
   mode. All backends must treat the IR as immutable once `compile_one` returns
   from the frontend.

2. **Per-backend state must be fully reset between backends.** The SIGSEGV fixed
   in G-8 (`emit_program` / `jvm_emit_stmt` accessing `children[1]` on unary
   `E_INDR`) was a multi-file bug, but multi-backend state bleed is the
   analogous risk within a single file. Each backend entry point (`asm_emit`,
   `jvm_emit`, `net_emit`, `c_emit`) must zero its own statics before running.
   This was partially addressed in G-8 (G-8 commit `6967683`); verify completeness
   in Phase 4 (M-G4-SHARED-CONC-FOLD) when backends share more emit helpers.

3. **run_emit_check.sh `--update` mode** already exploits this: a single scrip-cc
   call can regenerate `.s`, `.j`, and `.il` in one pass if wired that way.
   Worth doing explicitly to speed up baseline regeneration.

4. **Lowering passes** (e.g., `fixup_val_tree`, snocone lowering, Prolog
   lowering) run as part of frontend and produce the final IR. They must not
   be re-run per backend. Verify: each lowering pass is called exactly once,
   before the first backend entry point, inside `compile_one`.

5. **Phase 4 `ir_emit_common.c`** — shared helpers (e.g., `emit_concat_fold`)
   called from multiple backends on the same tree must not cache pointers into
   the tree across backend runs if the backends' memory arenas are recycled.

**Action item:** Add an `IR_FROZEN` debug flag (or assert) that backends set at
entry and the IR node allocator checks — any `expr_new()` call while frozen is a
bug. Lightweight: a static bool in `ir.c`. Can be `#ifdef DEBUG` if desired.
