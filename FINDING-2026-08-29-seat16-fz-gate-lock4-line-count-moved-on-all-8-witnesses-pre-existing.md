# FINDING: test_gate_fz_release.sh LOCK 4 is RED on all 8 witnesses -- pre-existing, not caused by probe/fz conversion

Row: `corpus-crosscheck-probe-total-conversion` (clause 3). Discovered while converting `corpus/probe/fz`
to suite format and re-pointing the gate's `FZ` source (extraction via `corpus_suite_harness.py`, mirroring
`util_zsm_beta_skew_census.sh`'s ptc-grid idiom). NOT this row's to fix -- flagging for whoever owns FZ/depth-planner codegen.

## Measured, not inferred

Ran `test_gate_fz_release.sh` TWICE on the current tree: once against the original loose `corpus/probe/fz/*.sno`
(before touching anything), once against the re-pointed gate reading extracted-from-suite copies (after
conversion). **Full stdout is byte-identical between the two runs, same exit code (1).** This proves the
re-point is behavior-preserving and rules out the conversion as the cause of what follows.

LOCK 1 (disarmed vs .ref), LOCK 2 (no over-release), LOCK 3 (armed vs .ref), LOCK 5 (op_zpat road): all PASS/OK,
all 8 witnesses. **LOCK 4 (the cut is visible to the depth planner -- armed/disarmed `.s` line count must match)
fails on all 8 witnesses uniformly**, e.g.:

```
fz1_span_fence_span              LINE COUNT MOVED (367 vs 368) -- the arm changed more than the cut
fz2_cut_family                   LINE COUNT MOVED (1634 vs 1638)
fz3_capture_across_fence         LINE COUNT MOVED (1505 vs 1510)
...
```

Every witness moved by a small, non-zero, non-uniform delta (1 to 4 lines) -- not the "vacuous, bills 0" exit,
and not the "arm moved a line that is neither the cut nor a staged offset" single-witness shape LOCK 4's own
code distinguishes. A uniform-direction shift across every witness in the family, independent of which fence
pattern each exercises, smells like a shared codegen/runtime path gaining or losing a small fixed number of
emitted lines per box -- not a fence-specific regression, but that is a hypothesis, not a proof.

## What I did NOT do

I did not bisect or root-cause this -- FZ/depth-planner internals are outside this row's lane (corpus format
conversion), and I don't have the historical context LOCK 2/4's authors had when they wrote the tolerances.
Circumstantial-only: this tree was `git pull --rebase`d immediately before I measured (SCRIP `531cb8b7` ->
current), pulling in `77e8e423`/`9fb2445c`/`b85d2a2a`/`38a0119b`/`98b6e12c`/`06d4852f`/`f5c2fd83`/`9b39f6fd`
(icon N-2 generator-frame work + "zeta-choice-shape-eradication-phase2" collapsing dead `ZC_PORT_FORTH`
disjuncts in `zeta_storage.c`/`zeta_alloc.c`). ζ-storage is shared across all box families per ARCH's own
THREE-ZETAS section, so a shared-path change is plausible, but I have not confirmed LOCK 4 was green
immediately before these commits landed -- I'm reporting what I measured on the tree as of this sitting, not
a bisection result.

## Why this is worth a FINDING rather than silence

`test_gate_fz_release.sh` is not in `make test`'s four-script mandatory sequence, so this red is not currently
blocking anything -- but LOCK 4 is the tripwire for exactly the class of defect this file's own history (FZ-1,
FZ-3) says is easy to miss and expensive to find later. Left undocumented, the next seat to touch `probe/fz`
or this gate would have no way to know the red predates them.

Evidence: `test_gate_fz_release.sh` run output (both pre- and post-repoint, byte-identical), captured this
sitting. SCRIP tree at time of measurement: post-pull, pre-existing-red confirmed on both the loose-file and
suite-extracted sources.
