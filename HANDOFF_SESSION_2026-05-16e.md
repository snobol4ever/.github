# HANDOFF — Session 2026-05-16e (GOAL-ICON-BB-JCON)

**Date:** 2026-05-16
**Goal:** GOAL-ICON-BB-JCON — Icon BB JCON failing-rung triage
**Claude:** Opus 4.7

---

## Headline

**ir-run: 82/265 → 105/265 (+23 in one session)** via two commits, each landing a single high-leverage edge in the Icon AST→IR lowering. Both predicted ranges from the prior survey met or exceeded. GATE-2 broker bonus: 18 → 19. All other gates flat or unchanged.

---

## Work completed this session

### IJ-SCAN — one4all@1841f7de (ir-run 82 → 97, +15)

**Diagnosis.** The 2026-05-16d failing-rung survey grouped 6+ FAIL categories under "pattern-scan ops need fresh SM/BB lowering": rung05_scan_*, rung06_cset_any/many/upto, rung08_strbuiltins_find/match/move/tab, plus rung11/14/15/17/32 string-related FAILs. Tracing the actual code path:

- `--interp` on Icon goes through `sm_preamble` → `sm_interp_run` → `SM_BB_PUMP_PROC` → `icn_bb_pump_proc_by_name`. When a proc has an `ir_body`, execution flows into `IR_exec_node` on the IR.
- `IR_CALL` (built from `TT_FNC`) dispatches via `icn_try_call_builtin_by_name` (interp_eval.c:205).
- **`any`/`many`/`upto`/`match`/`move`/`find`/`tab` are all already fully implemented there** (lines 900–1004), using the global `scan_subj`/`scan_pos` set by the `?` operator.

The real blocker was upstream: `lower_icn_expr_node` returned NULL for:
- `TT_SCAN` (`subj ? body`) — no case at all
- `TT_KEYWORD` (`&pos`, `&subject`, `&null`, `&fail`) — no case at all
- `&`-prefixed `TT_VAR` — explicit `if (e->v.sval[0] == '&') return NULL;`

NULL from any subexpression aborts the whole proc-body IR build → `proc_table[i].ir_body == NULL` → fallback to the `SM_BB_EVAL` stub which prints `[NO-AST] SM_BB_EVAL stub: needs fresh SM/BB lowering` and fail-exits.

**Fix.** Three edges added:
1. `IR_ICN_SCAN` IR kind (`IR.h`) — c[0]=subject, c[1]=body. Executor (`ir_exec.c`) saves `scan_subj`/`scan_pos` onto `scan_stack`, evaluates subject, sets globals, evaluates body, restores from stack.
2. `IR_ICN_KEYWORD` IR kind — `sval` holds full `"&name"`. Executor returns `STRVAL(scan_subj)` for `&subject`, `INTVAL(scan_pos)` for `&pos`, `NULVCL` for `&null`, `FAILDESCR` for `&fail`, else falls back to global var lookup.
3. `lower_icn.c` — TT_SCAN, TT_KEYWORD, and `&`-prefixed TT_VAR now lower to the above kinds.

**Result.** Recovers 15 rungs in one commit — all 6 named categories at once, plus rung11 (`bang_str`), rung14 (`limit_str`), rung15 (`iterate_string`, `real_swap_str`), rung17 (`real_arith_string_conv`), rung32 (`strret_every`).

**Latent bug exposed (NOT a regression).** `rung36_jcon_lexcmp` previously exited 0 because its `&null` reference failed to lower, falling back to `SM_BB_EVAL` stub which fail-exits cleanly. With `&null` now lowering, the proc body reaches a pre-existing `every (s := A | B) do body` infinite-loop bug. Reproduces at watermark on the minimal program `every (s := "" | "a") do write(s)` — bug is not introduced here, just newly observable. GATE-4 PASS count goes 278 → 277 because this rung now times out instead of exiting 0; but FAIL=0 ABORT=0 (the substance of the honest gate) is preserved.

---

### IJ-BINOP-GEN — one4all@05097be3 (ir-run 97 → 105, +8)

**Diagnosis.** `(1 to 3) * (1 to 2)` produced only `1, 4` instead of the cross-product `1,2,2,4,3,6`. Plain `TT_MUL` → `IR_BINOP`, a single-shot executor that evaluates each operand once and yields one result. Augmented assignments already used `IR_ICN_BINOP` (the older bb_node_t-based generator path) for cross-product, but bare binops did not.

**Fix.** New `IR_BINOP_GEN` IR kind:
- Same encoding as `IR_BINOP`: `ival = IcnBinopKind`, `ival2 = is_relop`, `c[0]/c[1] = lhs/rhs`.
- Executor is a state machine: state==0 seeds both sides; state==1 advances inner generator (c[1]) first, then outer (c[0]) with c[1] reset (`->state = 0`) on c[1] exhaustion. On relop fail, same advance logic runs in a retry loop.
- **Per-child gen-kind tracking** is the subtle bit: a child is "really" a generator only if its IR kind is in the set `{IR_ICN_TO, IR_ICN_TO_BY, IR_ICN_UPTO, IR_ALT, IR_ALTERNATE, IR_BINOP_GEN, IR_ICN_ITERATE, IR_ICN_LIMIT, IR_ICN_PROC_GEN, IR_TO_BY}`. Non-generator operands (literals, vars) succeed on every `IR_exec_node` call and would otherwise drive an infinite loop on outer relops like `5 > ((1 to 2) * (3 to 4))`. With the tracking, non-generator children are single-shot — they're not re-pumped.

In `lower_icn.c`, the TT_ADD/SUB/MUL/DIV/MOD/LT/LE/GT/GE/EQ/NE/CAT case now calls `is_suspendable(e->c[0]) || is_suspendable(e->c[1])` (extern'd from `icn_runtime.c`) and picks `IR_BINOP_GEN` vs `IR_BINOP`.

**Result.** rung01_paper_mult, rung02_arith_gen_paper_mul, plus 6 other generator-binop rungs now pass. Bonus: one cross-language broker program now passes (18 → 19).

---

## Final state — push to remote confirmed

```
one4all: 05097be3 → integrated into remote (then PST-SN4-1b 7013a856,
                    PST-SN4-1d 8ba8f599 landed on top from parallel session)
.github: 88fd98b2 → integrated into remote (then PST-SN4-1b d2d4f4a6,
                    PST-SN4-1d 9c68ba1b, HANDOFF-c 22f4bc88 landed on top)

ir-run:  105/265   honest: 277 PASS / 0 FAIL / 0 ABORT
smoke_icon: 5/5    broker: 19/49
cross-lang smokes: snobol4 7/7, raku 5/5, snocone 5/5, rebus 4/4, prolog 3/5
```

Both repos pulled clean fast-forward post-session — the PST-SN4 work touched a different goal (`GOAL-PARSER-PURE-SYNTAX-TREE`) and a different row in PLAN.md, so no conflict.

---

## Next session pickup

**Target:** Category 3 from the 2026-05-16d survey — `every write(fact(5))` over-iteration. The proc `fact(5)` should yield once but emits `120` five times. Suggests either:
- `IR_ICN_PROC_GEN` (the ucontext-based user-proc generator) re-yields after return when it shouldn't, or
- `IR_EVERY` doesn't stop on a proc that returns (vs suspends).

Affects rung02_proc_* and rung03_suspend_*. Expected yield uncertain; survey didn't quantify. Probably +3–8 rungs.

**Inspection starting points:**
- `src/lower/ir_exec.c` — `case IR_EVERY` (loops while c[0] doesn't FAIL; check that a `return` value isn't being re-yielded).
- `src/lower/ir_exec.c` — `case IR_ICN_PROC_GEN` (and the GeneratorState ucontext plumbing).
- `src/lower/lower_icn.c` — how `TT_FNC` becomes `IR_CALL` vs `IR_ICN_PROC_GEN`. Suspendable user-procs need the generator path; non-suspendable should be plain calls.

**Latent bug (still on the radar, don't block on it):** `every (s := "" | "a") do write(s)` infinite-loops in IR mode. Pre-existing at watermark; exposed by IJ-SCAN. File as separate ticket when convenient.

---

## Files touched (commits already pushed)

**one4all:**
- `src/include/IR.h` — added `IR_ICN_SCAN`, `IR_ICN_KEYWORD`, `IR_BINOP_GEN`
- `src/lower/ir_exec.c` — executors for the three new kinds
- `src/lower/lower_icn.c` — TT_SCAN, TT_KEYWORD, `&`-VAR, and gen-aware binop case

**.github:**
- `GOAL-ICON-BB-JCON.md` — Completed steps table, NEXT step, Watermark all updated
- `PLAN.md` — Icon BB JCON row updated to current state
