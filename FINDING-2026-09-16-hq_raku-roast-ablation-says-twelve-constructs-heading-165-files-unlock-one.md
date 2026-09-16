# FINDING 2026-09-16 hq_raku — roast ablation: the top TWELVE constructs head 165 files and unlock ONE

**Instrument:** `SCRIP/scripts/util_raku_roast_ablation_ranker.sh` (landed `56f09596d`). Writes nothing.
**Tree:** SCRIP `56f09596d`, roast `/home/resources/roast-master` (unversioned), RT_OPT `-O0`, measurer hq_raku.

## The measurement

```
ROAST_ABLATION_RANK census=1464 parse_dark=1371 graded=19 candidates=12
    moved=1  past_parse=0  advanced=16  same=1  headed=18   subtest 'STR' => {
    moved=0  past_parse=2  advanced=55  same=2  headed=59   use lib $*PROGRAM.parent(N).add: 'STR';
    moved=0  past_parse=0  advanced=9   same=0  headed=9    BEGIN %*ENV<RAKU_TEST_DIE_ON_FAIL> = True;
    ... nine more, every one moved=0 ...
ROAST_ABLATION_TOTAL candidates=12 files_headed=165 files_moved_to_graded=1
```

**Roast is a broad flat parser gap.** Twelve constructs, 165 files headed, ONE file unlocked. Any plan
promising a large roast jump from a handful of cures should be disbelieved unless an ablation backs it.

## Why this is not the histogram again

`--inventory`'s `ROAST_TOP_BLOCKING_CONSTRUCTS` ranks what each file hits FIRST, which is not what BLOCKS
it. hq_T proved that by hand on 2026-09-14 and the caveat has been printed on every run since. This
instrument generalises the proof: it removes the construct, re-runs, and counts files that actually MOVED.

The corroboration is the part worth trusting: the `use lib $*PROGRAM` row reproduces hq_T's hand measurement
**to the file** — headed=59, advanced=55, same=2, moved=0, i.e. "57 of 59 still parse-fail, zero graded" —
on a run nobody tuned it against.

The four outcome columns are four different facts, and collapsing them is how frequency gets mistaken for
progress: **moved** (a real unlock) · **past_parse** (left the parse bucket, still not graded) · **advanced**
(still parse-failing, at a NEW construct — the queue moving, which looks like progress and is not) · **same**
(the ablation did not take). Deletion is the ablation operator, so a file that breaks structurally counts as
"did not move": **every number here is a floor.**

## Two instrument defects found on the way, both of the same family

1. ⛔ **`SCRIP/refs/` was deleted org-wide on 2026-09-16 and both roast instruments hardcoded `$ROOT/refs/`.**
   `raku_roast_scoreboard.sh` refused rc=2 on an absent population — correctly, which is why it was cheap to
   find. But `test_gate_raku_paren_call_passes_its_arguments.sh` is **WIRED BLOCKING**, and it had been
   refusing rc=2 for all ten seats with its roast witness arm unreachable. A refusal inside the blocking set
   is exactly the class CEO-582's loop-and-report cure exists to make *visible* rather than to tolerate.
   Both now resolve per-root `refs/` first, then `/home/resources`, then an explicit override, refusing with
   every candidate named. ⛔ **Nine more scripts still path into `refs/`** (jcon, prolog, icon lanes — routed
   to the cto, not touched): `jcon_selfhost_build.sh`, `audit_prolog_iso_coverage.sh`,
   `audit_prolog_dialect_coverage.sh`, `audit_jcon_wholesale.sh`, `bench_icon_rate_3way.sh`,
   `util_raku_roast_error_histogram.sh`, `test_gate_rakugram_precedence.sh`, and two others.
   ⭐ **The general form: a deletion blinds every instrument that pathed into what was deleted, and the ones
   that refuse loudly are the lucky half.**

2. ⭐⭐ **A uniquely-named function is its own ratchet; a generically-named one cannot be counted globally.**
   The new gate's arm 4 pins the one-authority property the ablation measurement rests on — the ranker
   reports a DIFFERENCE between two classifications, so a private copy of the bucket rule would measure the
   copies as much as the cure, silently and in the flattering direction. That arm was **wrong on its first
   run**: it counted every file defining `classify()` tree-wide, found THREE, and all three were innocent
   (`board_demos_zeta.sh` classifies SNOBOL4 demos; `test_icn_d2_suspend_witness.sh` classifies Icon
   witnesses). It asked *who defines a function named classify* when the question was *who defines the roast
   bucket rule*. Now `roast_bucket()` — a name nothing else would pick — is counted tree-wide, and
   `classify()` is policed only in the two consumers that must not define it.

## Pre-existing, named so it is not inherited as anonymous debt

`test_gate_raku_zframe.sh` rc=1 (RK-ZC-8), reproduced on a clean stashed tree with this landing's edits
removed. Raku lane; wants a row.
