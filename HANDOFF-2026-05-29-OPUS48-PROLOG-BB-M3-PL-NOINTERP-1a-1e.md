# HANDOFF 2026-05-29 — Opus 4.8 — Prolog BB — M3-PL-NOINTERP-1a..1e

**one4all commit:** `b408b086`
**Goal:** GOAL-PROLOG-BB.md — native `--run` (mode-3) Prolog program entry
**Headline:** mode-3 native crosscheck **0 → 10 PASS**, no regressions, FACT clean.

## What landed

Native (MEDIUM_BINARY/WIRED) Prolog `--run` now RUNS instead of aborting, for the
self-contained-single-predicate arithmetic/atom/write class of programs. Eight BB-template
binary-arm fixes plus the SM entry point. Every fix was a latent `movabs rax,0; call rax`
(call-to-null) or a TEXT-only arm emitting assembly-as-bytes — all invisible until mode-3
native first exercised MEDIUM_BINARY (mode-4 uses MEDIUM_TEXT, so these never ran before).

| File | Change |
|---|---|
| `SM_templates/sm_bb_switch.cpp` | SM_BB_PL_INVOKE BINARY arm: abort-stub → env-push + walk_bb_flat + γ/ω tail in raw bytes (SM_BB_INVOKE scratch-buffer recipe). Multi-predicate DEFER GUARD via g_sm_native_unsupported. |
| `BB_templates/bb_builtin.cpp` | write: call-0 → rt_pl_write_atom/var. NEW is/2 arm → rt_pl_is. NEW comparison arm (12 ops) → rt_pl_arith_cmp/rt_pl_term_cmp. |
| `BB_templates/bb_unify.cpp` | two call-0 → rt_pl_node_to_term/rt_pl_unify_terms (scalar). Compound (BB_PL_STRUCT) honest-abort-guarded. |
| `BB_templates/bb_arith.cpp` | full 7-arg rt_pl_arith port. |
| `BB_templates/bb_pl_cut.cpp` | call-0 → rt_pl_cut_set. |
| `BB_templates/bb_pl_var.cpp` | call-0 → rt_pl_var_push. |
| `BB_templates/bb_atom.cpp` | call-0 → rt_pl_atom_push; fixed rcx→rdi register bug. |

## Verified (run live, this session)

- mode-3 native crosscheck: **10 PASS / 122 FAIL** (was 0/132). Passers: hello, arith,
  rung01_hello_hello, rung04_arith_arith, rung21_char_type_space_alnum,
  rung23_arith_ext_{bitwise,max_min,power,sign,truncate}. All 3-mode agreement.
- rung04 confirmed byte-identical to mode-2 by eye (`6 / true / false`) before trusting the gate.
- GATE-3 mode-2: 104/107 (no regression).
- GATE-SWI mode-2: 57/57 (no regression).
- siblings: icon 5/5, raku 5/5, snobol4 13/13.
- FACT check 1: 0 violations. All emitted bytes inside `*_templates/`.

## Findings worth keeping

- The "is/2" and comparison builtins were TEXT-only arms that returned assembly strings with no
  medium gate — in MEDIUM_BINARY those strings were emitted AS BYTES. is/2 left vars unbound (`_`);
  comparisons always falsely succeeded (5<3 → true). Both now have explicit BINARY arms.
- rung04's `X is 2*3` does NOT route through bb_arith.cpp — it routes through bb_builtin.cpp's
  `is` arm (rt_pl_is, which binds dst_slot). bb_arith handles bare BB_ARITH nodes only.
- Discipline held: where a binary port would be more than wiring (compound unify, multi-predicate),
  I set g_sm_native_unsupported for an HONEST ABORT rather than ship silent-wrong output. The
  crosscheck only moved on tests that are genuinely correct in all three modes.

## NEXT (multi-session, value order)

The 122 remaining native FAILs need, in priority order:
1. **CALLEE-BLOCK LOOP** (highest value): port the TEXT arm's `pl_emit_callee_block_body` sweep
   into the 1a SM_BB_PL_INVOKE BINARY arm. Unblocks EVERY multi-predicate program at once
   (rung02/05/06/...). The TEXT loop is in sm_bb_switch.cpp ~lines 288-326; each non-entry user
   predicate gets a block with γ/ω/redo labels.
2. **COMPOUND-TERM BUILDER**: port `emit_build_compound_term` (bb_builtin.cpp, recursive
   rt_pl_compound_build_n) to raw bytes. Unblocks rung03 + compound unify/functor/arg/univ.
   The 1b compound-operand abort-guard in bb_unify.cpp is the placeholder to remove once done.
3. **BB_PL_CHOICE / backtracking** BINARY arms (CP-stack).
4. **DCG**.

Develop and verify against mode-2 (`--interp`) — the correctness reference — throughout.
