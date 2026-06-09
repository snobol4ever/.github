# HANDOFF — PL-RV-1 + PL-RV-2: first Prolog boxes onto the x86() self-encoding API

**Date:** 2026-06-02 · **Model:** Opus 4.8 · **Track:** GOAL-PROLOG-BB, x86() TEMPLATE-REVAMP (the CURRENT PRIORITY)
**Status:** COMPLETE, all gates green, landed. Two boxes converted; technique + safety method proven.

## What shipped

The first two Prolog BB templates are converted to the `x86()` self-encoding API (one return per `PLATFORM_*`,
pure `x86(mnem,…)` concat, no `bb_bin_t`, `pBB`-free end-to-end, BINARY twin deleted).

| Box | Commit | Lines | Notes |
|-----|--------|-------|-------|
| `bb_cut`   | `ed42331` (PL-RV-1) | 50 → 32 | trivial leaf: `call rt_pl_cut_set; jmp γ; def β; jmp γ`. No operands. |
| `bb_arith` | `ced1acd` (PL-RV-2) | 92 → 52 | `rt_pl_arith` 7-arg call; operand scalars promoted driver-side. |

Watermark recorded in `.github` `GOAL-PROLOG-BB.md` (`37fd94d2`).

**`b.size()` ledger (Prolog revamp debt): 57 → 55.** Both boxes eliminated from
`scripts/test_gate_no_handencoded_bytes.sh`.

## The reusable SAFETY METHOD (the main contribution beyond the two boxes)

Before discarding a box's hand-coded `MEDIUM_BINARY` twin, **prove the twin is dead** rather than assuming the
TEXT-first conversion is byte-safe: insert a `fprintf(stderr, "[FIRED]")` into each arm, rebuild
`libscrip_rt` + `scrip`, and loop the FULL rung suite per mode (`--run` and `--compile`), grepping stderr.

Results this session:
- **`bb_cut` BINARY arm: ZERO fires in mode-3** across all rungs. Prolog mode-3 routes the oracle
  (`bb_exec_once`); mode-4 uses the TEXT arm (`call rt_pl_cut_set@PLT`). The twin was dead → safe to delete.
- **`bb_arith` — the WHOLE executed box: ZERO fires in any mode** across all rungs AND direct `X is 2+3` in
  interp/run/compile. `is/2` arithmetic is emitted by `bb_builtin`'s `is` arm (PLG-9a/9h); an `IR_ARITH` node
  only ever appears as a TERM operand built by `emit_build_compound_term`, never dispatched as an executed leaf.
  The box is dead → its conversion is byte-safe against the green baseline (kept correct for any future direct
  `IR_ARITH` dispatch).

This is why the Prolog revamp can proceed without re-baselining: a converted box must only keep the LIVE path
(TEXT, for mode-4) assembler-equivalent; the BINARY twin's exact bytes don't matter when no path executes them.
The mode-4 harness (`run_prolog_via_x86_backend.sh`) compares RUNTIME OUTPUT, not `.s` text, so the cosmetic
TEXT diffs (added `[x86() self-encoding]` comment, different node-id counter, `β:`-label-on-own-line vs
same-line) are all assembler-equivalent and gate-invisible.

## The one shared-struct change (additive, sibling-safe)

`bb_arith` reads its operand neighbors (`pBB->α->t/ival`, `pBB->β->t/ival`), which the no-neighbor FACT RULE
forbids in a template. Resolved via the established Prolog driver-side promotion in `bb_prepare_pl` (the
"`emit_bb.c` flat-drive resolves it first and deposits a scalar" pattern, point 3 of the FACT RULE — same
mechanism that already deposits `bb_ls`/`bb_rs`/`bb_op_lbl`):
- `sm_emit_t` (`src/emitter/emit_globals.h`) gains **4 additive fields**: `bb_lk`, `bb_li`, `bb_rk`, `bb_ri`
  (appended → existing offsets undisturbed → Icon 12/12/12 and SNOBOL4 12/7 baselines unchanged).
- `bb_prepare_pl` (`src/emitter/emit_bb.c`) IR_ARITH arm deposits those scalars; `bb_lk = -1` reset at the top
  is the **missing-operand sentinel** the template reads (`vacuous() { return _.bb_lk < 0; }`).
- The op string comes from `_.op_sval` — a DIRECT `nd->sval` promotion already set for every node at the
  `emit_core.c` dispatch point (line 383), so no extra promotion and no `pBB->sval` read.

Both converted boxes read ONLY `_` (g_emit): labels/ports + promoted scalars + literals. No `pBB`, no `_.node`.

## Files touched

- `src/emitter/BB_templates/bb_cut.cpp` — rewritten to `x86()` (PL-RV-1).
- `src/emitter/BB_templates/bb_arith.cpp` — rewritten to `x86()` (PL-RV-2).
- `src/emitter/BB_templates/bb_templates.h` — `bb_cut`/`bb_arith` prototypes → `(void)`.
- `src/emitter/emit_core.c` — `IR_CUT`/`IR_ARITH` dispatch → `pBB`-free calls.
- `src/emitter/emit_bb.c` — `bb_prepare_pl` IR_ARITH operand-scalar promotion + `bb_lk=-1` sentinel.
- `src/emitter/emit_globals.h` — 4 additive `sm_emit_t` fields.

## Verification (all green, every commit)

- GATE-1 **5/5/5**; GATE-3 m2 **111/111**, m3 **111/111**, m4 **86 PASS / 0 FAIL / 25 EXCISED** — unchanged
  (the converted boxes are dead/twin-dead; the revamp is byte-preserving on the live path).
- FACT grep (`seg_byte(SEG_CODE`/`SL_B(` outside templates) **0**; `g_vstack` **0**;
  `test_gate_pl_no_value_stack.sh` PASS; template-purity **8 baseline** (neither converted box flagged).
- Siblings: Icon 12/12/12; SNOBOL4 12/7 (pre-existing baseline) — confirms the shared-struct edit is additive.
- `bb_cut` end-to-end via mode-4 backend (assemble→link→run) → `done`.
- Clean cross-session rebases onto three parallel Icon/pattern conversions (`bb_binop_arith`, `bb_pat_abort`,
  `bb_pat_tab`, `bb_pat_atp`).

## NEXT — `bb_unify`, but note the coupling

`bb_unify` (1 `b.size()`) is the next single-site box, BUT it is **not** a quick conversion:
1. It is **LIVE** (mode-4 `unify` smoke passes) → no dead-box shortcut; the conversion must preserve behavior
   across all its shapes: vacuous, WAM-CP-7 self-unify (`x=x`), WAM-CP-7 var-const, and the general
   operand-build path — including **compound operands**.
2. It calls `emit_build_compound_term` / `emit_build_compound_term_bin` — the **twin-walkers PL-HY-1a mandates
   deleting** (the >1000-line bulk of `bb_builtin.cpp`). So `bb_unify`'s revamp is correctly coupled to the
   walker deletion: delete both walkers in favor of ONE `rt_pl_compound_build_n`/`rt_pl_node_to_term` call,
   THEN convert the consumer to `x86()`. That is a multi-file rung deserving its own fresh context.

Remaining Prolog revamp boxes (all live and/or multi-shape/looping — each its own rung; backtracking boxes use
the landed internal-label + ζ-frame keystone at `30e8422`):
`bb_unify`(1) · `bb_catch`(1) · `bb_conj`(2) · `bb_disj`(2) · `bb_ite`(2) · `bb_choice`(6) · `bb_goal`(13) ·
`bb_builtin`(28).

## Setup note for the next session

`refs/` was dropped from the fresh-start SCRIP repo. The canonical Prolog grounding sources (gprolog + swipl)
were restored this session as symlinks under `refs/` (gitignored) from uploaded zips; re-create per RULES.md
"CONSULT CANONICAL SOURCES" when needed: `refs/gprolog` → gprolog-master, `refs/swipl` → swipl-devel-master.
