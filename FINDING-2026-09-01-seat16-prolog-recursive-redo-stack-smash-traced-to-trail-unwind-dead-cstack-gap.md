# FINDING 2026-09-01 (seat16) — `member/2`'s redo stack-smash is a dead-C-stack detection gap in `pl_trail_unwind`, triggered specifically by RECURSION/CYCLES, not by backtracking in general

Row: `prolog-member-2-redo-smashes-stack-canary` (hq_P mint, FLEET-16, Prolog #1 priority). Tree: SCRIP `3c048661d`. RT_OPT `-O0`. No source changed this session — root-caused only, per PZ-4/P1's own precedent for this subsystem (see below for why a scoped fix was not attempted).

## The repro, confirmed exactly as minted

```
:- initialization(main, main).
main :- member(Z,[1,2,3]), write(Z), nl, fail.
main :- true.
```
`./scrip --run f.pl` prints `1`, `2`, then `*** stack smashing detected ***: terminated`, rc=134. Reproduces identically in mode-4 (`--compile --target=x86` via `run_prolog_via_x86_backend.sh`).

## The discriminator: RECURSION/CYCLES, not backtracking, not list length, not the name "member"

Six minimal witnesses, all `./scrip --run`, `-O0`, this tree:

| witness | shape | result |
|---|---|---|
| `member(Z,[1,2])`, 1 redo | direct recursion, prelude `member/2` | **CRASH** rc=134 |
| `mem2(Z,[1,2,3])`, renamed clauses, not "member" | direct recursion | **CRASH** — rules out any `by_name_dispatch.c` name collision with the unrelated `{"member",2}` method-dispatch entry |
| `mem2(Z,[1,2])`, 1 redo, depth 1 | direct recursion, minimal | **CRASH** — the task's "second redo" framing is not the true threshold; ONE redo through ONE level of self-recursion already crashes |
| `mem2→mem3→mem2` mutual recursion, `[1,2]` | cyclic, not self-recursive | **CRASH** — rules out "self-call" as the necessary condition; a cycle of any length triggers it |
| `q(a). q(X):-r(X). r(b).` — one level of an ordinary (acyclic) predicate call, redone | non-recursive nesting | **PASS** |
| `p(1).p(2).p(3).` flat fact base, 2 redos (seat06's control) | zero nesting | **PASS** (re-verified) |
| bare `(Z=a;Z=b)` disjunction, redone | no predicate call at all | **PASS** |

**The necessary and sufficient condition, empirically: the predicate (or predicate cycle) being redone must call itself, directly or through intermediates, at increasing stack depth.** Acyclic nesting of any depth is fine; a bare choice point is fine; only recursion breaks.

## gdb localization

```
#7  __stack_chk_fail () at ./debug/stack_chk_fail.c:24
#8  dop_call_nothrow (body=dop_unwind_nothrow, args=..., nargs=1) at src/runtime/by_name_dispatch.c:1499
#9  rt_pl_dop_unwind_nothrow (...) at src/runtime/by_name_dispatch.c:1573
```
`dop_call_nothrow` has no local array of its own — the canary it loses belongs to **its own frame**, meaning the corrupting write lands there from a callee that has no canary of its own to trip first. Its `body` is `dop_unwind_nothrow` (`by_name_dispatch.c:1392`), which does exactly one thing relevant here:
```c
pl_trail_unwind(&g_pl_trail, (int)args[0].i);
```

## The mechanism (`src/parsers/prolog/pl_cell.h`)

`pl_trail_unwind` (line 77) pops trail entries back to `mark`, writing each entry's saved old value back into its cell **unless** the entry's address is judged to belong to now-dead C-stack memory:
```c
while (t->top > mark) {
    t->top--;
    if (!plc_dead_cstack(ents[t->top].addr)) *ents[t->top].addr = ents[t->top].old;
}
```
`plc_dead_cstack` (line 64) answers that question with **one global**, `g_plw_unwind_floor` — set in `by_name_dispatch.c`'s `dop_call`/`dop_call_nothrow` to `__builtin_frame_address(0)` at entry and saved/restored around each nested call:
```c
return (char *)p < g_plw_unwind_floor + 16;
```
This correctly nests for **acyclic** call chains (witness `q`/`r` above): each `dop_call*` invocation gets its own floor, saved and restored like a stack, and an address below the *current* floor is reliably dead. **It has never been asked to distinguish two different C-stack depths of the *same* predicate's activation from each other** — a single scalar floor cannot tell "this trail entry belongs to the outer, still-live `mem2` activation" from "this trail entry belongs to the inner, already-collapsed-on-redo `mem2` activation," because both activations are the same predicate at two different points on the one stack, and the floor only records *the current* boundary, not *which activation* owns a given address below it. On the acyclic witness there is only ever one activation of any given predicate alive at a time, so the single floor never has to make that distinction — which is exactly why it has looked correct for as long as the corpus has been mostly non-recursive multi-clause predicates and why this is surfacing only now, under FLEET-16's Prolog-#1 push into recursion-heavy programs (`queens.pl`, `sentences.pl` — see below).

## This is inside P1's live blast radius, not a free-standing bug

`pl_trail_unwind`'s own `mark < 0` tripwire (the `SCRIP FATAL: ... TRIPWIRE, not a cure` refusal) is hq_C's **RULING 2** landing from `calling-convention-depth-tracked` (P1, SCRIP `48d320de`) — P1 is *already*, *today*, mid-flight on this exact function, this exact file, this exact "trail entry crosses a call boundary with nothing tracking which activation owns it" problem class (P1's task file: *"the mark crosses a call/return boundary in a fixed `[rsp+32]` slot with nothing tracking accumulated depth"*; `prolog-pz4-gamma-retain-activation-frames` (C21), parked `BLOCKED-ON:calling-convention-depth-tracked` by hq_B today, states the identical shape at the frame level: *"a Prolog caller's whole ζ is rsp-relative... there is no base to re-anchor off... host RBP promotion is the precondition."*) `g_plw_unwind_floor`/`plc_dead_cstack` is a **second, previously-undiscussed instance of the same missing property** — "which activation does this stack address belong to" — one level removed from the mark-transport problem P1 is already solving. My crash's mark itself is not negative or out of range; the address inside the trail entry is what goes stale, so P1's existing tripwire does not (and structurally cannot) catch it.

**I did not attempt a fix.** `dop_call`/`dop_call_nothrow`/`g_plw_unwind_floor` (`by_name_dispatch.c`) and `pl_trail_unwind`/`plc_dead_cstack` (`pl_cell.h`) are the literal files P1's own rulings are actively landing changes against this session (P1's task file cites `unification.c`'s trail-unwind work as "live" as of this reading). A scoped patch here risks exactly the collision RULES.md's SEAMS discipline exists to prevent, and PZ-4's own ledger already records three independent sessions converging on adjacent parts of this same wall before it was correctly parked rather than re-fought. This finding is offered as a witness for whichever of P1/PZ-4 lands next, not as a request to re-open either.

## Likely connection to the queens/sentences SEGVs (unconfirmed, worth checking)

`prolog-queens-and-sentences-segv-are-more-rt-jmp-frame-lexprep2-witnesses` (C14) reports `rt_jmp_frame_lexprep2` call counts of 9 and 10 in the crashing programs' emitted `.s`, both deeply recursive (N-queens backtracking search; a recursive sentence parser). `rt_jmp_frame_lexprep2` is a *different* function from the one this finding localizes (it's the SUSPEND-frame prologue, not the trail-unwind consumer), but both are reached only by multi-clause predicates and both are symptoms the master plan already attributes to the retained-activation-frame gap. I have not run those two programs under gdb to check whether they land in the same `plc_dead_cstack` path or a genuinely different one — flagging as a plausible shared root rather than claiming it.

## What the taker after P1/PZ-4 needs

The task's DONE-WHEN is now a real, currently-red, executable check (see task file) covering: mode-3 and mode-4 both produce `1`/`2`/`3` for the minted repro, `findall(Z,member(Z,[1,2,3]),L)` yields `L=[1,2,3]`, and the flat fact-base control still passes. Oracle agreement (`swipl_bin`/`gprolog_bin`) and the SNOBOL4 floor + four smokes are named in a DONE-WHEN-NOTE rather than embedded, per this repo's own guidance that a DONE-WHEN command should not be so complex it fails for reasons unrelated to the defect. The six-witness table above is the fastest re-orientation for whoever picks this back up — it already answers "is this the same wall as PZ-4" (yes, by mechanism, though a different concrete global) without needing to re-derive it.
