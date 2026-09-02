# FINDING — `forall/2` (rung57): the original wrong-answer defect looks fixed; a NEW frame-safety crash now blocks the same witness

**seat10 · 2026-09-01 · FLEET-16 · row `prolog-forall-wrong-answer-rung57` · SCRIP HEAD `2a140b90`**

## Context

Row `prolog-forall-wrong-answer-rung57` (minted hq_C 2026-08-29 at SCRIP `fef0c2fd`, from
`FINDING-2026-08-29-seat02-prolog-forall-wrong-answer-not-pz4.md`) describes a deterministic wrong-answer
defect: `forall(member(Y,[2,3,4]), Y mod 2 =:= 0)` should fail (`Y=3` breaks it) but wrongly succeeded —
rc=0, no crash, explicitly verified NOT PZ-4 at that HEAD.

The row's DONE-WHEN also names a now-stale path, `corpus/tests/prolog/rung57_forall/rung57.pl`. That
directory is gone — `tests-consolidate-prolog` swept it into the master suite weeks ago
(`ALL.excluded.txt:104`, `PENDING.md:24`, both confirmed after `git pull --rebase` brought corpus current).
The live witness is `ALL.pl`/`ALL.ref` entry 332, `forall_ite_directive_1` (`ALL.csv:333`, origin
`rung57_forall_rung57`) — same three-line source, byte-identical. Re-tested from there.

## What actually happens now (re-measured fresh, not inherited)

Isolated by ablation (RULES.md ASM-DIFF-FIRST step 1 — smallest repro first):

| witness | HEAD `2a140b90`, both modes |
|---|---|
| `forall(member(Y,[2,3,4]), Y mod 2 =:= 0)` alone — the originally-reported case, Cond **fails** partway | **correct** — `not_all2`, rc=0 |
| `forall(member(_,[]), fail)` alone — vacuous case | correct — `vacuous_true`, rc=0 |
| `forall(member(X,[2,4,6]), X mod 2 =:= 0)` alone — Cond **succeeds** for every element | **`*** stack smashing detected ***`, SIGABRT, rc=134** |
| full entry 332 (all three lines, as graded) | same SIGABRT — crashes before any output reaches stdout |

**The originally-reported wrong-answer symptom is gone** — seat02's exact case now gives the right answer.
What blocks entry 332 today is a different defect: `forall` crashes when its generator must backtrack to
*exhaustion* (every choice point explored, none breaking the inner negation), the mirror image of the
original bug's trigger. Not the same defect persisting — a different one now sits in its place.

## Root cause: a backtracking/frame-safety defect, not anything specific to `forall`

`forall/2` has no bespoke implementation — pure sugar, `lower_prolog.c:413-415`: `forall(Cond, Action)` →
`\+ (Cond, \+ Action)`, and `\+` (`lower_prolog.c:405`) is itself `(Goal -> fail ; true)`. Entry 332 line 1
therefore lowers to a `member/2` backtracking enumeration wrapped in nested negation-as-failure — exactly
the trigger shape seat02's own original FINDING already named for PZ-4: *"`\+`-guarded backtrack,
if-then-else inside a fail-driven `member/2` enumeration."*

gdb on the minimal repro lands in the neighborhood `MASTER-PLAN.md`'s own 2026-09-01 routing note already
flags by name:
```
#7  __stack_chk_fail ()
#8  dop_call_nothrow (by_name_dispatch.c:1516)
#9  rt_pl_dop_unwind_nothrow (by_name_dispatch.c:1590)
```
reached through the `g_plw_floor_bypass` path (`by_name_dispatch.c:1486-1516`) — the same path
`MASTER-PLAN.md` already flags: *"nothing now asserts a bypassed entry is SAFE."* That routing note is what
minted `prolog-plw-floor-bypass-safety-unproven` (QUEUE.tsv rank 1, **currently unassigned/FREE**, hq_P's
lane per MASTER-PLAN.md's ruling). The same crash shape also sits inside the broader, still-open keystone
`prolog-pz4-gamma-retain-activation-frames` (QUEUE.tsv rank 0, hq_C, itself
`BLOCKED-ON:calling-convention-depth-tracked`) — four other rows are already parked behind that keystone for
the identical shape (backtracking generator under negation/if-then-else): `prolog-multiclause-uninit-
lexprep-frame`, `prolog-sendmore-cryptarithm-segv`, `prolog-between-generator-backtrack-crash`,
`tests-consolidate-prolog-pz4-blocked-33`.

Did not attempt a fix here: not forall-specific (the desugar is shared control flow, so a bolt-on patch
would violate the shared-helper rule — branch on behavior, never on one caller's construct), and not a
leaf-rung-sized change — it needs the generator/negation machinery to be memory-safe under full
backtracking, which is exactly what the two rows above exist to land.

## Disposition

Same treatment as this row's own sibling `rung56_ite_backtrack` (confirmed genuine PZ-4, left loose, not
KEEP.md'd) and the four rows above: parking `prolog-forall-wrong-answer-rung57`
`BLOCKED-ON:prolog-pz4-gamma-retain-activation-frames`. Not closed, not KEEP.md'd — a bug, not a design
choice — DONE-WHEN reruns clean the moment that keystone (or `prolog-plw-floor-bypass-safety-unproven`, if
hq_P lands that first) lands. Baton updated with the corrected witness path and a fresh NEXT.

**General point** (same shape [[FINDING-2026-09-01-seat06-inherited-per-witness-dispositions-go-stale-and-only-a-re-test-tells-blocked-from-fixed]]
already named this session, opposite direction): a written disposition is a measurement with a timestamp,
not a standing fact, in either direction. This row's own GOAL text — *"NOT PZ-4 ... rc=0, no crash"* — was
accurate on 2026-08-29 and is not accurate today. Re-test before inheriting, even your own row's header.
