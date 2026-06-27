# HANDOFF — 2026-05-29 Opus 4.7 — Prolog BB prophylactic UNCOLLECTABLE swap

**Step closed:** prophylactic `GC_MALLOC → GC_MALLOC_UNCOLLECTABLE` at the four remaining
`lower_pl.c` state-struct sites flagged in HANDOFF-2026-05-29-OPUS-PROLOG-BB-GC-UNCOLLECTABLE.md.

**SCRIP commit:** `5bf88205` (parent `98c2f974`).
**.github commit:** this commit.

## What landed
7 swaps in `src/lower/lower_pl.c`, mechanical surgery on the same hazard pattern fixed at
the call/choice sites in the predecessor session:

| Line | Allocation | Site |
|------|------------|------|
| 77   | `bb_pl_ite_state_t *zi`         | `lower_pl_new_Ite` (if-then-else) |
| 148  | `bb_pl_seq_state_t *zs`         | `lower_pl_new_Conj` (goal conjunction) |
| 150  | `zs->goals = BB_t **`           | (sub-array of 148) |
| 527  | `bb_pl_catch_state_t *zc`       | `lower_pl_goal` catch/3 builtin |
| 553  | `bb_pl_findall_state_t *fs`     | `lower_pl_goal` findall/3 builtin |
| 648  | `bb_pl_seq_state_t *zs`         | `lower_pl_clause_body` (top-level seq wrapper) |
| 650  | `zs->goals = BB_t **`           | (sub-array of 648) |

## Hazard pattern (refresher)
- `BB_t` is libc-`calloc`'d in `scrip_ir.c:32,43` (NOT GC-aware).
- The state structs are `GC_MALLOC`'d and reachable from C **only** through `bb->ival`,
  which is `int64_t` — libgc sees an integer, not a pointer.
- libgc only scans its own heap regions for roots. Anything reachable solely through libc
  memory is *unreachable from libgc's perspective* and gets swept under collection.
- Under deep recursion that triggers a GC cycle, libgc reclaims the sidecar's backing
  pages and reuses them for new `Term` allocations. A later `(bb_pl_*_state_t *)bb->ival`
  read returns garbage. Past corruption signature: `zc->args[0]=0x3, [1]=0x61` —
  `Term{tag=TERM_INT, ival='a'}` aliased over the freed sidecar.

## Why these four were latent
The pj_rev deep-recursion path that triggered the original `string_chars` SIGSEGV does NOT
traverse ite / catch / findall / seq-clause-body. So they were safe in practice — but the
mechanism is identical and any of the following would have surfaced the same bug:
- a recursive predicate using `if-then-else` (very common pattern)
- a recursive predicate inside `catch/3`
- `findall/3` of a recursive goal
- any predicate body of multiple goals at depth (the clause-body seq wrapper)

## Why GC_MALLOC_UNCOLLECTABLE specifically
- Marks the allocation as permanently-rooted (libgc never sweeps it).
- Keeps it GC-aware for **tracing into** — `BB_t *` pointers stored in `zs->goals[]` etc.
  are still followed by libgc when scanning the sidecar.
- Equivalent to a permanent leak that libgc tolerates without complaining. Acceptable
  because BB graphs live for the program's lifetime in mode 2/3; mode-4
  `stage2_free_bb_after_emit` walks the graph explicitly.

## What was NOT swapped and why
Lines 126/127/128 — the `gα`/`gβ`/`gnodes` working arrays in `lower_pl_new_Conj` — are
local pointers used only inside that function call. They are copied into the now-
UNCOLLECTABLE `zs->goals[]` at line 152, then unreachable from anything that survives
the function. No libc-malloc'd struct holds a reference to them. They could be
upgraded to `GC_MALLOC_UNCOLLECTABLE` for paranoid uniformity (or even `malloc`+`free`)
but they are not part of the hazard class. Left alone.

## Gates (all byte-identical to `98c2f974` baseline)
| Gate | Result | Notes |
|------|--------|-------|
| GATE-1 (smoke prolog) | 5/5 | |
| GATE-2 (3-mode crosscheck) | 132/0 | 5 ORACLE_MISS (frontend gap, unchanged) |
| GATE-3 mode-2 (`--run`) | 104/107 | |
| GATE-4 (mode-4 minimal) | 4/4 | |
| GATE-SWI mode-2 (`--run`) | 57/57 (100%) | |
| GATE-SWI mode-3 (`--run`) | 57/57 (100%) | |
| FACT RULE | 0 violations | |
| smoke icon | 5/5 | |
| smoke raku | 5/5 | |
| smoke snobol4 | 13/13 | |

ZERO regressions.

## NEXT (3 long-arc options)
With both predecessor's reactive fix (`98c2f974`) and this prophylactic sweep landed,
the entire sidecar-via-`bb->ival` hazard class in `lower_pl.c` is closed. Remaining work:

**(a) WAM-CP-6 LCO proper (multi-session, highest-value).** Refactor `bb_exec_once` from
recursive C-stack tail-calls into an explicit trampoline / non-recursive loop. The
80 KB stack-redux from session `52f80293` was a stopgap. With UNCOLLECTABLE in place,
deep recursion no longer corrupts sidecars — but it still consumes C stack. LCO would
remove the stack ceiling entirely and unlock the `count/1` benchmark (1e6 iterations
in O(1) stack per GOAL ladder). Study target: `doc/SWIPL-STUDY-2026-05-28-OPUS.md`
CP-stack idea #4.

**(b) WAM-CP-13 — mode-4 corpus (long-arc).** Mode-3 BB walk transparent via
`sm_interp_run` is at 90/107; mode-4 native (`--compile --target=x86`) corpus is
the next horizon. Requires per-builtin mode-4 emit arms for everything the mode-2
ladder covers. Mechanical but broad: ~40-50 builtins.

**(c) PL-RT-ASSERTZ (dynamic clauses, smallest).** `assertz/1`/`asserta/1`/`retract/1`.
Wire into `pl_runtime.c` clause-table. Independent of CP work; would close several
SWI suite gaps once tests are added (currently the suite doesn't exercise dynamic
clauses since support was missing).

Recommend (a) — highest leverage, unblocks count/1 and the broader recursion-heavy
corpus. Use the SWIPL study as the architectural compass.

## Files touched
- `SCRIP/src/lower/lower_pl.c` (7 token changes)
- `.github/PLAN.md` (Prolog BB row updated)
- `.github/GOAL-PROLOG-BB.md` (State-at-HEAD block prepended; prior block demoted to Prior HEAD)
- `.github/HANDOFF-2026-05-29-OPUS-PROLOG-BB-UNCOLLECTABLE-PROPHYLACTIC.md` (this file)
