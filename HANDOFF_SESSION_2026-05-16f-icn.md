# HANDOFF — Session 2026-05-16f (GOAL-ICON-BB-JCON)

**Date:** 2026-05-16
**Goal:** GOAL-ICON-BB-JCON — `every write(fact(5))` over-iteration triage
**Claude:** Opus 4.7

---

## Headline

**Category 3 decomposed into two independent fixes; Fix #1 landed.** The
"emits 120 five times" symptom described in the 2026-05-16e handoff was
actually masking a deeper architectural bug — `fact(5)` itself was
returning a null/empty value, not 120, due to recursive proc calls
wiping their caller's mid-evaluation IR graph state. With Fix #1
(`IJ-CALL-SNAPSHOT`, one4all `398776da`), `write(fact(5))` correctly
yields `120`. `every write(fact(5))` now loops emitting the correct
value (`120` ad infinitum) instead of blank lines — confirming Fix #2
(IR_EVERY exit-on-single-shot-proc) is a separate, smaller problem.
Gates flat at watermark.

---

## Work completed this session

### IJ-CALL-SNAPSHOT — one4all@398776da (ir-run 105 → 105, no rung flip)

**Diagnosis path.** Started reproducing `rung02_proc_fact.icn`:
```icon
procedure fact(n)
  if n = 0 then return 1;
  return n * fact(n - 1);
end
procedure main()
  every write(fact(5));
end
```
Expected: `120` (single line). Observed at watermark: **1,000,000 blank
lines** (NOT "120 five times" as the prior handoff stated — that turned
out to be a misreading; the actual symptom is a null-value infinite
loop). The handoff hypothesis ("IR_ICN_PROC_GEN re-yields" or "IR_EVERY
doesn't stop on proc return") was on the right track for the loop but
missed that the value itself was wrong.

Stripping `every` away as a control:
- `write(fact(0))` → `1` ✓
- `write(fact(1))` → *blank* ✗
- `write(fact(5))` → *blank* ✗

So the recursive branch (`return n * fact(n-1)`) was producing null,
not 120 with `every` repeating. Triangulating on operand orientation:
- `2 * fact(1)`         → blank
- `fact(1) * 2`         → 2
- `n * fact(n-1)` at n=1 → blank
- `fact(n-1) * n` at n=1 → 1
- `0 + fact(1)`         → blank
- `fact(1) + 0`         → 1
- `2 * id(3)` (non-recursive) → 6

**Pattern:** recursive call on the **right** of a binop returns null;
on the **left**, fine. The asymmetry is the smoking gun.

**Root cause.** Two interacting facts:
1. `is_suspendable(TT_FNC) = 1` in `icn_runtime.c:307`, so any binop
   with a function call lowers to `IR_BINOP_GEN` (not `IR_BINOP`).
2. `IR_BINOP_GEN` in `ir_exec.c:191` reads `nd->c[0]->value` AFTER
   evaluating both children — into the `icn_binop_apply` call. This
   is fine if both children are pure leaf evaluations, but…
3. `IR_CALL` user-proc dispatch (line 99-117) does:
   ```c
   IR_reset(proc_table[_pi].ir_body);
   out = IR_exec_once(proc_table[_pi].ir_body);
   ```
   and `IR_exec_once` itself calls `IR_reset(cfg)`. When the callee
   IS the same proc that's currently executing (recursion), `IR_reset`
   zeros `value`, `counter`, `state` on **every node of the shared
   graph** — including the outer activation's literal `2`, the outer
   IR_BINOP_GEN itself, and so on.

So in `2 * fact(1)`: outer `IR_BINOP_GEN` evals c[0] (literal 2) →
`c[0]->value = INTVAL(2)`. Then evals c[1] (`IR_CALL` fact(0)) → inner
`IR_exec_once` calls `IR_reset` → blows c[0]->value back to FAILDESCR.
IR_CALL writes c[1]->value = INTVAL(1). Then `icn_binop_apply(MUL,
c[0]->value=FAILDESCR, c[1]->value=1)` → propagates failure → blank.

`IR_BINOP` (the non-gen path) happens to be **correct by accident**
because it captures `lv` into a local *before* the inner call:
```c
IR_exec_node(nd->c[0]);
DESCR_t lv = nd->c[0]->value;   /* survives the inner reset */
...
IR_exec_node(nd->c[1]);
DESCR_t rv = nd->c[1]->value;   /* set after the inner reset, fine */
```

**Fix.** Architectural: snapshot the callee's per-node mutable state
(`value`, `counter`, `state` — exactly what `IR_reset` zeroes) before
`IR_exec_once`, restore after. Always-on, uniform; cost is
`malloc(n * 40 bytes)` per user-proc call. New helpers
`IR_snapshot_state` / `IR_restore_state` in `scrip_ir.c`, declared in
`IR.h`. Snapshot taken on the callee's `ir_body` regardless of
caller — when they're the same proc (recursion), this preserves the
caller's activation; when different (cross-proc), it's harmless
overhead.

**Result.**
- `write(fact(5))`         → `120` (was: blank)
- `n * fact(n-1)` at n=1   → `1`   (was: blank)
- `2 * fact(1)`            → `2`   (was: blank)
- `every write(fact(5))`   → `120` repeated (was: blank repeated) — Fix #2 still needed for termination

**Gate counts (median of 3 runs, all match watermark):**
- GATE-1 smoke_icon:   PASS=5  FAIL=0
- GATE-2 broker:       PASS=19 FAIL=30
- GATE-3 ir_all_rungs: PASS=105 FAIL=125 XFAIL=35 TOTAL=265
- GATE-4 no_ast_walk:  PASS=277 FAIL=0 ABORT=0

The fix doesn't flip rung02_proc_fact PASS because `every` still
infinite-loops — that's Fix #2. But the fix is architecturally
necessary for any future stateful node (IR_EVERY, IR_REPEAT, etc.)
appearing inside a recursive proc body; without it those would all
have subtle corruption bugs.

---

## Detour worth recording

During this session I temporarily added an IR_EVERY guard
(`if (!_c0_is_gen) break;` consuming `nd->ival2 = is_suspendable(c[0])`
set at lower time) thinking it'd be Fix #2. It would NOT be:
`is_suspendable(TT_FNC) = 1` returns 1 for every function call,
including non-generator ones like `write(fact(5))`. So `_c0_is_gen`
would be 1 and the loop wouldn't exit. Reverted.

The right signal for Fix #2 is **whether the called proc's body
contains a `TT_SUSPEND`** (i.e. is the proc itself a generator?) —
not whether the AST node is "suspendable". This bit can be computed at
proc-registration time and stored on `IcnProcEntry`, then consulted
at IR_EVERY when c[0]'s outermost node is an IR_CALL to a user proc.

---

## Final state — push confirmed

```
one4all: 398776da  (rebased onto 0b0dc9d3 from parallel session)
.github: HANDOFF + PLAN + GOAL updates to be pushed last per RULES

ir-run:  105/265   honest: 277 PASS / 0 FAIL / 0 ABORT
smoke_icon: 5/5    broker: 19/49
cross-lang smokes: snobol4 7/7, raku 5/5, snocone 5/5, rebus 4/4, prolog 3/5
```

---

## Next session pickup

**Target:** Fix #2 — `every write(fact(5))` over-iteration.

**Plan:**
1. Add `int is_generator` (or rename: `has_suspend`) field to
   `IcnProcEntry` in `icn_runtime.h`. Default 0.
2. At proc registration (where `proc_table[i].ir_body` is built),
   walk the body and set `is_generator = 1` if any `IR_SUSPEND` node
   exists. Alternatively, set it at AST time via the existing
   `proc_has_suspend(tree_t*)` helper in `icn_runtime.c:295`.
3. In `IR_EVERY`'s executor (`ir_exec.c:260`), detect when c[0]
   resolves to an `IR_CALL` to a user proc and consult that proc's
   `is_generator` bit. If non-generator, break after one iteration.
4. Edge case: c[0] is a chained call (`write(fact(5))`) — the
   outermost call is `write`, which IS variadic but `write` itself is
   single-shot. So actually the rule simplifies: **if c[0]'s top is
   IR_CALL and the resolved proc is non-generator, single-shot**.
   The argument `fact(5)` is single-shot by the same rule recursively.
5. Run GATE-3 to measure ir-run delta. Expected: +5 to +10 (rung02_proc_*,
   maybe some rung03_suspend_* if the user-proc-generator path is also
   getting confused by this).

Latent bug to file: `every (s := "" | "a") do write(s)` infinite-loops
in IR mode at watermark — not blocked on this goal but worth a ticket.

---

## PST-RAKU-3b COMPLETE — 2026-05-16 (session 30/59)

**one4all**: `3b11ec53` PST-RAKU-3b: raku.y pure syntax tree — all violations fixed
**corpus**: `e662a5a` PST-RAKU-3b: parser_raku.sc mirror — fix finish_for_range in-place append (V4)
**.github**: `069243fa` PST-RAKU-3b ✅: goal complete — all Icon+Raku PST violations fixed and gated

All 6 Raku violations fixed. Gates: smoke_raku 5/5, smoke_icon 5/5, scrip_all_modes 2/0, crosscheck_snobol4 6/6.
Next goal: PST-REBUS-PROLOG at PST-PL-6a.
