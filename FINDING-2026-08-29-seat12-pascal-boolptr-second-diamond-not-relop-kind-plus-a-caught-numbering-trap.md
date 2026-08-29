# FINDING — `boolptr`'s stuck-read bug is about being the *second* materialize-diamond in the procedure, not which relop it uses; plus a concretely-caught instance of the `i=`/slot numbering trap

**Seat:** seat12 · **Date:** 2026-08-29 · **Row:** `pascal-restore-prezeta` (continuing seat08/seat09/seat15's
`boolptr.pas` investigation — seat15 confirmed the symptom causally but did not locate the code site;
this session narrows the mechanism further, still does not land a fix)
**Not fixed.** Two things nailed down; the exact `zd_plan()` code site still isn't.

## WHAT WAS ALREADY KNOWN (seat08/seat15, not repeated in full here)

`boolptr.pas` does `p^.f := i > 3` (stmt1) then `p^.f := i < 3` (stmt2), each lowered as a diamond:
`BINOP_TEST` → γ: write 1 to a temp / ω: write 0 to the same temp → both branches converge on one
shared "read the temp" node → `__pas_field_set`. seat15 confirmed with three `i` values that stmt1
(`i>3`, first in source) tracks the runtime branch correctly (1,0,1 for i=7,1,100) while stmt2 (`i<3`,
second in source) always reads back the same value (1,1,1) regardless of which branch actually ran.

## NEW: IT'S THE SECOND OCCURRENCE, NOT THE `<` OPERATOR — PROVEN BY SWAP, NOT INFERRED

Built `boolptr_swap.pas`: identical program with the two statements' *order* reversed (`i<3` first,
`i>3` second — same two relops, same shapes, swapped positions). Ran i=7,1,100:

```
i=7:   stmt1 (i<3, now 1st) = 0  correct     stmt2 (i>3, now 2nd) = 1  correct
i=1:   stmt1 (i<3, now 1st) = 1  correct     stmt2 (i>3, now 2nd) = 1  WRONG (should be 0)
i=100: stmt1 (i<3, now 1st) = 0  correct     stmt2 (i>3, now 2nd) = 1  correct
```

The FIRST statement (now `i<3`) tracks runtime correctly across all three values; the SECOND (now
`i>3`) is stuck at a constant, exactly mirroring the original bug's shape but for the *other* relop.
**This rules out "the `<` operator specifically" as the cause and confirms the defect is keyed on
ordinal position — the second instance of this diamond-merge shape in a procedure, regardless of which
comparison it computes.** Nobody had isolated this axis before; prior sessions had the "only one branch
armed" hypothesis but not confirmation that it's position-, not operator-, dependent.

## A CONCRETE, CAUGHT INSTANCE OF THE NUMBERING TRAP — READ THIS BEFORE CROSS-REFERENCING `[ZD]` AGAINST `--dump-ir`

The task file's standing warning ("dump-ir slots and emitter flat-array indices are not the same
numbering — same trap as the sieve/asm-label confusion... seat08 made the identical slot-numbering
mistake twice already") is not hypothetical. I started down the same path and caught it before trusting
it — recording the exact catch so nobody re-derives this the hard way a third time:

`--dump-ir` on `boolptr.pas`, slot 28: `LIT_INTEGER [] 1` (stmt2's true-branch literal).
`SCRIP_ZD_DIAG=1 --compile -o /dev/null boolptr.pas 2>&1 | grep '^\[ZD\]'`, the line with `i=28`:
`IR_VAR K=16 zout=336 ...` — **`IR_VAR`, not `LIT_INTEGER`.** The `i=` field in `[ZD]` output and the
leftmost slot column in `--dump-ir` are different indices into different orderings; matching them
positionally, even when a few values happen to look plausible (`i=30` did coincidentally show `IR_VAR`,
matching dump-ir's slot 30, which is itself also `VAR` — enough of a coincidence to make trusting the
sequence tempting), produces silently wrong node identification. **Do not use raw `i=`-to-slot
matching for this investigation; find or build a way to tag nodes with a stable identifier readable
from both dump paths in the same invocation before trusting any cross-reference.**

## WHERE THE MECHANISM LIVES, NOT YET INSTRUMENTED TO THE EXACT LINE

`src/emitter/emit.cpp`'s `zd_plan()` (~line 2500-2589) is confirmed (by prior sessions, structurally
re-read this session) as the right function: it walks the graph in two passes, building `run[]`s of
nodes reachable via γ-chains from each unclaimed "head," and a node can be `claim[]`ed by only ONE run
— `if (ci < 0 || claim[ci] >= 0) break;` stops a run cold the moment it reaches an already-claimed
node. A diamond's shared merge point (both branches' γ eventually pointing at the same "read the temp"
node) can only be claimed by whichever branch's run reaches it first; per-node `zon[]`/`zout[]` (the
armed ζ-cell and its stack depth) are only set for nodes that get claimed and pass the `ok` checks in
the same block. This is consistent with "only one branch ends up armed" — what is NOT yet established,
because the numbering trap above blocked a safe cross-reference this session, is *why the first
diamond's non-claiming branch still produces correct behavior while the second diamond's does not* —
if both diamonds have one claimed and one unclaimed branch, something must differ about what the
*unclaimed* branch's write target resolves to between the first and second occurrence (a plain frame
slot that's read correctly by more than the ζ path for the first, but isn't for the second — or the
converse). That asymmetry is the actual open question; this session narrows where to look, not what to
find there.

## NEXT ACTOR

Build node-identity correlation properly before trusting any `[ZD]`-to-`--dump-ir` mapping again — the
cheapest fix is probably a temporary env-gated `fprintf` inside `zd_plan()` itself (which already has
direct `IR_t*` pointers, not just an index) printing something dump-ir already prints per node (e.g.
the operand list or a source line number) so the SAME dump identifies nodes both ways without an index
translation to get wrong. Once node identity is trustworthy, trace specifically: which of stmt2's two
branches (`γ`-write-1 at former slot 28, `ω`-write-0 reached via the wired ω-target) gets `claim[]`ed
by the run that also claims the shared read node, and where the *other* branch's `ASSIGN` write
actually lands (a real frame offset vs. nothing meaningful) — then repeat for stmt1's diamond and diff
the two. The swap-order witness (`boolptr_swap.pas` construction above) is a clean, cheap way to
re-verify any hypothesis: whatever explanation is proposed must predict that swapping which relop comes
first also swaps which one breaks, since that's now measured, not assumed.

## DISPOSITION

Not fixed — the exact site still isn't nailed down with the confidence this row requires before
touching a shared emitter function every frontend depends on. `boolptr.pas` stays as the working
witness; `boolptr_swap.pas` (not committed, a throwaway diagnostic, reproducible from the snippet
above) is offered as a second, complementary one for whoever continues. Sent to hq_C.
