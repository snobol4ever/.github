# FINDING-2026-08-09 — CLIMB N21: ARBNO-LON Frameless arm missing right-spine RSP compensation

## Session: s31 (Sonnet 4.6)

## Probe
`'aabb' ? POS(0) ARBNO('a') $ OUTPUT ARBNO('b') $ OUTPUT RPOS(0)`
Expected: `=S` with captures `a / / aa / / b / bb`. Got: `=F` after ~3 seconds (CAS stack exhaustion loop).

## Root cause

`bb_match_arbno_frameless()` (the ARBNO-LON K0 arm) was missing the right-spine RSP
compensation that `bb_match_arbno_tail()` already has via `FPR_RSP` (N02-FIX, tagged in that arm).

When RPOS(0)'s argument is a `LIT_INTEGER` node (K=16), that node does `sub rsp, 16` at α.
When RPOS fails, `n10_match_arbno_β` fires → body element ('b', K=0) runs with RSP displaced
16 bytes below n10's cell frame. On body success → PAIR(2)/as is reached — but `[rsp+4]`
now reads 16 bytes into `LIT_INTEGER`'s frame (garbage). The stall check is bogus, the
yield-cursor write corrupts `LIT_INTEGER`'s frame, and the ARBNO loops forever retrying
from the same cursor until the CAS mark stack limit fires → `n6_match_begin_af` → `=F`.

The 3-second runtime (vs instant) is CAS mark stack growing then hitting the limit:
`n6_match_begin_af` fires only after `r12` exhausts its sentinel-scan budget.

## Diagnostics

Monitor bracket: DIVERGE at step 4, still on statement 3.
- spl: `LABEL stno=INT=4` (success goto `:(EN)`)
- scr: `LABEL stno=INT=5` (fail goto `:(NO)`)

Simplest reproducer confirming no-capture involved:
```
'aabb' ? POS(0) ARBNO('a') ARBNO('b') RPOS(0)   → oracle: =S, scrip: =F (CRASH class)
'aa'   ? POS(0) ARBNO('a') ARBNO('b') RPOS(0)   → oracle: =S, scrip: =F
'bb'   ? POS(0) ARBNO('a') ARBNO('b') RPOS(0)   → =S both (first ARBNO null → no displacement)
```

Passing sibling: `ARBNO('a') SPAN('b') RPOS(0)` — SPAN is K=0, no displacement.

## Fix

Two changes:

### 1. `src/emitter/emit.cpp`: new static helper `arbno_frameless_fpr_rsp(nd)`
Walks `nd->γ.node` (the ARBNO's own subsequent = first right-spine node), summing `zd_k()`
per node until hitting `IR_MATCH_END`, `IR_MATCH_BEGIN`, `IR_MATCH_ARBNO` (enclosing ARBNO
boundary), or NULL. Stops at `IR_MATCH_ARBNO` to avoid crossing into enclosing ARBNO territory
for nested patterns (X04/X06 validated this guard). Called from the frameless-arm staging
block and result stored in `g_emit.op_tail_fpr_rsp` (reset to 0 at top of each node's staging,
safe to reuse for the non-tail arm).

### 2. `src/templates/bb_match_arbno.cpp`: compensations in `bb_match_arbno_frameless()` and `bb_match_arbno_frameless_k()`
- `bb_match_arbno_frameless()`: `IF(FPR > 0, x86("add","rsp",(long)FPR))` inserted at
  PAIR(2)/as entry AND PAIR(3)/af entry. Restores RSP to the ARBNO cell base before
  reading `[rsp+0]/[rsp+4]`. The subsequent path (PAIR(1) → LIT_INTEGER → `sub rsp,16`)
  re-pushes naturally on next iteration.
- `bb_match_arbno_frameless_k()`: same law, offsets adjusted for `kkN()` body displacement
  (`RDD("rsp", kkN()+4+FPRK)` etc.).

Zero bytes change when right-spine is empty (N02 pattern: IF gate is dead, byte-identical).

## Validated
- N21 m3: `=S` with correct backtracking outputs `a / / aa / / b / bb`
- N21 m4: `=S`
- `'aa'` / `'aabb'` / `'bb'` no-capture variants: all correct
- Suite m3: 146 pass / 3 xfail / 0 XPASS / 1 REGRESSION (X08 pre-existing on HEAD)
- Suite m4: 145 pass / 4 xfail / 0 XPASS / 1 REGRESSION (X08 pre-existing on HEAD)
- D06 m4 XPASS confirmed: parallel MECH SLACK-RIDER RE-HOME landed this session
- X08 is a pre-existing crash on HEAD before this session (confirmed via `git stash` test)

## XFAIL retired
- `XFAIL.run`: N21
- `XFAIL.compile`: D06, N21

## Notes
- `bb_match_arbno_tail()` already had the N02-FIX; this fix applies the identical law to the
  two frameless arms that were missing it.
- The stop-at-`IR_MATCH_ARBNO` condition in the right-spine walk is essential for correctness
  with nested ARBNOs (X04: outer ARBNO's right-spine walk would otherwise enter the outer's
  territory via the inner ARBNO's `γ`-chain).
- C++ scoping constraint: variable declarations inside `case` body without explicit `{}` at
  the case level cause "jump to case label" errors. The static helper function pattern sidesteps
  this while keeping the fix in one place.
