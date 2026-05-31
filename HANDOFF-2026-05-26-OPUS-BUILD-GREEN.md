# HANDOFF — 2026-05-26 — Opus Session (build RED→GREEN)

**Goal:** GOAL-ICON-BB, Phase H (Attribute Grammar) — continue from `97b92f26` emergency handoff.
**SCRIP HEAD at start:** `97b92f26` (build RED) — working tree now dirty (uncommitted, see below).
**Build:** ✅ GREEN — `scrip` compiles AND links (8.8 MB binary).
**Gates:** smoke_icon 3/5 ⛔ · broker(smoke) 15 ⛔ · rungs --interp 118/113/35 ⛔ (baseline 153).

⚠ **NOT COMMITTED.** Per RULES "no broken commits," gates are not green so nothing was committed.
Next session decides: emergency-commit the build-restoration, or land Phase H bb_exec fixes first.

---

## What this session did — restored the build from fully RED

The prior handoff (`97b92f26`) claimed "build RED at emit_sm.c only." **That was inaccurate.**
The build actually died much earlier, in `sm_jit_interp.c`, which had been broken since `7b087f0f`
(FREE-2 WIP, "BROKEN do not run"). Its errors were *masked* because bb_exec.c's ~272 errors
halted the build first; the `97b92f26` bb_exec.c fix uncovered the older rubble.

### Files changed (8, all uncommitted)
```
src/processor/sm_jit_interp.c                  | 38 +   (build + link blocker)
src/emitter/emit_sm.c                          | 86 +   (Prolog serializer + flat-pattern builder)
src/emitter/emit_bb.c                          | 44 +   (flat-pattern walker)
src/emitter/XA_templates/xa_pl_builder.cpp     | 20 +   (multi-body BB_CHOICE)
src/emitter/XA_templates/xa_pl_sub_builder.cpp |  6 +   (body-idx labels)
src/emitter/emit_globals.h                     |  3 +   (xa_pl_sub_body_idx field)
src/include/BB.h                               | 17 +   (bb_pat_kids_state_t aux + accessors)
src/tools/emit_per_kind_audit.c                | 24 +   (synthetic nodes → ports/aux)
```

### 1. `sm_jit_interp.c` — Mode-3 JIT, fully fixed (0 errors)
- Dropped `#include "../runtime/rt/rt.h"` (it redeclared ~50 local `static rt_*` non-static →
  collision). Only `rt_set_last_ok` was actually needed → replaced with `extern` fwd-decl.
- Added the **missing** `#define CUR_INS (&g_jit_prog->instrs[STATE->pc - 1])` (consistent with
  `h_unimpl`'s `STATE->pc-1`). It was used at 30+ sites but never defined.
- Moved `STATE`/`PUSH`/`POP` macros above their first use (were at line 310, used from 186).
- Forward-declared `jit_pump_print` and the entire **second-group** `rt_*` family (rt_add..
  rt_pat_*, defined below `sl_emit_one` but called from it).
- Moved `pl_runtime.h` include to the top block (pulls `Term`, `g_pl_env`, `pl_bb_once_proc_by_name`).
- `SM_instr_t` (undefined) → `SM_t` at the SB-LINEAR `sl_emit_one`.
- **Link fix:** `rt_exec_stmt` called undefined `bb_exec_pat_fn(...)` → corrected to
  `exec_stmt_blob(sn,&subj_d,pat_fn,repl,has_repl)` (the real, defined symbol; rt.c uses it the same way).

### 2. `emit_sm.c` Prolog Mode-4 serializer — the documented task, DONE
Old model: each clause body carried by a `BB_SUCCEED` node with `opaque` → its sub-graph (1 each).
New model: ONE `BB_CHOICE` node holds ALL bodies in `bb_pl_choice_state_t.bodies[]`.
- Added helpers `pl_node_choice_nbodies(nd)` and `pl_node_choice_body(nd,b)` (next to existing
  `pl_node_kids`/`pl_node_ival2`/`pl_node_choice_body0`).
- `node_is_sub[i]` repurposed: now the **count** of clause bodies (0 if none).
- Reshaped the `XA_PL_SUB_BUILDER` loop: outer over nodes, inner `for b in 0..nbodies-1`
  serializing `pl_node_choice_body(nd,b)`; sets new `g_emit.xa_pl_sub_body_idx`.
- `pl_pre_intern_pred_names` + main-loop kid/ival2 reads → helpers (no more c[]/n/ival2/opaque).
- New `g_emit.xa_pl_sub_body_idx` field; labels now `.Lpl_subbuilder_<pred>_<node>_<body>` and
  `.Lpl_sub_kids_<pred>_<node>_<body>_<i>` in `xa_pl_sub_builder.cpp`.
- `xa_pl_builder.cpp`: builds node first, then loops `node_is_sub[i]` times calling each
  sub-builder + `rt_pl_b_set_opaque(i, ...)` (which APPENDS to bodies[] per rt.c:355).
- ⚠ NOT runtime-verified: `--interp` on multi-clause needs `;/2` directive lowering ([NO-AST]),
  and `--compile -o` arg parsing failed in my quick test (`cannot open '-o'`). Verify Mode-4
  multi-clause emission with a proper invocation next session.

### 3. Flat-pattern child storage — SCOPE CORRECTION (coupled pair)
The handoff treated emit_sm.c and "emit_bb.c(20)" as separate, but the SNOBOL4 invariant-pattern
blob path is a COUPLED pair: builder `emit_walk_phase2`/`pat_set_children` (emit_sm.c) +
consumer `walk_bb_flat`/`flat_drive_cat|alt|fence`/`pre_build_children` (emit_bb.c), both on c[]/n.
This is SEPARATE from lower_pat_dcg.c's continuation-threaded DCG pattern model.
- New GC aux `bb_pat_kids_state_t { BB_t **kids; int nkids; }` in BB.h (option-b, ptr in `counter`),
  with `static inline bb_pat_nkids(nd)` / `bb_pat_kid(nd,i)` accessors.
- `pat_set_children` → stashes aux in counter. `lower_flat_invariant` + all emit_bb.c CAT/ALT/
  FENCE/ARBNO/pre_build walkers → `bb_pat_nkids`/`bb_pat_kid`.
- `pat_node_intarg` reverse flag: `nd->n = reverse` → `nd->sval = reverse?"r":NULL` (matches
  lower_pat_dcg.c; the `n` flag was DEAD anyway — bb_pat_pos.cpp reads `ival`, never `n`).
- `emit_per_kind_audit.c`: synthetic nodes rewired — pattern kinds use 3 static `bb_pat_kids_state_t`
  (kids1/2/3), non-pattern kinds (ASSIGN/FIELD/SECTION/BINOP/UNOP/CALL/PL_CALL) use α/β/γ;
  `BB_PL_CALL` `ival2`→`ival` (standardized arity field).

---

## ⛔ REMAINING WORK — genuine Phase H, in bb_exec.c (NOT touched this session)

The smoke/rung failures are pre-existing bugs from the `97b92f26` interp-path migration, in
**`bb_exec.c` Icon control flow** — exactly the Phase H gaps the goal file flags. My changes are
isolated to JIT/Prolog/pattern paths and did not touch them. Confirmed reproducers:

1. **BB_IF runs BOTH branches.** `if x>5 then write("big") else write("small")` →
   prints `big\nsmall\n`. Per goal-file Phase H note: "BB_IF: cond→α/then→β/else→γ; ⚠ else-on-γ
   collides with γ-as-success-continuation — works only for leaf/last IF, full fix needs H-1
   inherited-γ/ω threading." THIS is the H-1 work: thread inherited γ/ω down so else-branch isn't
   reached on success.
2. **`every write(1 to 3)` SEGFAULTS.** Generator-`every` over a TO_BY generator. Likely the
   BB_TO/BB_EVERY port wiring (α/β operand re-read) crashing under the executor. Check bb_exec.c
   BB_EVERY + BB_TO interaction.

After those two: re-run smoke (target 5/5), broker (≥17), rungs (≥153, recovers ≥169 at G-4).

---

## Verify-my-work checklist for next session
- [ ] `bash scripts/build_scrip.sh` → should still say "OK scrip built" (build is green).
- [ ] Multi-clause Prolog Mode-4: pick a corpus .pl with a 3-clause predicate, `--compile` it
      properly (check CLI: `--compile FILE` output path convention — `-o` flag may not be supported),
      confirm the emitted asm has `.Lpl_subbuilder_<p>_<n>_0/_1/_2` labels and runs.
- [ ] `grep -rnE '(nd|pBB|snd|gen|seq)->(c\[|n\b)' src/emitter/emit_sm.c src/emitter/emit_bb.c
      src/tools/emit_per_kind_audit.c` → should be empty (cfg->n / graph->n on BB_graph_t are legit).
- [ ] Then fix bb_exec.c BB_IF (H-1) + every/TO segfault → gates → COMMIT.

## Watermark
```
SCRIP: 97b92f26 + uncommitted (8 files, +157/-81) — BUILD GREEN, gates RED
.github: this file
GOAL: GOAL-ICON-BB Phase H
NEXT: bb_exec.c BB_IF inherited-γ/ω threading (H-1) + every+TO_BY segfault; then gates; then commit.
      Build is restored — the blocker is now genuine executor semantics, not compile rubble.
```
