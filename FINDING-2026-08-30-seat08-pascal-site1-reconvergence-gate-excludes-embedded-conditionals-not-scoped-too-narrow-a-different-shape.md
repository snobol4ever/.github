# FINDING: Site 2's reconvergence gate isn't "scoped too narrow" for Site 1 — the swap/partition
# conditionals are a structurally DIFFERENT shape (embedded-in-a-continuous-run) than the value-diamond
# the gate was built to detect (omega-branch-as-orphaned-dead-end), and the gate correctly excludes them

**Who/when:** seat08, 2026-08-30, `pascal-m4-site1-forloop-backedge-64byte-excess` row. Answers this row's
own live NEXT ACTOR item 1 directly: "check `ff1df778`'s actual diff scope first — this may be fixable by the
identical mechanism if that fix was scoped narrower than 'every IR_BINOP_TEST'." It is not fixable that way;
full evidence below. Also does item 2 (re-verify `quick.pas` independently, node-level, not by analogy).

## Setup

Fresh pull, `make pristine` (SCRIP `a9defbae`), re-reproduced the crash first: `echo 1 | ./scrip --run
bubble.pas` → **rc=139 SIGSEGV in mode-3 too**, not just m4 (confirms `FINDING-2026-08-30-seat03-pascal-bubble-
m3-segv-bisected-to-site2-flat-release-became-zd-plan-managed.md`, which landed in the same pull as this
session's start).

## Part 1 — read `ff1df778` itself, not just its commit message

The fix (`src/emitter/emit.cpp`) admits `IR_BINOP_TEST` into `zd_omega_head`/`zd_omega_seed`/
`zd_omega_test_idx` **unconditionally** (any test op qualifies once `SCRIP_ZD_TESTFAM` is on, which is
default). The actual corrective pop computation, though, only fires through a second, separate gate:
```c
int vd_tidx = -1;
if (_zvd && pass == 1 && ok) {
    vd_tidx = zd_omega_test_idx(nodes, n, nodes[hi]);
    if (vd_tidx >= 0 && claim[vd_tidx] >= 0 && cur) {
        int _curi = ...; // index of `cur` in nodes[]
        if (!(_curi >= 0 && claim[_curi] == claim[vd_tidx])) vd_tidx = -1;
    } else vd_tidx = -1;
}
if (vd_tidx >= 0) zvd_ok[vd_tidx] = 1;   // ONLY nodes with zvd_ok[i] get the deferred-pop treatment
```
This only runs `pass == 1` — i.e., only for a run that gets (re-)claimed in a **second pass**, after pass 0's
claiming already completed. That is precisely the value-diamond shape the commit message describes: an
omega-branch that pass 0 leaves as an **unclaimed dead end**, later picked up as its own claim in pass 1.

## Part 2 — empirically, which nodes actually get the fix (measured, not inferred from the diff)

`SCRIP_ZD_DIAG=1` prints a `[ZD-FINAL]` line for every node where `zvd_ok[i]` is true — i.e., every node the
fix actually touches. On `bubble.pas` (7 total `IR_BINOP_TEST` nodes, via `SCRIP_ZD_MAP=1`):
```
[ZD-FINAL] i=53 IR_BINOP_TEST K=16 zout=672 gpop=0 wpop=-16 gback=54  oback=58
[ZD-FINAL] i=80 IR_BINOP_TEST K=16 zout=128 gpop=0 wpop=-16 gback=81  oback=114
```
**Only 2 of 7.** Both are genuine **loop tests** (`gback`/`oback` point at the loop body entry and the loop
exit target respectively — real reconvergence across a claim boundary). The other 5 `IR_BINOP_TEST` nodes,
**including i=89 — confirmed to be the sort's own swap conditional** (`sortlist[i]>sortlist[i+1]`, immediately
followed by node i=90, the swap body-entry node seat14's prior FINDING already pinned down) — get **no**
`[ZD-FINAL]` line at all: `zvd_ok[89]` never becomes true.

**Why, checked directly rather than assumed:** i=89's own claim is 71; its omega-chase target (node i=110) is
**also claim 71** — the SAME continuous run pass 0 already walked, not a separate pass-1 claim. `zd_omega_test_
idx` only matches when some OTHER run's head (`nodes[hi]`, evaluated during `pass == 1`) equals a test's omega
target — and no such separate pass-1 run exists here, because i=89's "diamond" was never split into two claims
in the first place. **This is the mechanical reason the gate excludes it, and it is not an oversight of scope:**
i=53/i=80 (loop tests) have an omega branch that pass 0 genuinely could not claim yet (the loop's own back-edge
has to close first) — a real orphan, picked up in pass 1. i=89's omega branch (skip-swap) rejoins the SAME
loop-body run that's already one continuous claim — there is no orphan for pass 1 to adopt.

## Part 3 — cross-checked independently on `quick.pas`, not by analogy (this row's own NEXT ACTOR item 2)

`quick.pas`'s current state, checked fresh (not assumed identical to bubble): **m3 (`--run`) is CLEAN** —
`echo 1 | ./scrip --run quick.pas` matches `quick.ref` exactly, no crash. **m4 (`--compile`) is WRONG-OUTPUT,
not a crash**: linked binary prints `10414` where `.ref` says `15505`, rc=0. This is a different failure shape
than `bubble.pas` (crashes both modes) — flagged, not explained; do not assume the same instruction sequence is
responsible without checking (this row's own repeatedly-learned lesson).

Same `SCRIP_ZD_DIAG`/`SCRIP_ZD_MAP` measurement, independently re-run on `quick.pas`: **20 total
`IR_BINOP_TEST` nodes, only 2 get `[ZD-FINAL]`** (`i=21`, `i=49` — again loop tests by their `gback`/`oback`
shape). The other 18, including whichever node is quicksort's own pivot-comparison/partition conditional (not
individually identified this pass — see NEXT ACTOR), get no reconvergence treatment. **The pattern replicates
exactly**: loop tests get the fix, embedded conditionals inside a loop body do not.

## What this settles and what it doesn't

**Settles:** widening Site 2's `SCRIP_ZD_TESTFAM`/`zd_omega_head` admission (already unconditional for
`IR_BINOP_TEST`) would do nothing — the actual gate is the `pass==1`-plus-claim-match reconvergence check, and
it correctly reports "not a reconverged diamond" for these nodes, because they genuinely aren't one. This is
not a bug in Site 2's scoping; it's the wrong tool for a different shape.

**Does NOT settle:** what the correct fix for the embedded-conditional shape actually is. The base (pass-0)
accounting for i=89's omega arm evidently still computes a release/pop that doesn't match physical reality
(the row's own gdb-measured 288-byte-per-skip drift stands, unexplained mechanically) — but that is a
different question from "does Site 2 apply here," and this pass did not trace the pass-0 K/REL computation for
this specific shape to find where the 288 bytes actually goes missing.

## Not attempted

No fix, no source touched (`git status --short` clean throughout). Per this row's own standing authorization
rule, the underlying repair is `zd_plan`'s shared accounting, reserved for hq_C — this FINDING narrows the
question (a genuinely different control-flow shape, not a scoping oversight) without answering it.

## Suggested next step, not decided here

1. Trace the pass-0 K/REL computation specifically for an embedded-conditional-inside-a-continuous-claim shape
   (i=89 on `bubble.pas`, or its `quick.pas` analog) the same rigor Site 2's own investigation applied to the
   value-diamond shape — this is genuinely new territory, not a re-derivation of Site 2's work.
2. Identify quicksort's specific embedded conditional (its partition/pivot compare) by name/line, the same way
   `n89`/`sortlist[i]>sortlist[i+1]` was pinned down for `bubble.pas` — not done this pass.
3. `quick.pas`'s m3-clean-but-m4-wrong asymmetry is itself unexplained and may be a separate, useful data
   point (a shape where the drift stays under whatever threshold m3's memory layout tolerates) — worth a
   dedicated look before assuming it's the identical mechanism at a smaller magnitude.
4. Still reserved for hq_C; not solo-fixable, same restraint as every prior session on this row.
