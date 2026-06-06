# HANDOFF-2026-06-06-SONNET46-ICON-BB-FULL-PASS-1.md

## Session summary

**Goal:** GOAL-ICON-FULL-PASS.md — bring all 247 non-xfail Icon tests to PASS in modes 2/3/4.
**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** `1589bd5`
**Baseline → result:** m2 143→**171** (+28) · m3 31 (unchanged) · m4 41 (unchanged)

---

## What landed

### ICN-HY-FENCE (committed `f3e7938` SCRIP / `226b5690` .github)
`scripts/test_gate_bb_one_box.sh` extended with `ICN_BOX_FILES` (32 entries) and `ICN_HELPER_FILES` (4 entries). Added to Session Setup. PASS.

### GOAL-ICON-FULL-PASS.md created (`4c799a59` .github)
32-step plan mapping every m2/m3/m4 failure to its root cause (lower unhandled, runtime mismatch, or native emitter bug). See that file for the full ladder.

### ICN-FULL-1..9 lowerer (`1589bd5` SCRIP)
Added Icon arms to `src/lower/lower.c` for the following `TT_*` kinds that previously hit `lower_unhandled` and aborted (rc=134):

| Step | Kind | Lowers to | Rungs unlocked |
|------|------|-----------|----------------|
| FULL-1 | `TT_INITIAL` | `IR_INITIAL` | 21 (partial), 25 (partial) |
| FULL-2 | `TT_LIMIT` | `IR_LIMIT` | 14 (partial — see below) |
| FULL-3 | `TT_MAKELIST`/`TT_VLIST` | `IR_CALL("MAKELIST",…)` | 22, 31, 35 |
| FULL-4 | `TT_IDX` | `IR_CALL("[]", base, idx)` | 13, 16 (partial) |
| FULL-5 | `TT_CASE` | `IR_CASE` chain | 33 (partial — see below) |
| FULL-6 | (TT_IDX table path) | same as FULL-4 | 23 (partial) |
| FULL-7 | `TT_FIELD` | `IR_FIELD_GET` | 24 (partial) |
| FULL-8 | `TT_CSET_DIFF/UNION/INTER` | `IR_CALL("--"/"++"/"**", …)` | 37 subset |
| FULL-9 | `TT_REVASSIGN`/`TT_REVSWAP` | `IR_SWAP` | 15 (partial) |

Also: `TT_SECTION`/`TT_SECTION_PLUS`/`TT_SECTION_MINUS` → `IR_SECTION` (unlocks rung 20).

**Net gain: m2 143 → 171 (+28).** All gates green (FACT 0, no-stack 0, g_vstack 0, one-box PASS, smoke icon 12/12, prolog 5/5, broker 32/35).

---

## Open bugs (next session MUST fix first)

### BUG-1: IR_LIMIT body topology wrong — `lim->α` must be the generator node, not the chain entry
**Symptom:** `every write((1|2|3|4|5) \ 2)` prints `1 1` instead of `1 2`.
**Root cause:** The lowerer sets `lim->α = bα` (entry of body literal chain: LIT_I(1)). The interp calls `IR_interp_node(lim->α)` which just evaluates the LIT_I and returns 1 each time; the IR_ALT generator node (the actual stateful generator) is never reached iteratively.
**Fix:** For IR_LIMIT, `lim->α` must point to the STATEFUL GENERATOR node itself (the IR_ALT in this case), not the entry of the chain that feeds into it. Study how `v_every` sets `ev->α = g1α` where g1α is the IR node that has state. The LIMIT interp calls `IR_interp_node(bb->α)` as a single-node call — that node must carry state itself (be a generator like IR_ALT/IR_TO). Fix the lowerer's `TT_LIMIT` arm: use `body` (the FINAL node of the body subgraph, the one with state) not `bα` (the entry). Inspect the graph with `--dump-bb` to confirm node topology after fix.
**Rungs:** 14 (5 subtests).

### BUG-2: IR_CASE segfaults (rc=139 SIGSEGV)
**Symptom:** All `rung33_case_*` tests crash.
**Root cause:** The arm-chain wiring in the `TT_CASE` lowerer arm is producing a malformed graph with a NULL pointer dereference in the interp. The `cas->α->γ` assignment and the arm-chain linking logic is incorrect — specifically the handling of `key_nd->γ = val_nd` may be clobbering a γ that was already set, creating a cycle or NULL.
**Fix:** Rewrite the `TT_CASE` arm more carefully. The IR_CASE interp (see `IR_interp.c:3610`) expects: `cas->α` = the selector expr node; `cas->α->γ` = first key node; each key_nd->γ = its val_nd; each val_nd->γ = next key_nd (or NULL for last); last pair has `val_nd->γ = NULL` (the interp uses NULL to terminate the walk). Do NOT use `lower2` for key and value nodes — use `lower_value_subgraph` into subgraphs stored in `operand_aux`, or directly build the chain with `nalloc` + manual γ wiring. Study the IR_interp.c `case IR_CASE` walk before rewriting. Use `--dump-bb` to verify graph is cycle-free.
**Rungs:** 33 (5 subtests).

### BUG-3: IR_SWAP returns wrong value — `x :=: y` result
**Symptom:** `rung15_real_swap_swap_basic` prints `1 2` instead of `2 1`. The swap happens but something about the return value or the write order is wrong.
**Root cause:** The `TT_REVASSIGN` lower chains `lower2` of lhs and rhs as `bounded` subgraphs wired to `sw`. The IR_SWAP interp reads both variables, swaps them, sets `bb->value = rv` (the original rhs value). But the test writes both x and y after the swap — so the issue may be that the VAR nodes feeding `sw->α`/`sw->β` need to be plain IR_VAR nodes (variable refs), not subgraph entries. Check with `--dump-bb`: `sw->α` and `sw->β` must be IR_VAR nodes pointing to the variable names (like the interp checks: `l_var->t != IR_VAR`). If they're not IR_VAR, the interp fails silently and returns &ω.
**Fix:** For `TT_REVASSIGN` with two `TT_VAR` children, build `sw->α = nalloc(IR_VAR)` with `sval = lhs_name` and `sw->β = nalloc(IR_VAR)` with `sval = rhs_name` directly — do not use `lower2` for the operands.
**Rungs:** 15 (2 subtests).

### BUG-4: Subscript assignment `a[i] := v` — `TT_ASSIGN` with `TT_IDX` lhs (kind=47)
**Symptom:** `rung13_table_subscript_assign` and `rung23_table_*` abort with `[lower2] UNHANDLED role=0 kind=47`.
**Root cause:** `t[key] := val` lowers as `TT_ASSIGN` where the lhs is `TT_IDX`. The current `TT_ASSIGN` arm in lower.c doesn't handle the case where lhs is `TT_IDX` for Icon. The interp has `IR_IDX_SET` for this.
**Fix:** In the `TT_ASSIGN` arm (around line 955 of lower.c), add an Icon arm: if lhs is `TT_IDX`, lower to `IR_IDX_SET { base_α, key_β, rhs_γ }`. Study `IR_IDX_SET` in IR_interp.c (line ~3410) for the expected node layout. Also check `IR_FIELD_SET` for `rec.field := val` (TT_FIELD lhs).
**Rungs:** 13 (subscript assign), 23 (table assign), 24 (field assign).

### BUG-5: `pow()` returns integer instead of real — `2^10 = 1024` not `1024.0`
**Symptom:** `rung26_pow_*` expects `1024.0` but gets `1024`.
**Root cause:** Icon's `^` operator always returns a real. The current `rt_pow` or BINOP_POW handler returns an integer when both operands are integers.
**Fix:** In `src/runtime/arithmetic.c` or wherever BINOP_POW is implemented, coerce the result to real regardless of operand types. Consult `refs/icon-master/src/runtime/oarith.r` for canonical behavior.
**Rungs:** 19, 26 (9 subtests combined).

### BUG-6: `initial` runs on every call instead of just once
**Symptom:** `rung21_global_initial_initial_once` prints `1 2 3` instead of `1`. The initial clause runs on every procedure invocation.
**Root cause:** `IR_INITIAL` uses `bb->ival` as a "done" flag (0=not run, 1=done). But the IR node is shared across calls — if the interpreter resets node state between calls (e.g., `bb->ival` gets reset), the initial runs again. OR the lowerer is not generating a proper IR_INITIAL node that persists its `ival` across calls.
**Fix:** Verify the IR_INITIAL node is in the procedure's BB graph and its `ival` persists (is not reset by the interp between calls). If the problem is node-state reset, use a `GC_malloc`'d flag variable via `NV_GET`/`NV_SET` keyed on the proc name instead of `bb->ival`.
**Rungs:** 21, 25 (partial).

---

## Next session checklist

1. Fix BUG-1 (IR_LIMIT body topology) → confirm rung14 all 5 PASS.
2. Fix BUG-2 (IR_CASE segfault) → confirm rung33 all 5 PASS.
3. Fix BUG-3 (IR_SWAP operands must be IR_VAR) → confirm rung15 PASS.
4. Fix BUG-4 (TT_ASSIGN with IDX/FIELD lhs → IR_IDX_SET/IR_FIELD_SET) → rung13, 23, 24.
5. Fix BUG-5 (pow always real) → rung19, 26.
6. Fix BUG-6 (initial once-flag persistence) → rung21, rung25.
7. Then continue GOAL-ICON-FULL-PASS.md remaining steps (FULL-10 through FULL-32).

Expected m2 after fixes: ~195–205 / 247.

---

## Watermark

**HEAD (SCRIP) = `1589bd5` — ICN-FULL-1..9 LANDED 2026-06-06. m2 171 · m3 31 · m4 41.**
**HEAD (.github) = this entry.**

Session 2026-06-06 (Sonnet 4.6, GOAL-ICON-BB → GOAL-ICON-FULL-PASS):
- ICN-HY-FENCE: gate extended, committed.
- GOAL-ICON-FULL-PASS.md: 32-step plan created, committed.
- ICN-FULL-1..9: Phase 1 lowerer arms for 9 TT_* kinds → m2 +28 (143→171). SCRIP `1589bd5`.
- 6 open bugs documented above; none committed in broken state.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
