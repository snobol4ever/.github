# GOAL-OPTIMIZER.md — The OPTIMIZATION stage: the mutable wall between LOWER and EMITTER

Session origin: Lon directive 2026-07-18 — "Fully implement OPTIMIZATION stage" (branch-to-branch, value-copy
propagation, pattern constant folding, general constant folding, peephole), grounded in Proebsting §5: naive
four-port template expansion "suffers from generating many simple copies and many branches to branches";
copy-prop + branch chaining collapse Figure 1's chunk soup into Figure 2's tight loops. All passes live in
`src/optimizer/`, run inside `optimizer_run()` (ON by default; `SCRIP_OPT=0` emergency escape only), and are
LANGUAGE-BLIND — dispatch on IR kind only, per the no-identity-past-dispatch FACT RULE. Optimize→slot-assign
order is load-bearing and verified at both call sites (`lower_snobol4.c:1983`, `bb_pat_build.cpp:79`): nodes
folded away never receive ZLS slots.

## ⭐ LIVE CURSOR → OPT-CMP: CMP_TEST literal fold (first unlanded rung)
Fold `IR_CMP_TEST` when both operands (looking through IR_COERCE_* wrappers of literals) are compile-time
decidable. BLOCKER TO RESOLVE FIRST: succeed-path writes the node's slot := null string — DT_SNUL vs DT_S ""
representational split must be proven observably identical (IDENT/DIFFER/datatype probes vs oracle) before an
IR_LIT_STRING("") rewrite is legal, or a dedicated null-writing rewrite target must be found. Always-fail arm
is easier: rewrite to IR_GOTO with γ := old ω (fail path never reads the slot).

## LANDED (SCRIP 175793d9, artifacts corpus a00a347d + 8cd39d26, SCRIP 48fc4960)
- **OPT-CF const_fold** — `IR_BINOP{ADD,SUB,MUL,DIV,MOD}` over literal INT/REAL/STRING folded by calling
  `rt_num_arith` itself at compile time: runtime semantics mirrored BY CONSTRUCTION (the fold IS the runtime
  computing it); FAILDESCR (div/mod-zero) never folds, preserving statement-failure behavior; CONCAT str×str
  exact-bytes. In-place rewrite to IR_LIT_* preserves all γ/ω wiring. POW excluded: `rt_ipow_descr` may reach
  error sinks — a compile-time fold must never abort compilation of code that only fails (or never runs) at
  runtime. This exclusion principle governs every future fold rung.
- **OPT-DP dead_pure** — operand-unreferenced literal producers → `IR_SUCCEED` passthrough; pre-existing
  `bc_run` splices them (branch-to-branch elimination doing double duty as dead-code sweep).
- **OPT-CP copy_prop** — operand-web retargeting through proven-identity forwarders: IR_COERCE_STRING over
  LIT_STRING; IR_COERCE_INTEGER over LIT_INTEGER honoring the packed negative-errcode guard (`ival>>16`).
  Conforming forwarders neutered to IR_SUCCEED — statically proven unable to fault. Op-filter is one line to
  extend when new identity-forwarder kinds appear.
- ⛔ **OPT-PF pat_fold — RETIRED 2026-09-11 (hq_P, row `pat-fold-dead-pass`); DELETED FROM THE TREE, NOT
  LANDED.** It landed here and was killed by SEQ-ERAD: `b88b6e2e0` ("IR_MATCH_SEQUENCE deleted from
  enum+dispatch") removed the ONLY node kind `pf_run` folded over and emptied the body to
  `int pf_run(IR_graph_t * g) { (void)g; return 0; }` in the SAME commit, leaving four static helpers dead.
  ⛔ **Re-implementation was not available**: `IR_MATCH_SEQUENCE` has ZERO occurrences tree-wide, so there is
  nothing to fold — the pass had no subject, not a missing body. Measured before deleting: `SCRIP_OPT_STATS`
  printed `pat=0` on every graph of every witness (pattern_test, beauty included), and the emitted `.s` is
  BYTE-IDENTICAL across four pattern-heavy witnesses with the pass and its call site removed.
  ⭐ **The adjacent-literal-merge OPPORTUNITY is real and survives its implementation** — if it is ever wanted
  again it must be re-cut against whatever represents pattern sequences today, as a NEW rung with its own
  measurement, never by restoring this file.
- **Driver** — ≤8-round fixpoint cf→cp→dp with `bc_run` every round (bc floor preserved);
  `SCRIP_OPT_STATS` prints `fold= copy= dead= branch_chain= dead_goto=`. ⛔ The `pf` stage and the `pat=`
  field were removed with OPT-PF on 2026-09-11; nothing parsed `pat=` (one occurrence tree-wide, its own
  `fprintf`), so no instrument was keyed on it.
- **arith_fold.c stays parked out of the build** — references GZ#5-amputated opcodes (IR_ARITH/IR_ATOM/
  IR_LOGICVAR); its const-eval library becomes relevant only if those shapes are ever re-seated.

Gates at landing (exact watermark): smokes 7/7×2 · crosscheck m3 305/2 · m4 304/2/1 · DIVERGE=1
(1017_arg_local) · bench 15/16 (eval_dynamic CRASH pre-existing — times out under SCRIP_OPT=0 too; optimizer
measured net −6% wall on 50k-EVAL variant) · icon 4/0 HARD · prolog 150/0/13. Feature .s artifacts net
−1526 asm lines.

## PARKED LADDER (in rough leverage order after OPT-CMP)
- OPT-CAT-INT: CONCAT int×str fold via runtime's own int→string (`%lld` per rt_num_arith CUNION arm) —
  requires proving format identity against the runtime's actual conversion sink first.
- OPT-CSET: fold CUNION/CDIFF/CINTER of literals by calling `cset_canonical(cset_union(...))` at compile time
  into IR_LIT_CHARSET; then admit IR_LIT_CHARSET to dead_pure once its emit is proven registration-free.
- ⛔ OPT-SEQ1 — **MOOTED BY THE SAME ERADICATION, flagged 2026-09-11 by hq_P; not cured, just named.** It
  reads "collapse sequence-of-one (post-merge N==1) to the bare element … past the driver box", and both the
  driver box (`IR_MATCH_SEQUENCE`) and the "post-merge" state it consumes (OPT-PF) are gone. A seat taking
  this rung as written would go looking for a node that does not exist. It stays on the ladder only as a
  RESTATEMENT TASK: re-express it against today's sequence representation, or retire it.
- OPT-FZ-RESEAT: FZ-3/FZ-4/FZ-5a invariant-subpattern freezing (IR_REF_INVARIANT sealed blobs) lives only in
  `lower_snobol4.gz5-parked-41b53078.c`; template `bb_ref_invariant.cpp` still exists. Re-seat into live
  lower per the GOAL-IR-IMMUTABLE-EMIT SN4-PAT ladder — the single biggest pattern-fold prize.
- OPT-ALT: MATCH_ALTERNATE-level folds (duplicate-alternative elision; literal-prefix factoring) — needs the
  ALTERNATE backtrack-tree contract read first.

## METHOD NOTES (bind on every future rung here)
Fold-by-calling-the-runtime is the house move: never re-implement semantics, invoke the linked rt sink on
literal DESCRs and translate the result DESCR back to a literal node (skip on FAILDESCR; exclude any sink
that can abort). Every structural surgery on driver boxes must first locate ALL cached geometry (`ival`
counts, doubled-operand conventions) — the emit contract comment at `emit.cpp:1117` is the reference. Gates
are the full five-language battery above, never SNOBOL4 alone: the stage is shared.
