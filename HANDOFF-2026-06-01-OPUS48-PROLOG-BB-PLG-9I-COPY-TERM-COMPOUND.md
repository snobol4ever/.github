# HANDOFF — PLG-9i: mode-4 native `copy_term/2` for a compound arg0

**Date:** 2026-06-01 · **Model:** Opus 4.8 · **Track:** GOAL-PROLOG-BB, mode-4 ladder
**Status:** COMPLETE, all gates green, landed. (Same session as PLG-9h.)

## What shipped

`copy_term/2` now emits natively in mode-4 for a **compound** first argument.

**GATE-3 rung suite m4: 80 → 81 PASS** (0 FAIL, 31 → 30 EXCISED). Closed **rung26**
(`rung26_copy_concat_copy_term`): `copy_term(f(X,X), f(A,B))` then `A == B` → `same`, and
`copy_term(hello, C)` → `hello`. Byte-exact in all three modes.

## Root cause — a closure the PLG-9g handoff mis-filed as substrate

`copy_term` had two emit paths: a **scalar** arm (`rt_pl_copy_term`, CAT-D-5, with a TEXT arm) and a
**compound** arm (PLR-K-15, `rt_pl_copy_term_terms`, which preserves intra-term var-sharing) — but the
compound arm was **MEDIUM_BINARY only, with no `@PLT` TEXT twin**. The standalone `.s` can't use a BINARY arm
(in-process patch idiom), and the scalar TEXT arm degenerates a compound arg0 (`rt_pl_node_to_term` flattens
an `IR_STRUCT`, losing var-sharing → `copy_term(f(X,X),f(A,B))` gave `A\==B`). So the rich gate EXCISED
copy_term entirely. PLG-9g-rest listed this as "copy_term var-identity" needing substrate — but it is the
exact same **"BINARY-arm-needs-an-`@PLT`-TEXT-twin"** shape as writeq/write_canonical/atomic_list_concat
(PLG-9g) and float `is/2` (PLG-9h). No substrate required.

## The two changes (Prolog-arm-only, FACT-clean)

1. **`src/emitter/BB_templates/bb_builtin.cpp`** — a MEDIUM_TEXT twin of PLR-K-15, placed before the scalar
   CAT-D-5 arm, firing for `copy_term` with `IR_STRUCT`/`IR_ARITH` arg0. Builds arg0 (and, if compound, arg1)
   via `emit_build_compound_term` (the TEXT post-order walker), then:
   - both compound → hold arg0 in `[rsp+0]` across arg1's build, `rt_pl_copy_term_terms(t0,t1)`@PLT;
   - scalar arg1 → `rt_pl_copy_term_term(t0, k1,i1,s1)`@PLT.
   `sub rsp,16` = the slot + 16B alignment across the builder/helper calls. `test eax → je ω / jmp γ; β→ω`.

2. **`src/driver/scrip.c`** — `pl_rich_node_emittable` admits `copy_term/2` (γ-chain pair). Updated the stale
   "var-identity gap" comments.

## Why var-sharing is preserved for free

The TEXT builder's `IR_LOGICVAR` case calls `rt_pl_node_to_term(IR_LOGICVAR, slot, …)` (rt.c:1158), which —
when the env slot is empty — creates a fresh var Term **and writes it back to `g_resolve_env[slot]`**. So the
second occurrence of the same slot (the second `X` in `f(X,X)`) rereads the **same** Term. This is identical
to the BINARY builder's behavior, so `bb_copy_term` (which the helper calls) sees the shared structure and
clones it sharing-correctly. No new identity machinery needed.

## Verification (all green)

- GATE-1 smoke **5/5/5**; GATE-3 m2 **111/111**, m3 **111/111**, m4 **81 PASS / 0 FAIL / 30 EXCISED**.
- FACT grep 0; `g_vstack` 0; no-value-stack gate PASS; template-purity 7 baseline (`bb_builtin.cpp` unflagged).
- Siblings: Icon 12/12/12; SNOBOL4 12 PASS / 7 FAIL (this change is two Prolog-arm-only edits).
- Robustness: `copy_term(f(a,b),X)` (scalar-var arg1 → the `rt_pl_copy_term_term` branch); nested shared-var
  `copy_term(g(X,h(X,Y)),Z)` → `shared`. Both m2==m4.

## Remaining 30 EXCISED — now genuinely all substrate

findall ×5, retract/retractall ×5, abolish ×5, numbervars ×5, aggregate ×4, catch/throw ×5, dcg_generate ×1.
With float `is/2` (PLG-9h) and copy_term (PLG-9i) closed, **every remaining EXCISED family needs a real
runtime substrate** — there is no "missing TEXT twin" closure left. The two buckets:

- **WAM-CP-13** — dynamic-DB mode-4 emit. Unblocks retract/retractall/abolish/assertz = 15 rungs. Note the
  rung14/15 tests don't merely assert/abolish — they **call and enumerate** the dynamically-asserted predicate
  (`fact(_)`, `bird(X)…fail`), so this needs dynamic-predicate call + backtracking (CP) in the standalone `.s`,
  not just a deterministic helper. Confirmed by reading the rung programs this session.
- **PLG-10** — findall/aggregate goal-subgraph closure + the catch/throw exception barrier.

Both are multi-session substrates warranting a fresh design pass against the gprolog/swipl sources before any
emit code. This session deliberately stops here with a clean tree rather than half-start one.
