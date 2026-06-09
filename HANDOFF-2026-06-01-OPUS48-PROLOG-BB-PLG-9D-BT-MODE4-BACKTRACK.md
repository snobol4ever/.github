# HANDOFF — PLG-9d-bt: Prolog mode-4 BACKTRACKING (`IR_CHOICE` multi-clause + `IR_DISJ` `;`)

**Author:** Claude Opus 4.8 · **Date:** 2026-06-01 · **SCRIP HEAD:** `3be7e6e` (rebased onto the concurrent GZ-11 SUSPEND commit `a3728c0`) · **.github HEAD:** `9f1ea5c6`
**Goal:** GOAL-PROLOG-BB.md (PLG-9 mode-4 ladder)
**Directive (Lon):** continue GOAL-PROLOG-BB — climb the mode-4 ladder; PLG-9d-bt (backtracking) follows PLG-9d (deterministic facts/calls).

## What landed

**Fail-driven backtracking — multi-clause clause enumeration (`IR_CHOICE`) and disjunction (`IR_DISJ` `;`) — now emits, assembles, links, and runs as a standalone x86 binary, driven end-to-end through the CP spine.** This is the first time the `bb_choice.cpp` / `bb_disj.cpp` / `bb_goal.cpp` CP TEXT arms have run end-to-end in the post-Ground-Zero tree (mode-3 routed these shapes through the interpreter, so they were unproven natively).

```prolog
:- initialization(main).
person(brown). person(jones). person(smith).
main :- person(X), write(X), nl, fail ; true.       % rung02 -> brown/jones/smith
```
→ `brown jones smith` in all three modes. Also 3-mode AGREE:
- **rung05** `member(X,[a,b,c]), write(X), nl, fail ; true` → `a b c` (recursion + backtrack through a list)
- **rung08** `fib(6,F)` / `factorial(3,G)` → `8` / `6` (deep recursion + multi-goal clause bodies + integer arith)

## Gates (all green, no regression)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 HARD | 5/5 HARD |
| GATE-1 smoke m3 | 5/5 | 5/5 |
| GATE-1 smoke m4 | 3 PASS / 2 EXCISED | **5 PASS / 0 EXCISED** (+`clause`, +`recursion`) |
| GATE-3 rung m2 | 111/111 | 111/111 (byte-identical) |
| GATE-3 rung m3 | 111/111 | 111/111 (byte-identical) |
| GATE-3 rung m4 | 11 PASS / 100 EXCISED | **24 PASS / 0 FAIL** / 87 EXCISED (+13) |
| FACT grep | 0 | 0 |
| Icon m2 (sibling) | 90/157/36 | byte-identical to this work; live 107/140/36 (the +17 is GZ-11, not this commit) |
| SNOBOL4 smoke | m2 7/7 HARD m3 5 m4 0 | unchanged |

Sibling neutrality was proven by **stash-and-compare**: at clean `HEAD` the Icon m2 baseline was 90/157/36 and matched exactly with my changes applied. After rebasing SCRIP onto the concurrent GZ-11 SUSPEND commit (`a3728c0`, an Icon-only change that bumped Icon corpus 90→107), the merged tree was re-built and re-gated green — Prolog m4 24/0 held, Icon m2 = 107/140/36, SNOBOL4 unchanged.

## THE EMPTY-OUTPUT BUG WAS FOUR DISTINCT DEFECTS (not one)

Flipping the gate to admit `IR_CHOICE`/`IR_DISJ` made rung02 EMIT but produce **empty output** (FAIL, strictly worse than EXCISED). Root cause was four independent defects in how a disjunctive body is selected, lowered, and walked. The mental model that unlocked it: **the mode-2 interpreter follows γ/ω edges transitively, but the mode-4 emitter (`walk_bb_flat`) emits ONE node and relies on the SEQ/ALT/CHOICE driver to re-thread the sequence — so every "where do I enter this construct" convention differs between the two.**

1. **Body-root mis-selection** (`scrip.c` `pl_rich_body_root`; `emit_bb.c` `codegen_pl_callee_block`).
   `main :- (A,B,fail ; true)` lowers to a top `IR_GCONJ` wrapping an `IR_DISJ` whose α IS its left-arm `IR_GCONJ`'s entry. So TWO GCONJs share `goals[0]==entry`, and BOTH old heuristics ("unique GCONJ" / "goals[0]==entry") mis-pick — walking only the first goal (`person/1`), dropping `write/nl/fail` and the `; true` arm.
   **FIX:** new `IR_graph_t.body_root` field (`IR.h`), set by `lower2_clause_body_entry` to the top GCONJ it builds; both selectors prefer it.

2. **`IR_GCONJ` goals[] stored element α's, not principals** (`lower.c` `wire_seq` + `lower2_clause_body_entry`).
   `flat_drive_pl_seq` walks `goals[i]` via `walk_bb_flat`. For a disjunction element, `goals[i]` was the DISJ's deep α (an `IR_GOAL`), so `walk_bb_flat` dispatched the goal, never the `IR_DISJ` — the disjunction structure was invisible.
   **FIX:** store each element's PRINCIPAL node (`apply[i]`), not its α (`entry[i]`), in the `bb_conj_state_t` goals sidecar. A no-op where α==principal (simple goals — the deterministic tier); the fix exactly where they differ (`IR_DISJ`, `IR_ITE`, nested `IR_GCONJ`). The mode-2 interpreter ignores the GCONJ goals[] sidecar, so this is additive for mode-2.

3. **`flat_drive_pl_alt` read the wrong arm source** (`emit_bb.c`).
   It read disjunction arms from `pBB->α`/`pBB->β` (a binary view) — for a Prolog `IR_DISJ` only α is set, so it saw ONE arm and silently dropped `; true`. The arms live in `operand_aux` (as the mode-2 `IR_DISJ` exec already reads via `bb_operand_aux_get`).
   **FIX:** read n-ary arm principals via `bb_operand_aux_get(g_emit_cfg, pBB, &n)`; thread each arm's success → `lbl_γ` and its failure → the next arm's `pre` label (the `bb_disj` template's `pre` does `rt_pl_trail_unwind_top` then jumps that arm's body), last arm → `lbl_ω`. This required `wire_alt` to store arm PRINCIPALS in `operand_aux` for `IR_DISJ` (it stored `entry[]`; now `apply[]`, uniform with Icon `IR_ALT`). The mode-2 `IR_DISJ` exec then **unwraps a `GCONJ` arm to its `goals[0]`** (new `bb_exec.c` `pl_disj_arm_enter`) at both `return arms[…]` sites — provably the SAME jump target as the prior `entry[]` representation (a conjunction's `goals[0]` IS that arm's deep entry), so mode-2 is byte-identical (111/111 held).

4. **`g_emit_cfg` unset on the mode-4 walk** (`scrip.c` rich arm; `emit_bb.c` `codegen_pl_callee_block`).
   `operand_aux` is keyed by (graph, node). Only the mode-3 `bb_build_flat` path set `g_emit_cfg`; the mode-4 `codegen_flat_build` / `codegen_pl_callee_block` did not, so the `operand_aux` reads in fix #3 resolved against a stale/NULL graph.
   **FIX:** set `g_emit_cfg = pl_main` around the main-body `codegen_flat_build`, and `g_emit_cfg = g` (the callee graph, save/restore) inside `codegen_pl_callee_block`.

**Plus:** `resolve_choice_bodies_em` now returns each clause's `body_root` (the body's top GCONJ), not `->entry` — so a multi-goal clause body (fib's recursive clause) emits ALL its goals via `flat_drive_pl_choice`. Byte-identical for single-element fact bodies (a `GCONJ(n=1)` walks its sole goal directly).

## TWO gate-completeness fixes (kept mode-4 at 0 FAIL — both found via the rung suite, not by luck)

(a) **`pl_rich_graph_ok` now recurses into `IR_CHOICE` clause-body sub-graphs** (`zc->bodies[]`).
A multi-clause predicate's clause bodies are SEPARATE `IR_graph_t`, not in the predicate graph's `all[]`. So a non-emittable builtin buried in a recursive clause — `rung14`'s `retract` (`retract_loop :- retract(item(_)), retract_loop`) — slipped the gate, emitted an "unknown builtin" stub, and **segfaulted (a FAIL)**. With the recursion the program now EXCISES cleanly. (`IR_DISJ` arms and `IR_ITE` branches are inline nodes already in `all[]`, so they need no special recursion.)

(b) **Admit integer-scalar arithmetic comparisons** (`>`,`<`,`>=`,`=<`,`=:=`,`=\=`) to the rich gate.
The `bb_builtin.cpp` CAT-D-9 comparison arm serializes each operand as `(kind, ival, sval)` and calls `rt_pl_arith_cmp`, which evaluates ONLY a scalar operand — an integer literal or a logic-variable slot. A float literal, a nested `IR_ARITH` expression, or an atom it cannot evaluate (→ wrong result). So admit iff BOTH operands are `pl_flat_arith_leaf_simple` (rejects float/nested-arith/atom → `rung16`/`rung29` stay EXCISED). `rung08`'s `N>1` / `N>0` proves the shape 3-mode. (NOTE: fix (a) initially over-EXCISED rung08 because its `>` lives in fib's recursive clause body — now visible to the gate — and `>` was not yet admitted; fix (b) restores it.)

## CRITICAL FINDINGS for the next engineer

- **The CP-bearing TEXT arms had never run end-to-end in this tree.** rung02/05 in mode-3 run the *interpreter* (`bb_exec_once`), because `pl_flat_body_root` returns NULL on a disjunction. So `bb_choice.cpp`/`bb_disj.cpp`/`bb_goal.cpp`'s CP protocol (resolve_cp_push/current/pop, per-clause trail unwind, the gprolog CREATE/UPDATE/DELETE_CHOICE_POINT shape) was UNPROVEN natively. PLG-9d-bt is its first end-to-end proof. The CP globals (`g_resolve_bfr`/`g_resolve_cut_barrier`/`g_resolve_cut_flag`) are zero-initialized in the fresh process, so a top-level query starts with an empty CP spine — no explicit reset needed in the standalone `main:`.
- **mode-2 vs mode-4 entry conventions are OPPOSITE for a conjunction.** mode-2 enters a conjunction at its FIRST GOAL (the GCONJ node is a success funnel; "executing" it returns `γ`). The mode-4 emitter enters at the GCONJ PRINCIPAL so `flat_drive_pl_seq` can re-thread the goals. Fixes #2/#3 reconcile these: `operand_aux`/goals[] hold principals; the mode-2 exec unwraps to the first goal at jump time.
- **The gate must recurse into `IR_CHOICE` bodies** (fix (a)) — the predicate-registry walk only checks each predicate graph's top-level `all[]`. Any future tier widening must keep this recursion, or a non-emittable node in a clause body re-opens the segfault class.

## Mechanism summary (additive, Prolog-arm-only, FACT-clean: 0 bytes outside templates)

- `src/include/IR.h` — `+IR_t *body_root;` in `IR_graph_t` (calloc-zeroed → NULL for graphs not built via `lower2_clause_body_entry`).
- `src/lower/lower.c` — `wire_seq`/`lower2_clause_body_entry` goals[] ← `apply[]`; `wire_alt` IR_DISJ `operand_aux` ← `apply[]` (+ records `body_root`). Only the `IR_GCONJ`/`IR_DISJ` arms touched; Icon `IR_CONJ`/`IR_ALT` and SNOBOL `IR_PAT_CAT`/`IR_PAT_ALT` arms untouched (the `wire_seq` change is inside `if (kind==IR_GCONJ)`; the `wire_alt` store is now unconditional `apply` — identical to what `IR_ALT`/`IR_PAT_ALT` already used).
- `src/lower/bb_exec.c` — `pl_disj_arm_enter` helper + the two `IR_DISJ` exec return sites (mode-2; byte-identical jump targets).
- `src/emitter/emit_bb.c` — `flat_drive_pl_alt` rewrite (operand_aux n-ary arms); `resolve_choice_bodies_em` → `body_root`; `codegen_pl_callee_block` sets `g_emit_cfg`; `codegen_pl_callee_block` prefers `body_root`.
- `src/driver/scrip.c` — gate admits `IR_CHOICE`/`IR_DISJ` + integer arith-comparisons; `pl_rich_graph_ok` recurses into `IR_CHOICE` bodies; `pl_rich_body_root` prefers `body_root`; rich arm sets `g_emit_cfg = pl_main`.

## NEXT — PLG-9e+

The remaining ~87 mode-4-EXCISED rungs are the mode-2-only builtin families: findall, atom/string builtins, sort/msort, format, numbervars, term comparisons (`==`/`\==`/`@<`…, via `rt_pl_term_cmp`), catch/throw (WAM-CP-13 TEXT-stub gap), float arith/constants, and runtime assert/retract/abolish (PLG-10 mutable-clause-store). Each EXCISES cleanly (0 FAIL). A purist tidy still pending: the callee γ/ω epilogue is literal `emit_text_n` in `emit_bb.c` (matches the existing `scrip.c` `main:` `printf` idiom) — a future `xa_pl_callee_epilogue` XA template would route it through the template path.

## Files

`src/include/IR.h`, `src/lower/lower.c`, `src/lower/bb_exec.c`, `src/emitter/emit_bb.c`, `src/driver/scrip.c` (SCRIP `3be7e6e`); `GOAL-PROLOG-BB.md` watermark (.github `9f1ea5c6`).
