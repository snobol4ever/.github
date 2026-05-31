# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: SWI-2d call/1 mode-2 fallback

**Repos:** SCRIP `d805b0fe` · corpus (untouched) · .github (this commit)

Continuation of SWI-2c. The prior handoff identified a blocker:
`call(true)` returns failure under `--interp`, masking the just-fixed
plunit test-fold. This session closes that blocker — but the diagnosis
hooks in the prior handoff led to dead code.

---

## What landed

### SCRIP `d805b0fe` — BB_PL_CALL call/1 meta-fallback in mode-2

Three files, +28 lines:
- `src/lower/bb_exec.c` (+15) — BB_PL_CALL handler intercepts
  `callee=="call" && carity==1` before `pl_bb_lookup`, converts
  `zc->args[0]` via existing `pl_node_to_term`, derefs through
  `g_pl_env`, dispatches via new `pl_call_term`.
- `src/runtime/interp/pl_runtime.c` (+8) — drops `static` on
  `pl_invoke_var_goal` (forward-decl); adds public wrapper
  `int pl_call_term(Term *gt) { return pl_invoke_var_goal(gt, NULL); }`.
- `src/runtime/interp/pl_runtime.h` (+5) — exports `pl_call_term` with
  doc-comment.

Empirically verified against six test programs:
- `call(true)` in if-then-else → `ok` (was `fail`)
- `call(true), write(ok), nl` → `ok` (was silent / failure)
- `call(fail)` in if-then-else → correctly takes else branch
- `G = true, call(G)` → `ok`
- `G = write(hello), call(G)` → `hello`
- Bare `true` (no `call` wrapper) — unchanged behavior, `ok`

---

## Diagnosis correction

The prior handoff (`SWI-2C-FOLD-REVIVAL`) pointed at three hooks in
`pl_runtime.c`:
- `pl_invoke_var_goal` at line 845
- `pl_term_to_synth_expr` TERM_ATOM branch at line 805
- `interp_exec_pl_builtin` `true` arm at line 894

**All three are dead code in mode-2 `--interp`.** Verified by adding
`SCRIP_TRACE_CALL1` env-gated `fprintf`s at the call/1 arm entry, at
`pl_invoke_var_goal`'s entry, and at each early-return inside. None
fired on the reproducer `call(true)`.

The real mode-2 path:
1. `--interp` lowers `:- main.` to `SM_BB_PL_INVOKE("main/0", 0)`
   (`scrip --dump-sm` confirms).
2. `sm_interp.c:707` SM_BB_PL_INVOKE handler calls
   `pl_bb_once_proc_by_name("main", 0)` → `bb_broker(pnode, bb_once)`.
3. Inside `main`'s BB graph, `call(Goal)` was lowered as `BB_PL_CALL`
   with `callee="call", carity=1` (lower_pl.c:443 catch-all).
4. `bb_exec.c:3259` BB_PL_CALL handler does
   `pl_bb_lookup("call/1", 1)` → returns NULL (no user predicate
   named `call/1`).
5. Returns FAILDESCR at line 3270.

`pl_builtin_style` (`lower_pl.c:202`) has no entry for `call`, so the
lowerer never routed it to the dedicated builtin path either. The
`interp_exec_pl_builtin` switch arm for `call/1` at line 1051 of
`pl_runtime.c` is reachable from a legacy AST-walking interp path that
mode-2 `--interp` doesn't take.

This means the fix could **not** live in `pl_runtime.c` — `bb_exec.c`
was the right hook all along.

---

## Why bb_exec.c BB_PL_CALL is the right hook (not lower_pl.c)

Two alternatives were considered:

**Option 1 (lowerer fix):** detect `call/N` in `lower_pl_goal`, rewrite
to direct lowering of arg-0 as a goal. Inline rewrite if arg-0 is
syntactically known; runtime synthesis if it's a variable.

Pros: clean architecturally — `call/N` becomes a lowering concern, not
a runtime concern.

Cons: would ripple into mode-3/4 native emit paths (the BB graph
shape changes, which changes what `bb_pl_call.cpp` and friends emit).
Per RULES.md FACT and per the GOAL-PROLOG-BB watermark, mode-3/4
template-byte gates are sensitive — better to not perturb them.

**Option 2 (runtime fallback — taken):** intercept in bb_exec.c
BB_PL_CALL handler. Lowering unchanged → mode-3/4 emit bytes unchanged
→ FACT-safe.

Cons: ad-hoc — `call` is now a special case in bb_exec.c's BB_PL_CALL
arm. If more meta-predicates need similar treatment, this approach
doesn't generalize as well as the lowerer path.

Net: option 2 is the small, narrow, FACT-safe fix that matches the
"highest leverage" framing of the prior handoff. Option 1 is the
principled long-term direction (a future MET-CALL track, perhaps).

---

## Gates at this HEAD

All mode-2 `--interp`, **unchanged from `a88f1e68`** (no movement
because most call/1-using SWI tests were already PASS-by-accident
via `SF=:=0`):

| Gate | Result | Notes |
|---|---|---|
| GATE-1 smoke_prolog | 5/5 | |
| GATE-2 crosscheck | 132/0 | 5 ORACLE_MISS (frontend gap) |
| GATE-3 rung suite mode-2 | 104/3 (104/107) | |
| GATE-SWI plunit | 53/4 (53/57, 92%) | 4 MISS: catch, variant, float_compare, max_integer_size |
| BB honest | 128/0 (ABORT=0) | |
| FACT rule grep | 0 violations | |

Mode-3 (`--run`) rung_suite shows 0/107 at this HEAD — **pre-existing,
verified by stashing the fix and rebuilding clean: same 0/107**. The
"want: 123|\ngot: |" diff in the rung_suite output suggests a
wrap-script formatting issue, not a Prolog-runtime regression. Not
introduced by this session.

Mode-4 corpus rung blocked on missing `out/libscrip_rt.so` in this
build environment — also pre-existing.

---

## Why the gate number does not move

`call/1` on a bound atom now works. The SWI plunit gate is at
`53/57 (92%)` — same as the prior handoff. Reasons:

1. Of the 53 PASSing suites, most pass via the `SF=:=0 -> PASS` clause
   in `pj_suite_verdict` (false-positive: zero test bodies ran). With
   the SWI-2c fold revival, test bodies are now *stored* in
   `pj_test/4`. With the SWI-2d call/1 fix, `pj_run_one`'s
   `catch(Goal, _, ...)` can now invoke `call(Goal)` on a bound atom
   successfully.
2. **But test bodies that use `call/N` for N≥2 (e.g. `test_call.pl`'s
   `call1_a(X = 42)`) still don't run.** And many test bodies use
   builtins or features not yet implemented (forall, bagof, setof,
   variant, catch with specific exception types, ...).
3. So the gate stays at 53/57 — but the *meaning* of the PASSes is
   slowly shifting from "no body ran, defaulted to SF=0 PASS" toward
   "body ran and succeeded". A future SWI-5 (EMPTY verdict) would
   reveal how many PASSes are still false-positives.

The fix is on the critical path even though the number doesn't move
yet. Without it, no plunit test body can be invoked at all.

---

## Next session options

1. **call/N for N>1** (partial application). Now that the dispatch
   path is established in `bb_exec.c`, extending to N>1 is mechanical:
   convert the goal Term, walk its compound args, append the extras
   from `zc->args[1..]`, build a new compound, dispatch as before.
   Likely closes most of `rung33_bridge_callN` (currently 1/5).

2. **SWI-5 (EMPTY verdict)** — change `pj_suite_verdict` in
   `plunit.pl` to emit `EMPTY` (or `FAIL`) when zero tests ran. Makes
   the gate number honest. May invert the gate (some PASSes flip to
   EMPTY). Independent of #1.

3. **PL-RT-ASSERTZ** — runtime assertz so plunit.pl can ditch the
   nb_setval workaround. Needed before plunit can store dynamically-
   discovered test results.

4. **WAM-CP-13** — longjmp-free catch + mode-4 catch emit. Would
   close the `catch` SWI miss.

5. **WAM-CP-6 LCO** — principled SEGFAULT-CLUSTER fix.

Recommendation: **#1 next**. It's the natural follow-on, small in
scope, and converts the SWI-2d fallback from a one-off into a
general meta-call handler.

---

## Files touched this session

- `SCRIP/src/lower/bb_exec.c` (+15) — BB_PL_CALL call/1 fallback
- `SCRIP/src/runtime/interp/pl_runtime.c` (+8) — public wrapper
- `SCRIP/src/runtime/interp/pl_runtime.h` (+5) — export

## Commit identity

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
