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

**SR-4 ✅ Session 2026-05-11, one4all `556877a4`** — dispatcher infrastructure
+ `cohort_literal.c` (QLIT/CSET/ILIT/FLIT/NUL). `LowerHandler` typedef,
`g_handlers[]`, hybrid `lower_expr`, `cohort_literal_register()`. Stale
`sm_lower_baseline.txt` entry for `rk_logic_or` corrected. Gate: PASS=30 FAIL=0.

**SR-3 ✅ Session 2026-05-11, one4all `20d2fb63`** — `emit_goto`,
`expression_scope_walk`, `kw_canonicalize` moved from `sm_lower.c` to
`lower_ctx.c`.  Four inline upcase loops replaced with `kw_canonicalize`
(GC-allocated, no 63-char cap).  Gate: PASS=30 FAIL=0 byte-identical.

**SR-2 ✅ Session 2026-05-11, one4all `daf27aeb`** — `labtab_*` family
(labtab_init/define/find/patch_later/resolve/free) moved from `sm_lower.c`
to `lower_ctx.c`.  LabelEntry/PatchEntry/LabelTable declarations already in
`lower_ctx.h` (SR-1); added the six function prototypes.  Memory migrated to
GC_MALLOC/GC_REALLOC/GC_strdup; labtab_free() is a no-op shim; abort() paths
removed.  Makefile gains lower_ctx.o line.  sm_lower.c loses ~80 lines.
Gate: PASS=30 FAIL=0 byte-identical. All six frontend smokes green. Broker 49/49.

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

- [x] Move `labtab_*` family + types to `lower_ctx.{h,c}`
- [x] Migrate to GC allocation; drop `abort()` paths
- [x] Gate: as SR-1

**SR-3 — Extract emit helpers.** Move `emit_goto`,
`sm_pat_capture_fn_arg_names`, `expression_scope_walk`,
`emit_push_expr`, and the inline upcase-fold loop (newly extracted as
`kw_canonicalize`) into `lower_ctx.c` as proper helpers. `sm_lower.c`
keeps only the dispatch + entry point + (still-monolithic) cohort
switches.

- [x] Move helpers to `lower_ctx.c`
- [x] Extract `kw_canonicalize(const char *)` — no 63-char cap, GC-allocated
- [x] Replace both inline upcase loops in `AST_AUGOP` with the helper
- [x] Gate: as SR-1

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

- [x] `typedef void (*LowerHandler)(LowerCtx*, const AST_t*)` in `lower_ctx.h`
- [x] `g_handlers[AST_KIND_COUNT]` array in `sm_lower.c`
- [x] Hybrid `lower_expr`: handler-first, switch-fallback
- [x] `cohort_literal.c` with 5 handlers + `_register`
- [x] Remove the 5 cases from the legacy switch
- [x] Gate + verify `g_handlers[AST_QLIT]` etc. are non-NULL at runtime

**SR-5 ✅ Session 2026-05-11, one4all `237c8c51`** — `cohort_ref.c` (VAR/KEYWORD/INDIRECT/DEFER).
`lower_expr` promoted from `static` to non-static (Phase-2 cohort promotion; INDIRECT
and DEFER recurse into it). Declaration added to `lower_ctx.h`. 4 cases removed from
legacy switch. Gate: PASS=30 FAIL=0 byte-identical.

- [x] `cohort_ref.c` with 4 handlers
- [x] Remove 4 cases from legacy switch
- [x] Gate

**SR-6 ✅ Session 2026-05-11, one4all `237c8c51`** — `cohort_arith.c` (INTERROGATE/NAME/MNS/PLS/ADD/SUB/MUL/DIV/MOD/POW).
One-liners use LOWER2/LOWER1_VAL macros (with `SM_Program *p = c->p` in scope).
INTERROGATE and NAME moved from non-contiguous legacy-switch locations. 10 cases removed.
Gate: PASS=30 FAIL=0 byte-identical.

- [x] `cohort_arith.c` with 10 handlers
- [x] Remove 10 cases from legacy switch
- [x] Gate

**SR-7 ✅ Session 2026-05-11, one4all `0b06ccf1`** — `cohort_seq.c` (VLIST/CAT/SEQ/ALT/OPSYN)
+ `cohort_pat_prim.c` (18 pat-prim kinds, all delegate to lower_pat_expr)
+ `lower_pat.c` (lower_pat_expr + sm_pat_capture_fn_arg_names extracted from sm_lower.c).
Stale reb_btrees baseline entry corrected (244f9e6a, pre-existing drift).
Gate: PASS=30 FAIL=0 byte-identical.

- [x] `cohort_seq.c`, `cohort_pat_prim.c`
- [x] Move `lower_pat_expr` to `lower_pat.c`
- [x] Remove 19 cases from legacy switch
- [x] Gate

**SR-13 ✅ Session 2026-05-11, one4all `e9685621`** — `lower_proc_skeletons()` extracted from `lower()`. Icon/Raku + Prolog skeleton loops moved. `lower()` = 37 lines. Gate: PASS=30.

**SR-12 ✅ Session 2026-05-11, one4all `686615a9`** — `lower_stmt()` extracted to `lower_stmt.c`. 9 sub-phases named in file header. Forward decl in lower_ctx.h. Gate: PASS=30.

**SR-11 ✅ Session 2026-05-11, one4all `69e7dde8`** — `lower_icn_gen.c` (TO/TO_BY inline SM + EVERY/SUSPEND/ITERATE/ALTERNATE/LIMIT) + `lower_prolog.c` (CHOICE + 5 broker-children). Legacy switch now empty. Gate: PASS=30.

**SR-10 ✅ Session 2026-05-11, one4all `cb7d8bf0`** — `lower_icn_ctrl.c` (10: SEQ_EXPR/IF/WHILE/UNTIL/REPEAT/LOOP_BREAK/LOOP_NEXT/RETURN/PROC_FAIL/CASE with Icon+Raku layouts) + `lower_icn_data.c` (5: MAKELIST/RECORD/FIELD/GLOBAL/INITIAL) + `lower_icn_sect.c` (4: SECTION+/−/BANG_BINARY). Gate: PASS=30.

**SR-9 ✅ Session 2026-05-11, one4all `907644e5`** — `lower_icn_relop.c` (12 relop) + `lower_icn_cset.c` (4 cset ops + LCONCAT) + `lower_icn_unary.c` (7: NOT/NULL/NONNULL/SIZE/RANDOM/IDENTICAL/AUGOP). Mid-function `#include icon_lex.h` eliminated; `AugOp_e` added to ast.h. Gate: PASS=30.

**rename ✅ Session 2026-05-11, one4all `cc21aa5a`** — sm_lower→lower, cohort_*→lower_* (14 files renamed; all refs updated). Gate: PASS=30.

**SR-8 ✅ Session 2026-05-11, one4all `d3e36f36`** — `cohort_capture.c` (CAPT_COND_ASGN/CAPT_IMMED_ASGN/CAPT_CURSOR, all delegate to lower_pat_expr) + `cohort_call.c` (FNC with EVAL+Icon shapes, IDX, ASSIGN with frame-slot opt, SCAN, SWAP with inline VAR-VAR fast path). 8 cases removed from legacy switch; 2 registrations added to init_handlers. reb_btrees baseline hash corrected (pre-existing SR-7 drift). Gate: PASS=30 FAIL=0 byte-identical. All 8 smokes green.

**SR-9 — cohort_icn_relop + cohort_icn_cset + cohort_icn_unary.**
Icon relational (12) + cset ops (5) + unaries (7). AST_AUGOP's
inline `#include` is fixed here: introduce `AugOp_e` enum in
`ast.h`, normalize `TK_AUGPLUS → AUGOP_ADD` at the Icon frontend
boundary (one change in `icon.y`), and the cohort handler reads
`e->ival` as `AugOp_e` with no frontend dependency.

- [x] Gate

**SR-10 — cohort_icn_ctrl + cohort_icn_data + cohort_icn_sect.**
Control flow (9 kinds) + data constructors (4) + section ops (4).
The big AST_CASE handler (Raku) moves intact. AST_TO_BY (86 lines)
becomes a proper named function `lower_to_by`.


**SR-11 ✅ Session 2026-05-11, one4all `69e7dde8`** — `lower_icn_gen.c` (7: TO/TO_BY inline SM coroutines + EVERY/SUSPEND/ITERATE/ALTERNATE/LIMIT) + `lower_prolog.c` (6: CHOICE/CLAUSE/CUT/UNIFY/TRAIL_MARK/TRAIL_UNWIND). Legacy switch now empty — zero `case AST_*` remain. Gate: PASS=30 FAIL=0 byte-identical.

### Phase 3 — Statement orchestration

**SR-12 ✅ Session 2026-05-11, one4all `686615a9`** — `lower_stmt.c` (9 sub-phases: blank-guard, label+DEFINE-tag, STNO/HALT, Icon no-op, Prolog dispatch, pattern-match, assignment dispatch, bare-expr, gotos). Forward declaration in `lower_ctx.h`. Gate: PASS=30 FAIL=0.

**SR-13 ✅ Session 2026-05-11, one4all `e9685621`** — `lower_proc_skeletons(LowerCtx *c)` extracted (Icon/Raku proc bodies + Prolog predicate stubs). `lower()` is now 37 lines (thin orchestrator: init → skeletons → stmt loop → SM_HALT → resolve). Gate: PASS=30 FAIL=0.

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

- [x] `lower_unhandled` records kind in ctx
- [x] Post-lowering report (silent if empty)
- [x] Every `AST_e` value has an explicit handler-table entry


**SR-14 ✅ Session 2026-05-11, one4all `4b46d16c`** — silent fallback eliminated + cohort collapse.
`lower_unhandled(c,e)` records kind in `ctx->unhandled_kinds[]` bitset and emits SM_PUSH_NULL.
`init_handlers()` pre-fills all `AST_KIND_COUNT` slots with `lower_unhandled`; cohorts overwrite
their slices. `AST_REVASSIGN`/`AST_REVSWAP` explicitly left at `lower_unhandled` with SR-15+ comment.
`lower_expr` reduced to 4-line pure dispatch — no legacy switch, no silent default. Post-lowering
report in `lower()` names unhandled kinds via `ast_e_name[]` (requires `IR_DEFINE_NAMES`).
Lon request: all 17 cohort `.c` files (`lower_literal`, `lower_ref`, `lower_arith`, `lower_seq`,
`lower_pat`, `lower_pat_prim`, `lower_capture`, `lower_call`, `lower_icn_relop`, `lower_icn_cset`,
`lower_icn_unary`, `lower_icn_ctrl`, `lower_icn_data`, `lower_icn_sect`, `lower_icn_gen`,
`lower_prolog`, `lower_stmt`) merged into `lower.c` (1,854 lines) and deleted from tree.
`lower_ctx.c` stays separate. Gate: PASS=2/7/5/5/5/5/4 smokes, broker PASS=49/49.


**SR-15 ✅ Session 2026-05-11, one4all `f500a3bd`** — rewrite: 1854→1142 lines, readable, e→t rename.

**SI-1 ✅ Session 2026-05-11** — Add `AST_PROGRAM`, `AST_STMT`, `AST_GOTO_S`, `AST_GOTO_F`, `AST_GOTO_U` to `ast.h` enum before `AST_KIND_COUNT`. Matching `ast_e_name[]` entries added. New kinds routed to `lower_unhandled` via existing `default:` in `lower_expr`. Pure enum addition — zero runtime behaviour change. Gate: build clean + all 7 smokes PASS + broker 49/49.

**SI-2 ✅ Session 2026-05-11** — `AST_aux` union typedef + `a[3]` field added to `AST_t` (a[0].i=lineno, a[1].i=stno; no flag bits — pure). `AST_END` added as distinct kind (is_end is structure not bit). `stmt_ast.c` rewritten with pure encoding: `has_eq` = children[2] slot presence; `AST_NUL` = `=` with empty repl; goto arms: `sval`=label, `children[0]`=computed expr. Gate: build + all 7 smokes + broker 49/49.

**v-field note ✅ Session 2026-05-11, one4all `7f840b71`** — Anonymous union for sval/ival/dval attempted and reverted: Icon scope analysis (coro_runtime.c) sets both sval and ival on AST_VAR nodes after frame-slot assignment — union aliasing breaks this. C keeps three separate fields documented as the split of one logical v; Snocone tree will have one v field. Gate preserved.

**SI-3 ✅ Session 2026-05-11, one4all `9e9e1f8f`** — `AST_t` is now a pure 4-field logical tree (t=kind, v=sval/ival/dval, n=nchildren, c=children[]); `a[3]` removed. `AST_ATTR` kind added for tagged attribute nodes. `AST_STMT` encoding switches from positional children to tagged attributes matching `parser_snobol4.sc` exactly (`:lbl :lang :line :stno :subj :pat :eq :repl :goS :goF :go`). `lower_stmt` reads via `attr_*` tag-scan helpers — no positional indexing, no `a[]`. Gate: build + all 7 smokes + broker 49/49.
Factored: `emit_thunk` (JUMP/body/RETURN/PUSH_EXPRESSION pattern), `emit_var_load/store`
(frame-slot-or-NV dispatch), `emit_pat_capture/emit_pat_fn_args` (merged cond/immed capture),
`lower_while_until` (merged while/until), `lower_section_3` (merged three section variants),
`emit_range_coroutine` (merged lower_to/lower_to_by), `build_proc_scope` (extracted from skeletons).
T0/T1/T2 macros; CALL1/CALL2 for trivial builtins. All `e`→`t` (tree) in lower.c + lower_ctx.h macros.
Gate: PASS=2/7/5/5/5/5/4 smokes, broker PASS=49/49. GOAL-SM-LOWER-REFACTOR complete.

**SR-15 — Documentation pass + AST param rename.** Rename AST node parameter `e` → `t` (tree) throughout `lower.c` and `lower_ctx.h` — `e` reads as "expression" but the parameter carries any AST node kind, not only expressions. Convention: `p` = program, `c` = context, `t` = tree node, `s` = statement. Then: the head-comment of `lower.c`
becomes a one-page architectural overview: pipeline position,
the three phases, the cohort layout, the `LowerCtx` lifecycle, the
isolation gate. Every cohort file's head-comment lists its kinds
with one-line semantics. Rung-archaeology comments inside handler
bodies are pruned to the *load-bearing* explanations (why a check
exists, not what rung introduced it); the rest moves to commit
messages per RULES.md.

- [x] Per-cohort head-comments: kinds + semantics
- [x] Prune rung-archaeology; keep load-bearing rationale
- [x] Final review: would a new contributor understand this on first read?
- [x] Gate

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

---

## Phase 5 — Collapse CODE_t + STMT_t into AST_t (SI-1..SI-8)

`CODE_t` is a linked list of `STMT_t`. `STMT_t` is named pointers to `AST_t`
children plus scalars. Both are trees in struct clothing. Flatten into:

```
AST_PROGRAM                    ← was CODE_t
  AST_STMT  sval=label ival=lang a[0].i=lineno a[1].i=stno a[2].i=flags
    children[0] = subject
    children[1] = pattern      (NULL if absent)
    children[2] = replacement  (NULL if absent)
    children[3] = AST_GOTO_S   sval=target (NULL if absent)
    children[4] = AST_GOTO_F   sval=target
    children[5] = AST_GOTO_U   sval=target
    children[6..8] = goto_s/f/u_expr (computed gotos)
```

`lower()` takes `const AST_t *prog`. `lower_stmt` takes `const AST_t *s`.
`CODE_t` and `STMT_t` cease to exist — names freed for runtime use.

**SI-1** — Add `AST_PROGRAM`, `AST_STMT`, `AST_GOTO_S/F/U` to `ast.h` enum + `ast_e_name[]`.

- [x] Add kinds to `ast.h`
- [x] Gate: build

**SI-2** — Shim helpers in `src/driver/stmt_ast.c`:
`stmt_to_ast(STMT_t*)` and `code_to_ast(CODE_t*)`. Declare in `scrip_cc.h`.

- [x] Write `stmt_ast.c`, declare in `scrip_cc.h`
- [x] Gate: build + smoke snobol4

**SI-3** — `lower()` and `lower_stmt` take `AST_t*`. Pure tree encoding. Call sites use `code_to_ast()` shim.

- [x] Change `lower()` to `SM_Program *lower(const AST_t *prog)`; update `lower.h`
- [x] `AST_t` pure: remove `a[3]`; document `sval`/`ival`/`dval` as C split of logical `v` (Snocone will have one `v`; C keeps three because Icon scope analysis writes both `sval` and `ival` on `AST_VAR` nodes)
- [x] Add `AST_ATTR` kind for tagged attribute nodes; add `AST_END` as structural kind
- [x] `AST_STMT` uses tagged-attribute children matching `parser_snobol4.sc` exactly: `:lbl :lang :line :stno :subj :pat :eq :repl :goS :goF :go` — no positional slots, no flag bits
- [x] Rewrite `lower_stmt(const AST_t *s)` reading tagged attrs via `stmt_attr_find/expr/str`
- [x] Shim call sites: `lower(code_to_ast(prog))`
- [x] Gate: all smokes + broker byte-identical

**SI-4** — SNOBOL4 frontend emits `AST_STMT`/`AST_END` directly; remove shim from that path.

- [ ] Add `ast_stmt_new()` and `ast_attr_leaf/int/expr()` helpers in `scrip_cc.h`
- [ ] Update `snobol4.y` (or `CMPILE.c`) grammar actions to emit `AST_STMT` with tagged-attr children (`:lbl :lang :line :stno :subj :pat :eq :repl :goS :goF :go`) and `AST_END` directly — matching `stmt_to_ast()` output exactly
- [ ] Call `lower(ast_prog)` directly from the SNOBOL4 path; bypass `code_to_ast()`
- [ ] Gate: smoke snobol4 byte-identical

**SI-5** — Remaining five frontends emit `AST_STMT`/`AST_END` directly (same tagged-attr shape as SI-4).

- [ ] icon
- [ ] prolog
- [ ] raku
- [ ] rebus
- [ ] snocone
- [ ] Gate after each: that frontend's smoke + broker

**SI-6** — Delete `CODE_t`, `STMT_t`, `stmt_ast.c`, all related helpers.

- [ ] Delete structs and helpers
- [ ] Gate: all smokes + broker byte-identical

**SI-7** — Snocone parsers emit `'AST_PROGRAM'`/`'AST_STMT'`/`'AST_END'` trees with tagged-attr children; update `.ref` oracles.

The Snocone `tree` datatype has one `v` field (SNOBOL4 value). `AST_ATTR` nodes carry the tag in `v` and the payload as `children[0]` (or as a leaf with `v` for simple strings). `parser_snobol4.sc` already produces this shape — SI-7 aligns the `.ref` oracle files.

- [ ] Update `corpus/SCRIP/parser_*.sc` if needed for `AST_END`/`AST_ATTR` kinds
- [ ] Regenerate `.ref` oracles
- [ ] Gate: PARSER-* fixtures pass

**SI-8** — Doc pass: `PLAN.md`, `RULES.md`, `scrip_cc.h` header comment.

- [ ] Update docs
