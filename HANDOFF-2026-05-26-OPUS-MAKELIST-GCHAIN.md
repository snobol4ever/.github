# HANDOFF — 2026-05-26 — Opus Session (H-4 MAKELIST γ-chain + SCRIP_NO_AST_WALK verdict)

**Goal:** GOAL-ICON-BB, Phase H / H-4 (N-ary kinds via γ-chain).
**SCRIP:** `82ec79f8` PUSHED (rebased onto 340b14b9, clean).
**.github:** this file + PLAN.md watermark.
**Build:** ✅ GREEN · **smoke_icon 5/5** · **broker(smoke) 19** · **rungs --interp 189/42/35** (was 181).

---

## What landed — H-4 N-ary CALL fix (commit `82ec79f8`)

`src/lower/lower_icn.c`, +11/-4, one file.

### The bug
`TT_MAKELIST` (`[e1,…,eN]`) lowered each element to an arg box but wired only
`args[0]→α` and `args[1]→β`. The `BB_CALL` executor (`bb_exec.c:166-178`) reads
`nargs = nd->ival` and walks the **arg γ-chain** `α→γ→γ→…`, so elements 3..N were
unreachable. `[1,2,3]` therefore built a malformed/empty list: `*L`==0, `L[1]`
empty, `!L` yielded nothing. The list literal itself was broken — `!L` failing
was only the symptom that surfaced it.

### The fix
```c
if (args && n >= 1) {
    nd->α = args[0];
    for (int j = 0; j + 1 < n; j++) args[j]->γ = args[j + 1];
}
```
Identical to the already-correct general function-call site at `lower_icn.c:333`.
The other two BB_CALL-family sites are correct as-is: `BB_SEQ_GEN` (line 311) is
guarded to ≤2 args (α/β by contract), `BB_FIND_GEN` (line 287) uses positional
α/β/γ operands (executor reads those ports directly).

Also landed (was uncommitted in tree at session start, verified correct):
`TT_ITERATE` (`!E`) wires the iterable onto α. Matches `BB_LIST_BANG` executor
(`bb_exec.c:1019`) which caches `α->value` on state==0 and walks `counter`,
returning γ per element / ω on exhaustion.

### Rungs recovered (181→189, +8)
All of rung22 (lists): `bang_list`, `get`, `pull`, `push_put_size`, `put_bang`,
plus rung20/rung21 cases that depend on list construction. The whole list-literal
family was gated on this single γ-chain bug.

---

## ⛔ VERIFIED FINDING — `SCRIP_NO_AST_WALK` env var is DEAD (Lon flagged; confirmed)

Lon asked whether the env var is a useless/meaningless operation. **It is.**

- `grep -rn '"SCRIP_NO_AST_WALK"' src/` → **empty**. The string is never passed
  to `getenv`. Prefixing `SCRIP_NO_AST_WALK=1` on a scrip invocation sets a shell
  env var the program never reads → **no-op**. Prior "honest under
  SCRIP_NO_AST_WALK=1" claims were vacuous (identical to a plain run).
- The *real* tripwire is the always-on macro `NO_AST_WALK_GUARD(fn)`
  (`src/runtime/interp/icn_runtime.h:121` and `.c:18`). It fires unconditionally
  when `g_sm_dispatch_active && !g_ast_pump_active && g_lang == LANG_ICN`,
  `abort()`-ing with "FATAL: <fn> reached from SM dispatch (Icon BB incomplete)".
  Guard sites: `eval_pat.c:18`, `interp_ref.c:5`, `interp_call.c:90`.
  **This guard is LIVE and load-bearing — keep it.** It provides the honesty
  check unconditionally; no env var needed.

### CLEANUP for next session (~5 min, low risk)
Strip the meaningless `SCRIP_NO_AST_WALK=1` prefix and "honest under…" comments
from the only two scripts that set it (they rely on the abort, which the
always-on guard already produces):
- `scripts/icon_bb_probes.sh` (lines 46, 64, 66, 69, 102, 119, 124, 140, 158)
- `scripts/test_prolog_bb_honest.sh` (lines 2, 33, 45)
Rename `test_prolog_bb_honest.sh`'s header comment to drop the env-var premise.
No C change — the macro stays. Re-run both scripts after; behavior must be
byte-identical (proves the prefix was inert).

---

## NEXT (unchanged priority)
**H-1** — extend the lowerer to the full 4-attribute signature
`lower_icn_expr_node(cfg, e, γ_in, ω_in, &α_out, &β_out)` so inherited γ/ω are
threaded statically through the graph (not supplied at runtime by the executor).
Currently only 2/49 Icon BB kinds wire all four ports at lower-time
(BB_KEY_GEN full αβγω, BB_ALT αγω); the rest rely on executor continuation
threading. H-1 is the prerequisite for Mode-4 emit of nested IF/generators.

## Watermark
```
SCRIP: 82ec79f8 — BUILD GREEN, smoke 5/5, broker 19, rungs 189/42/35
.github: this file + PLAN.md BB-Ladder row (Sess 2026-05-26i)
GOAL: GOAL-ICON-BB Phase H
NEXT: (cleanup) strip dead SCRIP_NO_AST_WALK prefix from 2 scripts;
      (main) H-1 4-attribute lowerer signature for static γ/ω threading.
```
