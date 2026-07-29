# FINDING 2026-07-29 — Z4-3: the cross-epoch grid is complete; ALL 40 verdicts m3==m4; the call-path degradation reproduces on second hardware; the heap port shows FIB PARITY with cell-stack

**Session:** GOAL-ZETA-FOUR s2 (Opus). **Trees:** SCRIP `58f5c4dd` (untouched this rung) · wt-r12 `f7de3863` rebuilt with `-DZC_FRAME=ZC_FRAME_R12` via the era's own `#ifndef` seam (both `scrip` AND `libscrip_rt` — the EXTRACT-Z4-R12 pairing rule; the worktree edit reverted after build) · wt-cstack `d79a427a` rebuilt at its own default (`ZC_PORT_CSTACK`, verified in its zeta_choices.h line 69) · oracle `sbl` fresh clone. **All timings RT_OPT=-O0, best-of-3 minimum, RELATIVE-ONLY** — this sandbox is slower than s1's across the board (e.g. span C1 459 vs s1's 380), so cross-SESSION absolute comparison is invalid; cross-CONFIG ordering and ratios are the deliverable, and they agree with s1's everywhere they overlap.

## THE GRID (ms, best-of-3 min; verdict vs the fixed probe `.ref` oracles, corpus `34a99159`)

| Config | mode | z4_arith | z4_span | z4_arbno | z4_fib | z4_capture |
|---|---|---|---|---|---|---|
| **C1 frame-r12** (`f7de3863` + R12 flip) | m3 | OK 56 | OK 459 | OK 39 | OK **102** | OK 132 |
| | m4 | OK 53 | OK 483 | OK 45 | OK 100 | OK 127 |
| **C2 frame-rsp** (`d79a427a` cstack default) | m3 | OK 52 | OK 447 | OK 38 | OK **112** | OK 148 |
| | m4 | OK 50 | OK 457 | OK 39 | OK 119 | OK 131 |
| **C3 cell-stack** (HEAD `58f5c4dd` forth default) | m3 | OK 47 | OK **125** | OK 31 | OK **137** | **DIFF** 35 |
| | m4 | OK 43 | OK 124 | OK 25 | OK 134 | DIFF 33 |
| **C4 cell-heap** (HEAD `--zeta-port=heap`) | m3 | OK **85** | SIG11 | SIG11 | OK **137** | SIG11 |
| | m4 | OK 78 | SIG11 | SIG11 | OK 131 | SIG11 |

SIG11 cells report time-to-crash (15–19ms) — meaningless as perf, recorded only as verdicts. C3's capture 35ms is a WRONG-ANSWER speed (see §4) and must never be quoted as a win.

## 1. ALL 40 CELLS: m3 VERDICT == m4 VERDICT — across three epochs and the heap port
Every config × probe pair agrees between `--run` and `--compile` on OK/DIFF/SIG11, including both 2026-07-1x-era worktrees and including every heap crash. Two consequences: (a) a MODE34-IDENTICAL data point that now spans EPOCHS, not just HEAD; (b) ⭐ **the s206 bake fix (`cca948c5`) is proven END-TO-END for the first time** — before it, a mode-4 heap binary silently ran FORTH (`rt_zeta_port_set_mode` clamped 7 away) and would have shown OK where m3 SIG11'd; today the m4 heap column REPRODUCES the m3 crashes exactly. This grid is therefore the first honest m4 heap measurement in the repo. (Mechanics note for reproduction: m4 = `scrip --compile > p.s; gcc -no-pie p.s -L$TREE/out -lscrip_rt -Wl,-rpath,$TREE/out`; no `-lgc` needed on any epoch; timing is the produced binary only.)

## 2. THE CALL-PATH DEGRADATION REPRODUCES ON INDEPENDENT HARDWARE — z4_fib 102 → 112 → 137 across the three generations
s1 measured 71→83→98; this sandbox measures 102→112→137. Absolute numbers differ (different iron), the RATIOS match: C3/C1 = 1.34× here vs 1.38× at s1; C3/C2 = 1.22× vs 1.18×. Monotonic across all three generations, both sessions, both modes (m4: 100→119→134). **The z4_fib RATCHET in Z4-10 is now justified by two independent measurements** — activation cost regressed at BOTH pivots and any config claiming the crown must answer to this probe. Pattern-work half of the ledger also holds: span C3 is 3.6× faster than C2 (447→125) and arbno 1.2× (38→31), so the s1 verdict stands quantified twice: CELL beats FRAME for pattern work, FRAME beats CELL for calls.

## 3. ⭐ NEW — THE HEAP PORT HAS **FIB PARITY**: 137 == 137 (m3), 131 vs 134 (m4)
`z4_fib` (DEFINE recursion, the activation stressor) runs at CELL-STACK speed under `--zeta-port=heap`, while `z4_arith` pays **+81%** (47→85 m3). Read against s206's model: the arith slowdown is the α-carve itself (fc_vlit grants literals 16B cells even in arith-heavy statements — `add rbx,K` + frontier cmp + occasional C tail on every carving box), and the SEGV split is EXACTLY s206's refined law — a box that carves but never consults the grant a second time is slow-but-correct (arith), a box that consults twice dies on the storage-vs-addressing disagreement (span/arbno/capture: FR/FRQ still spell rsp). fib's parity says the DEFINE call path either reaches no per-box carve or hides it entirely under call overhead — EITHER WAY, ⭐ **the config-4 build-out (Z4-8) does not start from a call-path deficit**: the one axis where cell-stack loses to the frames is the one axis where heap currently matches cell-stack. When A-1's addressing half lands, z4_fib is the probe that will say whether heap residence adds activation cost; today's 137 is its baseline.

## 4. C3 capture DIFF pinned to one number: **1350000 vs oracle 1500000** — exactly 0.9×
First line of output, both modes. The probe accumulates capture lengths over fixed iterations, so 0.9× = one character short per capture — the s1 defect-(b) class ("anchored: drops first char") in arithmetic form. Both FRAME epochs compute the oracle-exact 1500000 (C1 and C2, both modes), re-confirming the bisect range `d79a427a..cca948c5` from a third measurement set. Belongs to `GOAL-SNOBOL4-BB.md` (MARKER-CAPTURE / capture-extent family), not Z4 — recorded here because the grid is where it shows.

## 5. Honest limits
(a) -O0, relative-only, stated above — do not quote absolutes. (b) The C4 arith/fib OK timings sit on a port whose grant/consumption contract is KNOWN defective (s206); they are baselines for Z4-8's before/after, not endorsements. (c) The C1 worktree carries a build-time source flip (line 140 default), reverted post-build; the built binaries embody R12 — verified by the era's own smoke plus 5/5 OK including arbno, which SEGVs under the same tree's RSP default per s1. (d) Grid runner preserved at `/home/claude/z4grid.sh` pattern (sandbox-local; recipe restated in §1 for reproduction).
