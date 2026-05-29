# HANDOFF 2026-05-29 Opus 4.8 — Prolog BB WAM-CP-6 Phase B2 (indexed-LCO frame reuse)

**one4all commit:** `167f31cb` (parent `d9062238` WAM-CP-8 first-arg indexing).
**Files:** `src/lower/bb_exec.c` ONLY. +95 / −22, additive. No enum / emitter / template /
lowering / FACT change. Pure mode-2 interpreter logic.

## What landed

Phase B2 pairs **WAM-CP-8 first-arg indexing** with the **WAM-CP-6 B1 redirect sentinel**
so a uniquely-indexed tail-position multi-clause call flattens to O(1) C stack. The benchmark
named in the goal file — `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 — now runs in
constant C stack.

Two surgical changes, both in `bb_exec.c`:

### (1) BB_CHOICE index path — run the unique cp-free-except-tail clause CP-free

The WAM-CP-8 no-CP commit previously gated on `bb_body_single_solution` (NO
BB_CHOICE/BB_PL_ALT/BB_PL_CALL at all). Extended to ALSO accept
`bb_body_cp_free_except_tail` (the looser check that exempts a tail-position BB_PL_CALL).
When the bound first arg selects exactly one clause whose body is cp-free-except-tail, the
clause runs via `bb_exec_once(body)` WITHOUT `pl_cp_push` — leaving `g_pl_bfr` unchanged.

**Why this is the unlock:** in the prior baseline the recursive `count(N1)` tail call always
saw `g_pl_bfr != NULL`, because count's own multi-clause BB_CHOICE pushed a clause-selection
CP that outlived the descent (LCO trace: every recursive call `tail=1 det=0 eligible=0`,
`bfr_before != bfr_after`). That live clause CP is exactly what defeats the tail-call LCO
gate. Eliding it (the body is provably ≤1 solution: the lone tail call is the only generator
and its own determinism governs the continuation) lets the tail call see a clean spine.

### (2) BB_PL_CALL B1 gate — redirect into the index-resolved clause body

New static helper `pl_choice_unique_indexed_body(callee, first_arg)` mirrors the BB_CHOICE
index logic: returns the single clause body graph iff the callee entry is a BB_CHOICE with a
populated index AND the deref'd first arg resolves to `ncand==1` AND that body is
`bb_body_cp_free_except_tail`; else NULL.

The B1 gate (formerly: tail-pos && `g_pl_bfr==NULL` && entry != BB_CHOICE &&
cp_free_except_tail) was restructured into a single `if (lco_tail_pos && g_pl_bfr == NULL)`
block with two arms sharing the arg-binding + reset + sentinel + return:
- **B1 arm** (entry != BB_CHOICE, cp_free_except_tail) → redirect target = `_bcfg` (callee
  graph). Behavior identical to the prior B1.
- **B2 arm** (entry == BB_CHOICE) → bind args into the LCO env, key
  `pl_choice_unique_indexed_body` on `callee_env_lco[0]`; if it returns a body, redirect
  target = that clause body graph (NOT the BB_CHOICE — bypassing the choice node's own
  `bb_exec_once` which would otherwise re-nest a frame per iteration).

The existing redirect sentinel (`g_pl_tail_redirect_cfg/_entry`) and both driver-loop consume
sites (`bb_exec_once` / `bb_exec_resume`) are unchanged — the sentinel just now carries a
clause-body graph instead of only single-clause callee graphs.

## Proof

- `count(1000000)` prints `done` at **1MB** stack (O(N) C recursion dies ~6k frames);
  `count(10000000)` at 8MB. Both exit 0.
- `sumto(0,A,A):-!. sumto(N,A,R):-N>0,A1 is A+N,N1 is N-1,sumto(N1,A1,R).`
  `sumto(500000,0,R)` → `125000250000` exact at **1MB** stack — binding propagation through
  flattened frames is correct (accumulator is the common real-world tail-recursion shape).
- `SCRIP_LCO_TRACE=2` shows `[LCO] ACTED count/1 frame-reuse redirect (B2 indexed)` — 19
  redirects for `count(20)`.
- Edge cases: `count(5)` → succeeds; `count(-1)` → fails correctly (base clause `count(0)`
  key INT(0) + wildcard clause 2 both match key INT(-1)? no — `-1 ≠ 0`, only clause 2 matches
  via N>0 which fails → correct fail). `count(0)` → ncand==2 (clause1 INT(0) + clause2
  wildcard) → normal scan + cut, NOT flattened — base case correctly excluded from B2.

## Gates (byte-identical to d9062238, ZERO regressions)

| Gate | Result |
|---|---|
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) |
| GATE-3 rung m2 | 104/107 |
| GATE-4 mode-4 minimal | 4/4 |
| GATE-SWI plunit | 57/57 (100%) |
| mode-4 corpus | 54/107 (unchanged — B2 is mode-2 only) |
| FACT grep | 0 |
| sibling icon/raku smoke | 5/5 / 5/5 |
| sibling snobol4 smoke | 13/13 |

GATE-SWI 57/57 is the key regression sentinel: the WAM-CP-8 first cut had regressed memberchk
57→56 by committing deterministically and stranding a recursive backtrack. B2 preserves it —
the cp-free-except-tail gate only fires when the body genuinely has no live alternative other
than its own tail call, and `count(0)`-style base cases (ncand>1 via wildcard) take the
unchanged CP-pushing scan.

## NEXT

**Heap, not stack, is now the ceiling for accumulators.** `sumto(10000000,…)` is `Killed`
(OOM): each iteration GC-allocates fresh Term cells (Acc1, N1) reachable through the trail
until the top call returns, so the trail + live-term set grows O(N) even though the C stack is
flat. This is the LATER tagged-word / global-stack track (SWIPL idea #1) explicitly scoped out
of WAM-CP — the trail should be truncatable once a deterministic frame is abandoned. Candidate
follow-ups:

1. **WAM-CP-6 Phase B3 — trail reclamation on deterministic redirect.** When B2 redirects (the
   caller frame is provably dead), the trail entries recorded by the abandoned frame's arg
   unifications are also dead unless aliased into the surviving env. Investigate truncating the
   trail to the pre-call mark after copying live bindings forward (the SWIPL `copyFrameArguments`
   analogue we deferred — needed now that the C stack no longer bounds depth).
2. **WAM-CP-13 mode-4 corpus** (54→~60/107) — mechanical per-builtin emit, independent of CP work.
3. **WAM-CP-7 unify specialization** — speed, any time.

Mechanism trace env vars (default OFF): `SCRIP_LCO_TRACE=2` (B2 redirect ACTED lines),
`SCRIP_IDX_TRACE=1` (CP-ELIDED lines), `SCRIP_LCO_TRACE=1` (eligibility audit).
