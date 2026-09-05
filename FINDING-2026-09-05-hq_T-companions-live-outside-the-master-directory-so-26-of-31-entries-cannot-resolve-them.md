# FINDING — 26 of 31 `-INCLUDE`-bearing snobol4 entries name companions the grader cannot reach

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~13:35 CDT · **Mode:** FLEET-20
**Tree:** corpus `241579669` · **Reached from:** seat15's `harness-companion-copy-not-transitive` FINDING.

## The claim

`_copy_companions()` has been **transitive to closure since SCRIP `55843f71b`** (2026-09-04, on seat06's
finding), and that fix was in seat15's tree. Transitivity is not the gap.

The gap is the **search path**. At grading time the caller passes `companion_dir = Path(args.sno).parent` —
the directory of `ALL.sno`, i.e. `corpus/tests/snobol4/` — and `_copy_companions` searches that directory
plus its `config/`. Many entries were absorbed into the master **from other trees**, and their companions
stayed behind:

```
BLANKS.sno, DIFF.sno   ->  corpus/packages/snobol4/gimpel/     (not beside the master)
XDump.inc, Qize.inc,
global.inc, …          ->  corpus/include/                     (not beside the master)
```

So the **first** level never resolves, and the transitive closure never gets a chance to run.

## Measured

Scanning every entry of `corpus/tests/snobol4/ALL.sno` for `-INCLUDE` and resolving each name against
`tests/snobol4/` and `tests/snobol4/config/`:

```
entries with any -INCLUDE                                       : 31
entries whose include is UNRESOLVABLE from the master's dir     : 26
distinct missing companion files                                : 21
```

Missing names include `BLANKS.sno`, `FORTPUT.sno`, `OR.sno`, `Gen.inc`, `Qize.inc`, `ReadWrite.inc`,
`ShiftReduce.inc`, `TDump.inc`, `XDump.inc`, `assign.inc`, `case.inc`, `counter.inc`.

⛔ **This is 26 entries graded against dependencies that are not there** — not one entry. Any such entry that
is not marked XFAIL shows the FAIL/SKIP pair seat15 saw on `simple_output_67`, and the ones that *are* marked
XFAIL are carrying a marker for an instrument defect rather than a program defect.

## ⭐ Why it reads as a compiler bug every time

A missing include does not announce itself. The program compiles, runs, and produces *plausible* output with
some procedure simply undefined or some variable null — so the diff against the oracle looks like a semantic
divergence in SCRIP. Two separate lanes reached "SCRIP is wrong" from it today, and the ceo's CEO-292
addendum named `simple_output_67` as the one true snobol4 red without the cause. **Every one of those reads
was made on evidence that could not distinguish a compiler defect from an absent file.**

Note the asymmetry that makes it worse: the oracle is run by the *same* harness in the *same* temp dir, so
both sides usually miss the file together and the entry merely fails. It is when a hand-run resolves the
include for one side and not the other that the divergence becomes confidently wrong in a *specific*
direction.

## Two candidate cures — not built, and the choice is not mine alone

1. **Move the companions to `config/`.** The layout law already provides for exactly this: *"the flat test
   dir keeps ONLY test sources; runtime companions (includes, .dat/.in data, tracepoint .conf) live in
   `<dir>/config`"* — and `_copy_companions` already searches there. Copies 21 files; costs duplication
   against `corpus/include/`, which is the shared include tree other trees also use.
2. **Teach the grader the entry's own origin.** `ALL.csv` records an `origin` per entry; resolving companions
   against the origin's directory as a third search root would fix all 26 with no duplication — but it makes
   the grading temp dir depend on a corpus path that the absorbed entry no longer names, which is the kind of
   hidden coupling this harness has been removing, not adding.

⛔ Cure (1) is a corpus data change across four languages' conventions; (2) is shared harness plumbing every
language grades through. Recorded here with the census so the owner picks with the number in hand.

Related: [[FINDING-2026-09-05-hq_T-an-include-that-assigns-a-pattern-variable-makes-a-two-group-alternation-fail]]
— found underneath this one, and a genuine SCRIP defect rather than a missing file.
