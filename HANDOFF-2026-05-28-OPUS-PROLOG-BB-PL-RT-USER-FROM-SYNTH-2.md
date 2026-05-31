# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: PL-RT-USER-FROM-SYNTH-2 ✅

**Goal:** GOAL-PROLOG-BB.md. Closes the rung33_bridge_callN 02/04/05 failures
predicted by the prior session's PL-RT-USER-FROM-SYNTH partial 🟡 handoff.

## What landed (one commit, engine-only)

**`61187cc7` — SCRIP/main:** `PL-RT-USER-FROM-SYNTH-2: 3 type-domain bugs
fixed, rung33_bridge_callN 2/5->5/5`. Single file touched:
`src/runtime/interp/pl_runtime.c` (+24/-24 lines, all logic edits + an updated
comment block; no API surface change).

## Root cause (one paragraph)

The prior session's PL-RT-USER-FROM-SYNTH partial 🟡 (953f981d) replaced the
`[NO-AST] interp_eval stub` at `pl_runtime.c:931` with real BB-graph dispatch
via `pl_bb_lookup` + `bb_exec_once`. The handoff diagnosed the residual
"works for all-input args but fails for output-mode vars" symptom as "the
body's local-var read doesn't connect to the caller's R cell" and recommended
**Approach B** (redesign `pl_call_term_n` to bypass `pl_term_to_synth_expr`
entirely for user predicates). That diagnosis was wrong in mechanism but
right in symptom location. The actual root cause was **three latent
type-domain bugs in `pl_term_to_synth_expr` + `pl_synth_free`**, all inert
until output-mode vars and integer literals reached the synthesis path
simultaneously:

1. **`pl_term_to_synth_expr` L789:** `case TT_VAR:` (tree_e value = 5) was
   matching `t->tag == 5`, which is `TermTag::TERM_REF` (never seen after
   `term_deref`). A caller's `TERM_VAR` (=1) fell through to the switch
   default → `pl_synth_new(TT_FNC)` with `v.sval=NULL`. Downstream
   `pl_unified_term_from_expr`'s TT_FNC arm read `e->v.sval ? e->v.sval : "f"`
   → `"f"` → `term_new_atom("f")`. The body's `Z is X+Y` then
   `unify(atom_f, int_7)` → 0 → `bb_exec_once` returned DT_FAIL=99.

2. **Same function L791:** `pl_synth_new(TERM_VAR)` (TermTag=1) produced a
   tree_t with `t = 1 = TT_ILIT`. Even if bug (1) had been correct, the
   consumer wouldn't have recognised it as a var.

3. **`pl_synth_free` L770:** freed `e->v.sval` for every node
   unconditionally. With bugs (1)+(2) fixed, real `TT_VAR`/`TT_ILIT`/`TT_FLIT`
   leaves now exist with `v.ival`/`v.dval` set; the union-overlapped bits
   were being read as `char*` and `free()`d — `free(0x3)` on integer literal 3
   in `add(3, 4, R)`. Gated to only free sval for `TT_FNC`/`TT_QLIT` (the
   only kinds where `pl_term_to_synth_expr`'s `strdup` actually produces it).

**Why all three were latent under the partial fix:** the partial only worked
for all-input-mode user-pred calls (e.g. `call(greet3, hi, ho, hum)`). Those
have no `TERM_VAR` caller terms (so bug 1 was a no-op), and only `strdup`'d
atom leaves (so bug 3 freed valid pointers). The output-var case
(`call(add, 3, 4, R)`) surfaces all three at once.

## Why Approach B was not needed

Approach B's premise was that the synthesis round-trip itself was incompatible
with output-var semantics. Empirically, once the type-domain bugs are
corrected, the round-trip works fine: caller's `TERM_VAR` Term goes into
`tenv[slot]` as itself (not a copy), the synth-tree TT_VAR node has `v.ival =
slot`, the user-call branch's `pl_unified_term_from_expr` returns the **same**
caller Term, `unify(at, caller_term, &g_pl_trail)` aliases the callee's fresh
var `at` to the caller's R cell on the trail, and the body's `is/2`
unification binds through the TERM_REF chain back to the caller. Standard WAM
shared-var binding via trail aliasing — no synthesis-layer fidelity loss
once the leaves are typed correctly.

If a future session still wants to do Approach B (bypass synth for user
predicates), it would be a tidier code path but not a correctness fix.

## Diagnosis method (for next session's reference)

1. Confirmed baseline 2/5 PASS at HEAD `953f981d`.
2. Compared with `add(3,4,R)` direct call (works) vs `call(add,3,4,R)` (segfault).
3. Added `SCRIP_DEBUG_PLRT_USER`-gated stderr traces in three locations:
   the user-call branch (line 944), `BB_PL_VAR` case in `bb_exec.c`, and
   `is/2` handler. Traces showed: arg[2] reached the branch as `c_t=45` (TT_FNC,
   not TT_VAR) — first smoking gun. The synth tree was being built with
   the wrong tree_e for caller's R.
4. Counted `tree_e` enum to confirm `TT_VAR=5`, `TT_FNC=45`, `TERM_VAR=1`,
   `TT_ILIT=1` — collision pattern visible from the union-overlap
   characteristic of C-style type-tag confusion.
5. Applied fix (1)+(2). Trace then showed `bb_exec_once -> v=6 (DT_I)`
   — success — but still segfault. Implicates `pl_synth_free`. Diagnosed
   bug (3) by reading the producer's strdup sites and noting only TT_FNC /
   TT_QLIT receive an actual string.
6. Applied fix (3). 5/5 PASS.
7. Removed all debug traces, verified clean working tree (`git diff --stat
   HEAD` showed only the intended file).

## Gates at handoff (HEAD `61187cc7`, post-push)

| Gate | Count | Vs HEAD `953f981d` baseline |
|------|-------|------------------------------|
| GATE-1 Prolog smoke | 5/5 | byte-identical |
| GATE-2 3-mode crosscheck | 132/0 ORACLE_MISS=5 | byte-identical |
| GATE-3 mode-2 (`--interp`) | 104/107 | byte-identical (same 3 pre-existing FAILs) |
| GATE-SWI | 53/57 (92%) | byte-identical |
| GATE-4 mode-4 minimal | 4/4 | byte-identical |
| BB-honest | 128/0 | byte-identical |
| **rung33_bridge_callN** | **5/5** | **2/5 → 5/5** ✅ |
| rung33 mode-3 (`--run`) | 5/5 | transparent via sm_interp_run |
| FACT rule | 0 violations | preserved |
| Sibling smokes (Icon/Snocone/Raku/SNOBOL4) | all green | byte-identical |

Concurrent upstream merge: rebased onto `debb8a4e` (SBL-M3-NATIVE-4 ARBNO
tree-shape foundation, owned by SNOBOL4-BB) — no conflict, clean rebase,
post-rebase build + smoke + rung33 all re-verified green.

## NEXT recommended (Lon's pick from the goal table options)

With rung33 closed and gate baseline preserved, the highest-leverage Prolog
next steps are:

- **WAM-CP-6 LCO** — segfault-cluster fix per Sonnet 4.6's prior analysis
  (HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md). Requires
  `bb_exec_once` non-recursive refactor via explicit call-descriptor stack.
- **SWI-5 EMPTY verdict** — close the 4 remaining SWI failures (currently
  53/57 → push to 57/57 or document XFAIL).
- **PL-RT-ASSERTZ** — dynamic clause support still partial.
- **WAM-CP-13** — full mode-4 corpus is 54/107 at HEAD; this is the long-arc
  improvement track per the WAM-CP rung ladder.

GNU-Prolog comparative study is queued from the prior 58c7cab9 handoff but
non-blocking on engine work.

## Verify-before-commit ran

`bash scripts/build_scrip.sh` → green at every step. Full gate sweep
documented above. FACT-grep (`grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` and `emit_core.c`) → 0.
No SM/BB walking at mode-3/4 runtime added; no AST walking added; no Byrd
boxes added; no template byte-construction violations.

## Trust notes for the next agent

The fix is **2 logic lines and 1 logic line + a comment** in a single file.
If you're tempted to widen the scope, don't — the diff is intentionally
minimal. The three bugs were a triad: any one fixed in isolation leaves
the path broken differently. The comment block at the user-call branch
documents the full chain so the next reader doesn't have to re-derive.
