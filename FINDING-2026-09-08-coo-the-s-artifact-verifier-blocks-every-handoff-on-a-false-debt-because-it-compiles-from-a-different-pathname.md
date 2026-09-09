# FINDING 2026-09-08 (coo) — the `.s` artifact verifier blocks EVERY seat's handoff on a debt that does not exist, because it compiles from a different pathname

**Seat:** coo · **Trees:** SCRIP `5bf935dd5`, corpus `115670356` · **Measured:** 2026-09-08 20:2x CDT
**Lane:** instruments (hq_T). ⛔ REPORTED, NOT CURED — same call as the sibling finding filed
tonight: under MODE NONET a seat asks before editing across a lane.
**Impact: fleet-wide and immediate.** `.s` artifact drift has BLOCKED the handoff verdict since
2026-08-30, so this false debt blocks *every* seat's handoff, not only mine.

## The symptom: two instruments that disagree about the same 23 files

```
$ bash scripts/util_regen_prolog_bench_s_artifacts.sh "coo-29b"
regen[coo-29b]: emitted=23 changed=0 fenced=0 refused=0 rejected=0 timedout=0 errored=0
  No changes — prolog bench .s artifacts already current.

$ bash scripts/handoff_status.sh
  VERDICT: OWED — 23 item(s) need attention before this counts as current:
    - prolog_bench: 23 .s/.FENCED owed -> benchmarks/prolog/bench/cal.s ...
```

The generator that writes these artifacts says they are current. The verifier that grades them says
all 23 are owed. Both ran against the same tree, minutes apart, with the same binary.

## Which one is right, settled by direct measurement

```
$ scrip --compile /home/claude_coo/corpus/benchmarks/prolog/bench/cal.pl > cal_fresh.s
$ diff -q cal_fresh.s corpus/benchmarks/prolog/bench/cal.s
  (identical)
```

**The committed artifacts are current. The verifier is wrong.**

## The cause, and it is one line of emitted output

`util_verify_s_artifacts_owed.sh` clones the corpus to a disposable scratch dir and re-runs the
regen script there, detecting "owed" by whether that run produced a *commit* in the clone
(`pre != post`, line ~199-208). The emitted `.s` carries the **absolute source pathname** in its
`.file` directive, so an artifact built from the clone can never equal one built from the real tree:

```
$ diff corpus/benchmarks/prolog/bench/cal.s <(scrip --compile <clone>/benchmarks/prolog/bench/cal.pl)
3c3
<   .file  1 "/home/claude_coo/corpus/benchmarks/prolog/bench/cal.pl"
---
>   .file  1 "vclone/benchmarks/prolog/bench/cal.pl"
```

**Exactly two changed lines across the whole file, and both are that one directive.** Every one of
the 23 differs for this reason and no other, so the regen commits in the clone, and the verifier
reports 23 owed. It would report 23 owed on a perfectly current tree forever.

## Why only prolog_bench, when the same check passes for the other three

`benchmark`, `demo` and `icon_bench` all report `owed=0` through the same scratch-clone mechanism.
The difference is the spelling each generator hands the compiler: the prolog one passes the full
path (`$B/*.pl`, line 24), so the pathname reaches the `.file` directive and the artifact is
position-dependent. The others do not produce that difference. **This is the same class the coo
cured in `test_snoflake_suite.sh` hours earlier the same day** — an engine given two different
spellings of one source produces two outputs that can never be compared — and the same class the cto
cured in the Arizona runner (`3bb0a210c`). Third instance in one day, in three unrelated
instruments.

## What the debt actually was

Not all of tonight's 66 were false. Running the three regen scripts genuinely cured 43 of them
(benchmark 19, demo 4, icon_bench 20, plus a real first-pass prolog_bench regeneration that changed
197,819 lines). The **residual 23 are the false ones** and they will not clear by regenerating,
because regenerating is not what they are asking for.

## Suggested DONE-WHEN for whoever owns the row

Compile each artifact through a stable spelling so the output is position-independent — the
snoflake/Arizona cure applied here — or have the verifier compare with the `.file` directive
normalised out, and say in the script which it chose and why. The gate on it must prove the case
that actually failed: **a clone at a different path must verify CLEAN on a current tree.** A check
that only runs in place cannot see this, which is precisely how it survived since 2026-08-30.
