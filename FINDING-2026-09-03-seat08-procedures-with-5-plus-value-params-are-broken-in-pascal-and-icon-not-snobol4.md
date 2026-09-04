# FINDING — a user procedure/function taking 5+ VALUE parameters is broken in at least Pascal and Icon (NOT SNOBOL4) — the "det" fast-path caps at 4 args and whatever the >4 fallback does is wrong for at least these two

**Date:** 2026-09-03 ~21:00-21:20 CDT · **Seat:** seat08 (FLEET-16, hq_P lane) · found while working
`pascal-fpc-class-runtime-102-numeric-expected`, NOT filed as a class of that row -- this is bigger.

## Headline

A plain user-defined procedure/function with **5 or more value parameters** does not receive its
arguments correctly, in at least two languages. This is very likely the true root cause behind (some of)
the three witnesses in `pascal-fpc-class-runtime-102-numeric-expected` — none of which actually share a
mechanism with each other by TYPE the way that row assumed; they may share this instead.

## Reproductions (all `./scrip --run`, SCRIP `b471cfc45`)

**Pascal**, 4 params (control) — correct:
```pascal
program min3;
procedure rep(a,b,c,d: single);
begin
    writeln(a, ' ', b, ' ', c, ' ', d);
    if (a<>1) or (b<>2) or (c<>3) or (d<>4) then halt(1);
end;
begin
    rep(1,2,3,4);
    writeln('ok');
end.
```
→ prints values (as plain ints, a SEPARATE and smaller cosmetic bug — SINGLE-typed values are not being
formatted as reals; not this finding's subject) then `ok`, rc=0.

Pascal, **5 params**, otherwise identical shape (also reproduces with plain `integer` params, not just
`single` — type is not the ingredient):
```pascal
program minN;
procedure rep(p1,p2,p3,p4,p5: integer);
begin
    writeln(p1,' ',p2,' ',p3,' ',p4,' ',p5);
    if (p1<>1) or (p2<>2) or (p3<>3) or (p4<>4) or (p5<>5) then halt(1);
end;
begin
    rep(1,2,3,4,5);
    writeln('ok');
end.
```
→ `writeln` prints blank/whitespace (not `1 2 3 4 5`), then **`Run-time error 102 / numeric expected`**,
rc=1. The comparison against a parameter beyond the 4th hits a non-numeric (garbage/unset) descriptor.
This is the ORIGINAL fpc_tests witness's exact symptom (`webtbs_tw37393.pas`, 12 `single` params, identical
shape) reduced from 12 parameters down to 5 -- 4 works, 5 is the threshold, not a `single`-vs-`integer`
question.

**Icon**, 4 params (control) — correct:
```icon
procedure main()
  rep(1,2,3,4)
end
procedure rep(p1,p2,p3,p4)
  write(p1," ",p2," ",p3," ",p4)
end
```
→ `1 2 3 4`, rc=0.

Icon, **5 params**, otherwise identical:
```icon
procedure main()
  rep(1,2,3,4,5)
end
procedure rep(p1,p2,p3,p4,p5)
  write(p1," ",p2," ",p3," ",p4," ",p5)
end
```
→ **no output at all**, rc=0. Silently wrong (empty), not even a diagnostic — worse than Pascal's crash in
one sense (no signal at all that anything went wrong).

**SNOBOL4, NOT reproduced** — a `DEFINE`d function with 5 params works correctly:
```snobol4
	DEFINE('REP(P1,P2,P3,P4,P5)')	:(REP_END)
REP	OUTPUT = P1 ' ' P2 ' ' P3 ' ' P4 ' ' P5	:(RETURN)
REP_END
	REP(1,2,3,4,5)
END
```
→ `1 2 3 4 5`, rc=0. **So this is not universally shared across every lowerer's call path** — SNOBOL4's
`DEFINE`d-function call mechanism is either a different code path entirely or otherwise unaffected.
Prolog/Raku not tested this session (time-boxed); do not assume either direction for them.

## Mechanism (found, not fixed)

`src/templates/bb/bb_call_proc_staged.cpp` implements a "deterministic" (`det`) fast-path for procedure
calls, hardcoded to **at most 4 arguments**:
```c
void *rt_proc_call_open_det0(long idx);
void *rt_proc_call_open_det1(long idx, DESCR_t *a0);
void *rt_proc_call_open_det2(long idx, DESCR_t *a0, DESCR_t *a1);
void *rt_proc_call_open_det3(long idx, DESCR_t *a0, DESCR_t *a1, DESCR_t *a2);
void *rt_proc_call_open_det4(long idx, DESCR_t *a0, DESCR_t *a1, DESCR_t *a2, DESCR_t *a3);
...
static const char *detN_argreg[4] = { "rsi", "rdx", "rcx", "r8" };
int det_nA = (int)_.op_ival; int det_fuse = (det_idx >= 0 && det_nA >= 0 && det_nA <= 4);
```
(there are two near-identical copies of this shape in the file, one under a `_z` suffix for a different
arm — grep `detN_argreg` to find both). `det_fuse` gates whether the 4-register fast path is taken; for
`nA <= 4` it is, for `nA >= 5` control must fall through to a slower, generic path.

The GENERIC path exists and is NOT capacity-limited the same way: `g_call_args[CALL_ARGS_MAX]`
(`src/runtime/rt/rt.c:713`, `CALL_ARGS_MAX = 64`) is a 64-slot global argument-staging array, populated via
`rt_arg_stage(int idx, DESCR_t v)` and read back by the callee. So the *storage* is not the bottleneck —
64 slots is nowhere near exhausted at 5 arguments. The bug is somewhere in **how the >4 fallback path
populates or consumes `g_call_args[]`** (or in how the CALLEE side decides how many of its formal
parameters to read from there vs. from the 4 dedicated registers) for at least the Pascal and Icon lowering
paths. Not root-caused further this session — `bb_call_proc_staged.cpp` is 857 dense lines with many
named historical arms (MONITOR_BIN-conditional arms, an "N-2 SELFREC 5TH WORD" fix, a "role-4 TINY shim",
multiple `SCRIP_*` env-var killswitches), and its own comments describe several previous sessions' subtle,
hard-won fixes in this exact file — this is not a quick, safe edit for a walker to attempt cold.

## Why this wasn't caught already

Every corpus witness that exercises multi-parameter procedures/functions in the Pascal and Icon masters
apparently uses ≤4 parameters (the master boards are green modulo already-tracked classes; none of the
known reds match this shape) — a real, structural coverage gap: nothing in either master's construct
ladder currently walks parameter COUNT as its own axis past 4. Worth a ladder rung or smoke case once
someone owns the fix, so a regression here is caught mechanically rather than found by chance again.

## Disposition

Not fixed, not filed as a fresh class under `pascal-fpc-class-runtime-102-numeric-expected` (that row's
own three witnesses may partly resolve once this is cured, but this defect is bigger than that row and
touches Icon too — hq_B's lane, not just hq_P's). Routing to hq_P (this session's HQ) with a recommendation
to treat it like the division-by-zero finding: SHARED-NODE, cross-language, needs the owning HQ(s) — likely
hq_C or ceo-level triage given it touches both hq_P's (Pascal) and hq_B's (Icon) lanes — to decide
ownership before anyone edits `bb_call_proc_staged.cpp`.
