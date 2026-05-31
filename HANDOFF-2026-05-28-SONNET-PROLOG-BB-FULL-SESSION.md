# HANDOFF 2026-05-28 — Sonnet 4.6 — PROLOG-BB: Full session summary

**Repos:** SCRIP `8c556f29` · .github `107b42b4` · corpus untouched.

---

## What landed this session (four commits to SCRIP)

### 1. `88bacd2a` — FACT cleanup Steps 2+3 (picked up from Opus Step 1)

`bb_emit_asm_result_pairs()` helper added to `emit_str.cpp`/`emit_str.h`. Reconstructs
(site, label, is_def) metadata from `xa_bb_emit_pair_*` arrays — templates need no
`bin.*` access. Also added `#include "emit_globals.h"` to `emit_str.cpp`.

Six combinator templates stripped to pure byte production:
`bb_pat_fence/alt/cat`, `bb_pl_seq/ite`, `bb_succeed` — wrappers swapped to
`bb_emit_asm_result_pairs`. `flat_drive_fence` 0-children path updated (Option B):
`EMIT_PAIR_JMP(lbl_γ) + EMIT_PAIR_DEF_JMP(lbl_β,lbl_ω) + EMIT_PAIR_FILL` replaces
bare `FILL`; dead special-case block in template removed.

**FACT grep: 0 violations.** All gates byte-identical.

### 2. WAM-CP-6 (LCO) — attempted, reverted, documented

Three approaches tried: naive env reuse, global trampoline flag, goto-restart loop.
All reverted — root cause: C stack grows O(N) because `bb_exec_once` calls itself
for every `BB_PL_CALL`. Eliminating Prolog env allocation does NOT eliminate the C
frame. Fix requires converting `bb_exec_once` to never call itself recursively — every
`BB_PL_CALL` pushes a call-descriptor onto an explicit stack; the outer loop drives it.
Full design in `HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md`.

Tree clean at `88bacd2a` after revert.

### 3. `abdf4290` — plus/3 bidirectional + `**` integer power

`plus/3` added as `PL_BI_CHAIN` builtin: handles all three binding modes
(XY→Z, XZ→Y, YZ→X). `**` operator now returns integer when both operands are
non-negative integers (mirrors existing `^` behavior).

**GATE-3: 96 → 100/107** (+4: rung18 ×3, rung23 ×1).

### 4. `8c556f29` — nb_setval/getval + aggregate_all

`nb_setval(Key,Val)` / `nb_getval(Key,Val)`: non-backtrackable global variable store
via open-addressing hash table `g_pl_nb[64]` (atom_id keyed). Both added as
`PL_BI_CHAIN` in lower_pl.c + executor arms in bb_exec.c.

`aggregate_all(Template, Goal, Result)`: supports `count`, `sum(V)`, `max(V)`,
`min(V)` templates. Runs the goal graph in a findall-style loop (bb_exec_once +
bb_exec_resume), accumulates, unifies Result. Goal looked up via `pl_bb_lookup`.

**GATE-3: 100 → 104/107** (+4: rung27 ×4).

---

## Gates at HEAD `8c556f29`

| Gate | Count | Notes |
|---|---|---|
| GATE-1 smoke | 5/5 | |
| GATE-2 crosscheck | 132/0 | 5 ORACLE_MISS (frontend gap) |
| GATE-3 mode-2 | **104/107** | +8 this session |
| GATE-4 mode-4 minimal | 4/4 | |
| Full mode-4 corpus | 54/107 | unchanged |
| FACT grep | 0 | bb_capture.cpp line 23 is a comment |

---

## Remaining 3 failures (GATE-3)

- **rung15** `abolish_abolish_then_reassert` — dynamic DB: `abolish/1` then `assert`
  of same predicate. Requires dynamic predicate table mutation.
- **rung27** `succ_or_zero` — corpus gap: `.pl` file is missing the `succ_or_zero/2`
  definition (JVM oracle has it, Prolog source doesn't). Not a runtime bug.
- **rung30** `dcg_pushback_rest` — DCG frontend gap (`pushback_rest`/`phrase/3` with
  rest arg). Frontend issue, not executor.

---

## NEXT session candidates (in priority order)

1. **WAM-CP-6 (LCO) — proper trampoline refactor.** Convert `BB_PL_CALL` in
   `bb_exec.c` to push a `bb_call_req_t` descriptor instead of calling `bb_exec_once`
   recursively. Outer loop in `bb_exec_once` drives the descriptor stack. LCO then
   eliminates the frame push when `is_last && g_pl_bfr == entry_bfr`. Full design spec
   in `HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md`.
   Gate: `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 O(1) stack.

2. **WAM-CP-13** — mode-4 catch/throw emit + longjmp-free CP-barrier unwind.
   `bb_pl_catch.cpp` currently stubs α/β → jmp ω. Real emit reuses WAM-CP-9 r12
   + saved-state-slot pattern. Gate: rung28 mode-4 (currently 0/5 in mode-4 corpus).

3. **WAM-CP-9 Steps B–D** — committed-ITE node + `!` in `(A;B)` disjunction-cut.

4. **rung15 abolish/reassert** — dynamic DB mutation after abolish. Small scope.

---

## Commit identity

```
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Verification

```
cd /home/claude/SCRIP && git log origin/main --oneline -1
# 8c556f29 Prolog BB: nb_setval/getval + aggregate_all(count/sum/max/min) builtins (rung27 +4, GATE-3 100→104)

cd /home/claude/.github && git log origin/main --oneline -1
# 107b42b4 Prolog BB: nb_setval/getval + aggregate_all watermark — GATE-3 104/107
```
