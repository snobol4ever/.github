# FINDING — the m4 Pascal spine leak is a BACK-EDGE JOIN-DEPTH MISMATCH, isolated to ONE node per
# kernel, with a per-node killswitch that makes `bubble` fully green. Confirms the join-depth
# hypothesis an earlier hq_P pass raised and could not test (its witness had stopped failing).

**hq_P · 2026-08-29 · row `pascal-m4-for-spine-leak-64b-per-iter`**

**Not cured — diagnosis only, nothing committed to SCRIP or corpus.** See §6 for why I stopped at the
cure boundary rather than editing `zd_plan`.

## 0. Answer

`zd_plan` gives a loop back-edge a **static** pop amount computed from the *plan's* depth for the jump
target. The target is reached from two predecessors **at two different runtime depths**, so the constant
is right for one path and wrong for the other. RSP therefore climbs by a fixed amount every iteration
until it leaves the stack — `SIGSEGV`, `rc=139`.

## 1. The measurement that settles it (gdb, `setarch -R`, `bubble`)

Break at the loop join `n23_var_α` and at the back-edge `n70_assign_α`:

```
n23  entry rsp=0x7ffffffedf90            <-- 1st entry, fall-through path
  n70 backedge rsp=0x7ffffffee040 (add 544 -> 0x7ffffffee260)
n23  entry rsp=0x7ffffffee260            <-- 2nd entry, back-edge path: NOT 0x...edf90
  n70 backedge rsp=0x7ffffffee310 (add 544 -> 0x7ffffffee530)
n23  entry rsp=0x7ffffffee530
  n70 backedge rsp=0x7ffffffee5e0 (add 544 -> 0x7ffffffee800)
n23  entry rsp=0x7ffffffee800
```

**The same join label is entered at a different RSP on each path.** Per iteration the loop body moves
RSP up `0xB0` (176) and the back-edge adds `544`, for a **monotonic +720 bytes/iteration**. It never
comes back down. The emitted back-edge is a bare constant:

```asm
n70_assign_α:   ...
                add   rsp, 544;   jmp   n23_var_α
```

⚠️ **The row's title says 64 bytes/iteration; I measured 720 on `bubble` at this HEAD.** I am not
retitling the row on one kernel, but the figure in the name should not be quoted as current without
re-measuring — the mechanism, not the constant, is the stable part.

## 2. Isolated to ONE node per kernel, with a working killswitch

`SCRIP_ZD_DIAG=1` prints the plan. In **every** kernel exactly one node carries a non-zero `gpop`, and
that node is the back-edge:

| kernel | zd nodes | the non-zero-`gpop` node | grid |
|---|---|---|---|
| bubble | 62 | `i=70 IR_ASSIGN K=0 zout=768 gpop=544 wpop=768` | FAIL 139 |
| quick | 58 | `i=66 IR_ASSIGN K=0 zout=736 gpop=544 wpop=736` | FAIL 139 |
| intmm | 60 | gpop=464 | PASS |
| queens / sieve / perm | 36 / 29 / 29 | gpop=160 | PASS |
| towers | 21 | gpop=192 | PASS |
| uplevel2 / uplevel3 | 1 | gpop=16 | PASS |

⛔ **So "non-zero `gpop`" is NOT itself the defect** — all seven passing kernels take that path too. The
two failures are distinguished by the *join*, not by the pop existing. Note bubble and quick share
`gpop=544` exactly, the numerical coincidence this row recorded long ago.

✅ **Per-node killswitch confirms causation:**

| arm | bubble | quick |
|---|---|---|
| default | FAIL rc=139 | FAIL rc=139 |
| `SCRIP_ZD=0` | **PASS** | rc=0, wrong answer (§5) |
| `SCRIP_ZD_OMEGA_HEAD=0` | FAIL rc=139 | FAIL rc=139 |
| `SCRIP_ZD_BACKEDGE=0` | FAIL rc=139 | FAIL rc=139 |
| **both of the above together** | **FAIL rc=139** | **FAIL rc=139** |
| `SCRIP_ZD_SKIP=<that node>` | **PASS** | rc=0, wrong answer (§5) |

## 3. ⛔ This corrects the row's working model, and that is the most useful part

The baton is organized around **Site 1** (back-edge) and **Site 2** (`zd_omega_head`'s per-op filter,
now tracked on `zd-omega-head-per-op-filter-...`). The table above shows **neither named killswitch cures
it, and neither does both together** — only disabling `zd_plan` wholesale, or skipping the single
back-edge node, does. So:

- The crash is **not** reachable through the `SCRIP_ZD_BACKEDGE` knob, even though it *is* the back edge.
  That knob controls whether `gback` is *discovered*; with it off, `gpop` falls back to an even larger
  constant (`_wzdepth`), which over-pops harder. **Both settings are wrong, in the same direction** —
  which is why toggling it looks like "no effect" and reads as exonerating the back edge. It does not.
- ⛔ **Do not expect the `zd-omega-head` cure to close this row.** The baton already said to expect
  `bubble`/`quick` to survive it; this is the mechanical reason, now measured rather than predicted.

⭐ **It also confirms an earlier hq_P pass's own hypothesis.** A prior `hq_P` NEXT on this row proposed a
"join-depth mismatch" and was demoted because its witness (`sieve`) had stopped failing, leaving it
"unconfirmed either way". `bubble` is a live witness and the hypothesis is now **confirmed on it**.

## 4. Where the constant comes from

`src/emitter/emit.cpp` (~2594), inside `zd_plan`:

```c
int _gbpre = (gback >= 0) ? (zout[gback] - zd_k(nodes[gback])) : 0;
if (!gin) zgpop[i] = (gback >= 0) ? (_wzdepth - _gbpre) : (...);
```

For `bubble`: `_wzdepth` = 768, target `n23` has `zout=240, K=16` so `_gbpre` = 224, giving
`gpop = 544`. Arithmetically consistent with the plan — **the plan is simply not what happens at
runtime**, because `zout[gback]` is one static number for a label with two differently-deep predecessors.

⭐ **The cure shape (NOT implemented): this is a REFUSE case, not a repair case.** `zd_plan` cannot
express "pop back to a join" with a constant unless every predecessor of that join agrees on depth. The
conservative fix is to detect disagreement and decline to zd-claim the run — the project's own
refuse-not-repair rule — rather than to compute a cleverer constant.

## 5. A SECOND, independent defect found in `quick` — routed, not conflated

With the crash removed (either `SCRIP_ZD=0` or `SCRIP_ZD_SKIP=66`), `quick` exits `rc=0` and prints a
**wrong** value:

```
m3            :  -50000 | 15505      <-- correct
ref           :  -50000 | 15505
m4 (crash off):  -50000 | 10414      <-- WRONG
```

⛔ This is **m4-specific and independent of `zd_plan`**, so it is *not* the row named
`pascal-quick-wrong-checksum-m3` (that name says m3, and m3 is correct here). It was invisible while the
SEGV masked it. A wrong **answer** is `hq_C`'s under the two-HQ interlock — routed there, not chased here.

## 6. Why I stopped at the cure boundary

I hold this row and Site 1 has no row of its own, so curing it is in scope. I did not, deliberately:
`zd_plan` is a **shared node** — SNOBOL4, Icon and Prolog all lower through it — so a cure is owed the
full SHARED-NODE verdict set, and two seats have already produced necessary-but-insufficient fixes in
this exact function. A depth-agreement analysis written in a hurry is how a third one gets produced. The
next actor gets a proven repro, an exact node, a killswitch, and a named cure shape instead.

## 7. State

- Trees: SCRIP `373d6774`, corpus `a37491bd4`, `.github` `aaf36fbb`; `make pristine`, `RT_OPT=-O0`.
- Grid re-measured fresh, `setarch -R`, 3 reps: `bubble` and `quick` FAIL rc=139 3/3; the other seven
  PASS 3/3. Matches every prior session's set — no drift.
- ⚠️ Reproducing needs `echo 1` on stdin (the DONE-WHEN says so). With `</dev/null` every kernel prints
  zeros and "fails" at rc=0, which looks like a mass regression and is not one. I hit this first.
