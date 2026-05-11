# GOAL-SM-LOWER-REFACTOR — `sm_lower.c` → Pristine Multi-Frontend Lowering

**Repo:** one4all (primary) + .github (this file)
**Prerequisite for:** GOAL-SNOCONE-SM-LOWER (M2 path) — we will not
translate `sm_lower.c` to Snocone until this refactor lands. A
faithful Snocone port of the current `sm_lower.c` would reproduce
all of its accumulated debt in a less-mature language.

---

## Why

`sm_lower.c` is the **single most important file** in SCRIP. It is
the canonical pipeline waist: six frontends (SNOBOL4, Snocone, Icon,
Rebus, Prolog, Raku) feed one AST, and this one file translates that
AST into the SM instruction stream that drives all four execution
modes (IR-interp, SM-interp, JIT-exec, native-emit). Every
downstream component depends on its output. Every frontend depends
on its uniformity.

Today the file works — it self-hosts `beauty.sno` byte-identical to
SPITBOL, and the Mode-3 emitter (ME-11) just landed against it. But
it has accumulated the marks of every rung that touched it:

| Symptom | Evidence |
|---|---|
| One 1,218-line `lower_expr` switch | lines 597–1812 |
| 102 case branches, sizes 1 to 86 lines, no language cohorts | survey |
| Globals threading state into the switch | `g_expression_body_lowering`, `g_expression_scope` |
| Inline `#include` mid-function | line 1199 (`icon_lex.h` inside `AST_AUGOP`) |
| Duplicated inline upcase loop, capped at 63 chars | lines 1192–1195, 1213–1216 |
| `default:` falls through to `emit_push_expr` (silent IR-walk escape) | line 1812 |
| Comments are rung sediment, not architecture | many block comments |

The file is **C+/B−** today. The goal of this rung is to make it
**A**: a piece of work that a compiler-textbook author could open
to and point to and say *this is how you write an AST-to-bytecode
lowering pass for a multi-frontend system.*

---

## Done when

1. `lower_expr` is ≤ 80 lines: a pure dispatcher over a kind→handler
   table. No case bodies inline.
2. Every kind handler lives in a cohort file matching the `ast.h`
   section headers. One handler per kind, named `lower_<kind>` with
   a uniform signature.
3. Cross-cutting state is a `LowerCtx` struct passed explicitly. No
   file-scope globals carrying lowering-time information.
4. No `#include` appears anywhere except the top of a file. Frontend
   token kinds (`TK_AUGPLUS` etc.) are normalized at the frontend
   boundary; `sm_lower` sees only `AST_e` values.
5. Every kind has an explicit handler. No silent `default:` fallback
   to `emit_push_expr`. Kinds-not-yet-handled are listed by name in
   one place with the rung that closes each.
6. Every public symbol (the emit-family helpers, the cohort handler
   list, the `LowerCtx` lifecycle) is documented at its declaration.
   The head-comment of `sm_lower.c` is a one-page architectural
   overview suitable for a new contributor's first read.
7. **All gates byte-identical** to baseline at every rung-close.
   Beauty self-host, Icon honest 152/238, Prolog smoke, Raku 147,
   Mode-3 ME-11 fires unchanged.
8. The result is what we translate to Snocone in SL-1.

---

## Design — the destination

```
src/runtime/x86/
  sm_lower.h          // public API: sm_lower(prog) → SM_Program*
  sm_lower.c          // dispatcher + sm_lower() entry; ~200 lines
  lower_ctx.h         // LowerCtx struct + label-table + helpers
  lower_ctx.c         // ctx lifecycle, label-table impl, emit helpers
  lower_stmt.c        // lower_stmt() — statement-level orchestration
  lower_pat.c         // pattern-context lowering (SNOBOL4)
  cohort_literal.c    // QLIT, ILIT, FLIT, CSET, NUL              (5)
  cohort_ref.c        // VAR, KEYWORD, INDIRECT, DEFER            (4)
  cohort_arith.c      // INTERROGATE, NAME, MNS, PLS, ADD..POW    (10)
  cohort_seq.c        // SEQ, CAT, ALT, VLIST, OPSYN              (5)
  cohort_pat_prim.c   // 14 pattern primitives                    (14)
  cohort_capture.c    // 3 captures                               (3)
  cohort_call.c       // FNC, IDX, ASSIGN, SCAN, SWAP             (5)
  cohort_icn_gen.c    // SUSPEND, TO, TO_BY, LIMIT, ALTERNATE,
                      // ITERATE, MAKELIST, EVERY                 (8)
  cohort_icn_relop.c  // LT/LE/GT/GE/EQ/NE + L-variants           (12)
  cohort_icn_cset.c   // 4 cset ops + LCONCAT                     (5)
  cohort_icn_unary.c  // NONNULL, NULL, NOT, SIZE, RANDOM,
                      // IDENTICAL, AUGOP                         (7)
  cohort_icn_ctrl.c   // SEQ_EXPR, WHILE, UNTIL, REPEAT, IF,
                      // CASE, RETURN, PROC_FAIL, LOOP_*          (9)
  cohort_icn_data.c   // MAKELIST (companion), RECORD, FIELD,
                      // GLOBAL, INITIAL                          (4)
  cohort_icn_sect.c   // SECTION, SECTION_PLUS, SECTION_MINUS,
                      // BANG_BINARY                              (4)
  cohort_prolog.c     // UNIFY, CLAUSE, CHOICE, CUT,
                      // TRAIL_MARK, TRAIL_UNWIND                 (6)
  cohort_raku.c       // (none distinct today; CASE handled in ctrl)
```

**16 cohort files at ≤ 300 lines each.** The boundaries follow
`ast.h`'s own section headers — they are not invented, they
formalize what is already documented.

**Each cohort file has the same shape:**

```c
/*
 * cohort_arith.c — Arithmetic operators
 *
 * AST kinds handled:
 *   AST_INTERROGATE  ?X  — null-on-success
 *   AST_NAME         .X  — name reference
 *   AST_MNS          -X  — unary minus
 *   ...
 *
 * Cross-cutting: none.  All handlers are pure functions of (ctx, e).
 */

#include "lower_ctx.h"

void lower_interrogate(LowerCtx *c, const AST_t *e) { ... }
void lower_name       (LowerCtx *c, const AST_t *e) { ... }
void lower_mns        (LowerCtx *c, const AST_t *e) { ... }
...

/* Registration: called by sm_lower.c at startup */
void cohort_arith_register(LowerHandler tbl[AST_KIND_COUNT]) {
    tbl[AST_INTERROGATE] = lower_interrogate;
    tbl[AST_NAME]        = lower_name;
    tbl[AST_MNS]         = lower_mns;
    ...
}
```

**`sm_lower.c` becomes:**

```c
static LowerHandler g_handlers[AST_KIND_COUNT];
static int g_handlers_initialized = 0;

static void register_all_cohorts(void) {
    cohort_literal_register   (g_handlers);
    cohort_ref_register       (g_handlers);
    cohort_arith_register     (g_handlers);
    cohort_seq_register       (g_handlers);
    cohort_pat_prim_register  (g_handlers);
    cohort_capture_register   (g_handlers);
    cohort_call_register      (g_handlers);
    cohort_icn_gen_register   (g_handlers);
    cohort_icn_relop_register (g_handlers);
    cohort_icn_cset_register  (g_handlers);
    cohort_icn_unary_register (g_handlers);
    cohort_icn_ctrl_register  (g_handlers);
    cohort_icn_data_register  (g_handlers);
    cohort_icn_sect_register  (g_handlers);
    cohort_prolog_register    (g_handlers);
    g_handlers_initialized = 1;
}

void lower_expr(LowerCtx *c, const AST_t *e) {
    if (!e) { sm_emit(c->p, SM_PUSH_NULL); return; }
    LowerHandler h = g_handlers[e->kind];
    if (!h) { lower_unhandled(c, e); return; }
    h(c, e);
}

SM_Program *sm_lower(const CODE_t *prog) {
    if (!g_handlers_initialized) register_all_cohorts();
    LowerCtx ctx; lower_ctx_init(&ctx, prog);
    lower_proc_skeletons(&ctx);
    lower_stmt_list      (&ctx, prog);
    lower_finalize       (&ctx);  // SM_HALT + label resolve
    SM_Program *p = ctx.p;
    lower_ctx_destroy(&ctx);
    return p;
}
```

**That is the destination.** Every rung below is a step toward it,
each independently committable, each preserving the gate.

---

## Architecture reminders

- **AST kinds are cohorted in `ast.h` already.** This refactor
  doesn't invent organization — it surfaces what's already there.
- **`LowerCtx` replaces three pieces of state** that today are
  passed (or smuggled) separately: `SM_Program *p`, `LabelTable *lt`,
  and the two globals `g_expression_body_lowering` +
  `g_expression_scope`. Threading the ctx makes the dataflow visible
  at every call site.
- **The `LOWER2` / `LOWER1_VAL` / `LOWER1_PAT` macros stay** — they
  are good. They move from being CPP macros to being `static inline`
  helpers in `lower_ctx.h`, gaining type-checking.
- **No behaviour changes during the refactor.** Every rung is a
  pure structural move. Gates byte-identical at every step.
- **The Snocone port is the consumer.** This refactor's success is
  measured by whether SL-1 onwards becomes a transcription exercise
  rather than a port-with-cleanup.

---

## Closed rungs (pointer trail)

**SR-1 ✅ Session 2026-05-11, one4all `f209b8d3` (initial `456dc7a6` +
rename followup `f209b8d3`)** — LowerCtx carved out into
`src/runtime/x86/lower_ctx.h`. Signatures of `lower_expr`,
`lower_pat_expr`, `lower_stmt`, `emit_goto`, `emit_push_expr` now
take `LowerCtx *c`. Two file-scope globals
(`g_expression_body_lowering`, `g_expression_scope`) removed; their
state moved to ctx fields. `CH0/CH1/LOWER*` macros and inline
`emit_push_expr` relocated to the header so cohort files (SR-4+)
can use them. Followup commit `f209b8d3` renamed `lt` → `labtab` and
`lt_*` → `labtab_*` (Lon: 'lt' reads as less-than to a SNOBOL4
brain — jarring). Verification harness
`scripts/test_sm_lower_byte_identical.sh` baked at 30 programs ×
6 frontends; PASS=30 FAIL=0 byte-identical. Full smoke gate green.

---

## Rung sequence

The plan is **15 rungs in 4 phases**. Each rung is independently
committable. The gate is byte-identical output across all six
frontends at every rung.

### Phase 1 — Foundations (no behaviour change, structural prep)

**SR-1 — Carve out `LowerCtx`.** Define `LowerCtx` in
`lower_ctx.h`: `{SM_Program *p; LabelTable lt; int
expression_body_lowering; IcnScope *expression_scope; const CODE_t
*prog; int has_icn;}`. Refactor `lower_expr`, `lower_stmt`, and
`lower_pat_expr` to take `LowerCtx *c` instead of `(SM_Program *p,
LabelTable *lt)`. The two globals `g_expression_body_lowering` and
`g_expression_scope` become ctx fields, set/cleared at the same
call sites as today. File is still monolithic; only the parameter
shape changes.

- [x] Define `LowerCtx` in new `lower_ctx.h`
- [x] Refactor signatures: `lower_expr(LowerCtx*, const AST_t*)` etc.
- [x] Move globals to ctx fields; remove file-scope state
- [x] Inline `emit_push_expr`, `LOWER*` macros, `CH0/CH1` move to header
- [x] Gate: scrip_all_modes + smoke ×6 + isolation byte-identical

**SR-2 — Extract `LabelTable` to its own translation unit.**
`labtab_init` / `labtab_define` / `labtab_find` / `labtab_patch_later`
/ `labtab_resolve` / `labtab_free` move to `lower_ctx.c`. `LabelEntry`
/ `PatchEntry` /
`LabelTable` typedefs move to `lower_ctx.h`. The file knows nothing
of `SM_Program` internals — it's a name-to-int registry with a
patch list. Replace `malloc/realloc/strdup/free` with `GC_MALLOC` /
`GC_strdup` for memory-discipline consistency with the rest of the
runtime.

- [ ] Move `labtab_*` family + types to `lower_ctx.{h,c}`
- [ ] Migrate to GC allocation; drop `abort()` paths
- [ ] Gate: as SR-1

**SR-3 — Extract emit helpers.** Move `emit_goto`,
`sm_pat_capture_fn_arg_names`, `expression_scope_walk`,
`emit_push_expr`, and the inline upcase-fold loop (newly extracted as
`kw_canonicalize`) into `lower_ctx.c` as proper helpers. `sm_lower.c`
keeps only the dispatch + entry point + (still-monolithic) cohort
switches.

- [ ] Move helpers to `lower_ctx.c`
- [ ] Extract `kw_canonicalize(const char *)` — no 63-char cap, GC-allocated
- [ ] Replace both inline upcase loops in `AST_AUGOP` with the helper
- [ ] Gate: as SR-1

### Phase 2 — Cohort carve-out (the bulk of the work)

Each rung moves one cohort out of the monolithic `lower_expr` switch
into its own cohort file. The cohort file gets a `_register(tbl)`
function. Cases that used to be in `lower_expr` are deleted; the
dispatch hits the handler table instead.

The dispatcher infrastructure goes in **before** the first cohort
move: `lower_expr` becomes hybrid — first consult `g_handlers[e->kind]`;
if NULL, fall through to the legacy switch. This lets us move
cohorts incrementally. Each rung shrinks the legacy switch by one
section.

**SR-4 — Dispatcher infrastructure + first cohort (literals).**
Introduce `LowerHandler` typedef, `g_handlers[]` table, hybrid
dispatcher, and registration mechanism. Migrate **cohort_literal**
(QLIT, ILIT, FLIT, CSET, NUL) — the simplest 5 cases — to validate
the pattern. Legacy switch loses these cases.

- [ ] `typedef void (*LowerHandler)(LowerCtx*, const AST_t*)` in `lower_ctx.h`
- [ ] `g_handlers[AST_KIND_COUNT]` array in `sm_lower.c`
- [ ] Hybrid `lower_expr`: handler-first, switch-fallback
- [ ] `cohort_literal.c` with 5 handlers + `_register`
- [ ] Remove the 5 cases from the legacy switch
- [ ] Gate + verify `g_handlers[AST_QLIT]` etc. are non-NULL at runtime

**SR-5 — cohort_ref.** VAR, KEYWORD, INDIRECT, DEFER. The
expression-scope-aware AST_VAR logic (frame slot vs NV) moves with
it; it consults `ctx->expression_scope` cleanly now that there's no
file-scope global.

- [ ] `cohort_ref.c` with 4 handlers
- [ ] Remove 4 cases from legacy switch
- [ ] Gate

**SR-6 — cohort_arith.** INTERROGATE, NAME, MNS, PLS, ADD, SUB, MUL,
DIV, MOD, POW. The `LOWER2` / `LOWER1_VAL` helpers do real work
here — most cases collapse to one-liners.

- [ ] `cohort_arith.c` with 10 handlers
- [ ] Remove 10 cases from legacy switch
- [ ] Gate

**SR-7 — cohort_seq + cohort_pat_prim.** Sequence/alternation (5)
plus the 14 pattern primitives. These are SNOBOL4-heavy and exercise
the `lower_pat_expr` adapter — the pattern adapter stays a single
file (`lower_pat.c`) but the *value-context* arms of these kinds
move into cohorts.

- [ ] `cohort_seq.c`, `cohort_pat_prim.c`
- [ ] Move `lower_pat_expr` to `lower_pat.c`
- [ ] Remove 19 cases from legacy switch
- [ ] Gate

**SR-8 — cohort_capture + cohort_call.** Captures (3) + FNC, IDX,
ASSIGN, SCAN, SWAP (5). AST_FNC includes the EVAL(*expr) special
case (CHUNKS-step02) and the Icon-style call shape (CH-17c) — both
move intact.

- [ ] `cohort_capture.c`, `cohort_call.c`
- [ ] Remove 8 cases from legacy switch
- [ ] Gate

**SR-9 — cohort_icn_relop + cohort_icn_cset + cohort_icn_unary.**
Icon relational (12) + cset ops (5) + unaries (7). AST_AUGOP's
inline `#include` is fixed here: introduce `AugOp_e` enum in
`ast.h`, normalize `TK_AUGPLUS → AUGOP_ADD` at the Icon frontend
boundary (one change in `icon.y`), and the cohort handler reads
`e->ival` as `AugOp_e` with no frontend dependency.

- [ ] New `AugOp_e` enum in `ast.h`
- [ ] Icon frontend writes `AugOp_e` values into `AST_AUGOP.ival`
- [ ] `cohort_icn_relop.c`, `cohort_icn_cset.c`, `cohort_icn_unary.c`
- [ ] Remove 24 cases from legacy switch
- [ ] Gate

**SR-10 — cohort_icn_ctrl + cohort_icn_data + cohort_icn_sect.**
Control flow (9 kinds) + data constructors (4) + section ops (4).
The big AST_CASE handler (Raku) moves intact. AST_TO_BY (86 lines)
becomes a proper named function `lower_to_by`.

- [ ] `cohort_icn_ctrl.c`, `cohort_icn_data.c`, `cohort_icn_sect.c`
- [ ] Remove 17 cases from legacy switch
- [ ] Gate

**SR-11 — cohort_icn_gen + cohort_prolog.** Icon generators (8:
SUSPEND, TO, TO_BY (already moved to ctrl?), LIMIT, ALTERNATE,
ITERATE, MAKELIST, EVERY) and Prolog (6: UNIFY, CLAUSE, CHOICE, CUT,
TRAIL_MARK, TRAIL_UNWIND). These are the "thin lowering" path —
each handler typically emits one `SM_BB_PUMP_*` opcode.

- [ ] Resolve cohort placement of TO/TO_BY/EVERY (gen vs ctrl)
- [ ] `cohort_icn_gen.c`, `cohort_prolog.c`
- [ ] Remove remaining cases from legacy switch
- [ ] **Legacy switch now empty.** Delete the `switch (e->kind)`
  wrapper from `lower_expr`.
- [ ] Gate

### Phase 3 — Statement orchestration

**SR-12 — Extract `lower_stmt` to `lower_stmt.c`.** The 250-line
`lower_stmt` function moves to its own translation unit. Sub-phases
(blank-line, label, STNO, subject, pattern, replacement, gotos)
become named static helpers (`lower_stmt_label`, `lower_stmt_subject`,
etc.). `lower_stmt` itself becomes a thin orchestrator ≤ 30 lines.

- [ ] `lower_stmt.c` with sub-phase helpers
- [ ] `lower_stmt` ≤ 30 lines
- [ ] Gate

**SR-13 — Extract proc-skeleton emission.** The proc-table /
pl_pred-table skeleton loops at the top of `sm_lower()` move to
`lower_proc_skeletons(LowerCtx *c)`. The Icon main() synthesis
moves to `lower_icon_main_pump(LowerCtx *c)`. `sm_lower()` becomes
the entry point listed in the design above — ≤ 30 lines.

- [ ] `lower_proc_skeletons` (Icon + Raku + Prolog)
- [ ] `lower_icon_main_pump`
- [ ] `sm_lower()` ≤ 30 lines, matches design block
- [ ] Gate

### Phase 4 — Polish

**SR-14 — Replace silent fallback.** The `default: emit_push_expr(p,e); return;`
in `lower_expr` becomes `lower_unhandled(c, e)` — a function that
emits SM_PUSH_EXPR *and* records the kind in a debug log
`ctx->unhandled_kinds[]`. After `sm_lower()` completes, if any
unhandled kinds were encountered, `sm_lower.c` emits a one-line
report listing them with rung references. No silent escape.

The handler-table now contains an entry for every `AST_e`. Kinds
not yet handled point to `lower_unhandled` explicitly, not by
omission. Adding a new kind to `ast.h` forces a registration choice
— either map to `lower_unhandled` (with a rung pointer) or write a
handler.

- [ ] `lower_unhandled` records kind in ctx
- [ ] Post-lowering report (silent if empty)
- [ ] Every `AST_e` value has an explicit handler-table entry
- [ ] Gate

**SR-15 — Documentation pass.** The head-comment of `sm_lower.c`
becomes a one-page architectural overview: pipeline position,
the three phases, the cohort layout, the `LowerCtx` lifecycle, the
isolation gate. Every cohort file's head-comment lists its kinds
with one-line semantics. Rung-archaeology comments inside handler
bodies are pruned to the *load-bearing* explanations (why a check
exists, not what rung introduced it); the rest moves to commit
messages per RULES.md.

- [ ] `sm_lower.c` head-comment: ≤ 80 lines, architectural
- [ ] Per-cohort head-comments: kinds + semantics
- [ ] Prune rung-archaeology; keep load-bearing rationale
- [ ] Final review: would a new contributor understand this on first read?
- [ ] Gate

---

## Gate (same for every rung)

```bash
cd /home/claude/one4all
bash scripts/test_smoke_scrip_all_modes.sh             # must PASS=2
bash scripts/test_smoke_snobol4.sh                     # must PASS unchanged
bash scripts/test_smoke_icon.sh                        # must PASS unchanged
bash scripts/test_smoke_prolog.sh                      # must PASS unchanged
bash scripts/test_smoke_raku.sh                        # must PASS unchanged
bash scripts/test_smoke_snocone.sh                     # must PASS unchanged
bash scripts/test_smoke_rebus.sh                       # must PASS unchanged
bash scripts/test_smoke_unified_broker.sh              # must PASS=49 FAIL=0
bash scripts/test_isolation_ir_sm.sh                   # must PASS
bash scripts/test_smoke_jit_emit_x64.sh                # ME-3 mode-3 must stay green
```

Any rung that perturbs any of these is rolled back before commit.
**Byte-identical output is the standard, not "no semantic
regression."** The whole point is that this is a structural refactor
— the bytecode emitted should not change one byte.

---

## Verification harness

To make byte-identical verification cheap, write a tiny harness at
**SR-1 first thing**:

```bash
# scripts/test_sm_lower_byte_identical.sh
# Compiles a corpus of small programs in all six frontends,
# captures sm_lower's output via --sm-dump, hashes each.
# At baseline (pre-SR-1) records the hashes.
# Every subsequent run compares against baseline; any drift = FAIL.
```

This is the gate that catches mistakes the smoke tests miss. ~50
programs × md5 = 50 lines of expected output. A single byte diff is
a hard FAIL.

- [x] Write the harness as part of SR-1 setup (before any structural change)
- [x] Bake baseline hashes
- [x] Run before/after every rung

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Hybrid dispatcher (handler+switch) is itself buggy | SR-4 migrates one trivial cohort; if hashes drift, isolated failure |
| Cohort placement disagreements (TO in gen or ctrl?) | Resolve at each rung; `ast.h` cohort headers are the tiebreaker |
| `AugOp_e` migration in SR-9 touches the Icon frontend | Confined change; icon.y already maps tokens — one extra mapping table |
| Globals removed in SR-1 break a path that smuggles them through `_usercall_hook` | SR-1 runs the full isolation gate; any reach-around shows up |
| Refactor takes more sessions than budgeted | Each rung is independent; partial completion is partial value |

---

## What this earns

A `sm_lower.c` that — at the end of SR-15 — looks like a piece of
work somebody **wanted** to write, not a piece of work that grew.
The Snocone port (SL-1+) becomes a transcription exercise: each
cohort file translates directly to a cohort `.sc` file, each
handler to a Snocone function, the dispatcher to a Snocone TABLE
lookup. The structural decisions were made here, in a mature
language with a mature gate, before being expressed in a
less-mature one.

The single piece that six languages depend on becomes the single
piece a new contributor reads first.
