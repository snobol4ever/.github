# FINDING: the fuzz "hang" is an UNBOUNDED control-flow divergence, not a timeout boundary — and Cluster B has ZERO gradeable pairs in either mode

**hq_C · 2026-08-29 · MODE FLEET-16 · row `fuzz-nondeterminism-rootcause` (Lon's row)**
**SCRIP `373d6774` (pristine, `RT_OPT=-O0`) · corpus `a37491bd4` · all three repos `merge --ff-only origin/main` before measuring.**

This is step (2) of the order the baton fixed: *stabilise or explicitly exclude the unstable pairs, before grading any cure.* It is now done, and it changes what the row can and cannot do next.

## 0. ⛔ I RAISED A HYPOTHESIS AND MY OWN MEASUREMENT KILLED IT — RETRACTED IN THE OPEN

I proposed, and put in writing to hq_B and in a script header, that the `rc=124` instability might be **fleet load** rather than the program: this box is one 16-core machine shared by ~20 seat roots, and I measured it at **load 20.5 → 26.8** with several concurrent pristine builds. `rc=124` *is* the timeout firing, so the theory is cheap and reasonable.

⛔ **IT IS FALSE, and the duration histogram is what refutes it.** Wall-clock per run (N=8, 20s ceiling, mode 3):

| witness | fast runs | slow runs |
|---|---|---|
| `fz_red_m1b` | **0.02s** ×2 (rc 0) | **≥20.01s** ×6 (rc 124) |
| `fz_segv_24` | **0.02s** ×4 (rc 0) | **≥20.01s** ×4 (rc 124) |

**There is nothing in between — not one run anywhere near the old 8s boundary.** A load-induced timeout artifact would cluster durations *around* the boundary; these sit at 0.02s or run past any ceiling offered. **The hang is genuine and unbounded, and load is irrelevant to it.**

⭐ **Why this is worth recording rather than deleting:** the theory was reasonable, the next person will have it too, and **an rc alone can never refute it.** `rc=124` is identical whether the program needs 8.1 seconds or forever. Only the *duration distribution* separates them, and no instrument on this row had ever recorded one — six sessions read a timeout code and inferred a hang. Correction filed as an addendum, not a silent edit, per RULES.md § TRANSCRIPTION.

**This is the third time today that an instrument on this row answered a narrower question than the sentence built on it — and the second of those three is mine.**

## 1. The measured state, both modes, on the current tree

`scripts/util_fuzz_witness_predicate_ladder.sh`, N=10, TIMEOUT=20s. The ladder reports the **finest predicate under which each pair is stable**: P1 (stdout,rc) → P2 stdout → P3 rc → P4 crashed?

| witness | mode | observed | finest stable predicate |
|---|---|---|---|
| `fz_red_m1b` | m3 | `0:4 124:6` | ⛔ **NONE** |
| `fz_red_m1b` | m4 | `0:5 124:5` | ⛔ **NONE** |
| `fz_red_m4a` | m3 | `132:3 139:7` | ✅ **P2 stdout only** |
| `fz_red_m4a` | m4 | `139:10` | ✅ **P1 strictest** |
| `fz_red_m4b` | m3 | `0:6 139:4` | ⛔ **NONE** |
| `fz_red_m4b` | m4 | `0:6 139:4` | ⛔ **NONE** |
| `fz_segv_09` | m3 | `139:10` | ✅ **P1 strictest** |
| `fz_segv_09` | m4 | `139:10` | ✅ **P1 strictest** |
| `fz_segv_24` | m3 | `0:5 124:5` | ⛔ **NONE** |
| `fz_segv_24` | m4 | `0:7 124:3` | ⛔ **NONE** |

## 2. ✅ The reframe that rescues a witness: stability is PREDICATE-RELATIVE

The stability runner asked *"stable under (stdout, rc) as a pair?"* and answered correctly. That was then read as **"5 pairs are unusable"** — a stronger claim than the instrument made.

`fz_red_m4a` m3 is the proof: **stdout is constant across all 10 runs while the crash signal cycles 132/139, at a rock-steady ~1.26s.** It is useless for grading an rc and **perfectly usable for grading output** — and a cure that makes the program run correctly changes stdout away from constant-empty, so it *can* falsify. One pair recovered by naming the predicate rather than by changing any code.

⭐ **The general shape, and it is this row's own disease seen from the other side.** The earlier errors were instruments answering a *narrower* question than the sentence built on them (stdout-only read as "the witness"). This is the mirror: an instrument answering a *wider* question than the sentence needs, and being read as a **veto**. Both are the same defect — the predicate was left implicit. Naming it is the cure in both directions.

## 3. ⛔ The exclusion, which is what step (2) actually owed

**RETAIN — 4 pairs, each with its named predicate:**
- `fz_segv_09` m3 **and** m4 — P1, `139:10` both. The strongest arm in the set.
- `fz_red_m4a` m4 — P1, `139:10`.
- `fz_red_m4a` m3 — **P2 (stdout only)**; its rc may not be graded.

**EXCLUDE — 6 pairs, disagreeing even at P4 (crashed vs clean), so no predicate rescues them:**
`fz_red_m1b` m3+m4 · `fz_red_m4b` m3+m4 · `fz_segv_24` m3+m4.

⛔ **ALL FOUR RETAINED PAIRS ARE CLUSTER A** (seat09's `PAT$N_res` hard-coded stack offset). **CLUSTER B — `fz_red_m1b`, `fz_red_m4b`, `fz_segv_24` — NOW HAS ZERO GRADEABLE PAIRS IN EITHER MODE.** The baton already suspected this for m3; it is now measured for both. **A Cluster-B cure cannot be graded against this witness set at all**, and any candidate that appears to pass is passing against a coin.

## 4. ⛔ The baton's stability table is VOID, and the set got WORSE

The recorded first run was **SCRIP `f5231fa6`: 5 stable / 5 unstable, with `fz_segv_24` STABLE rc=0 in both modes.** On `373d6774` it is **4 stable / 6 unstable**, and `fz_segv_24` is **unstable in both** (`0:5 124:5`, `0:7 124:3`).

**128 `src/` files changed between those trees — including `bb_match_any`, `bb_match_break`, `bb_match_notany` and `bb_match_span`, the exact pattern machinery these witnesses exercise.** The REBASE-BASELINE COROLLARY is not theoretical on this row; it fired.

⚠️ **`fz_segv_24` has now been measured in THREE different states on three trees in one day** — `4×empty/6×nomatch` earlier, `STABLE rc=0` at `f5231fa6`, `50/50 unbounded hang` now. It is the least trustworthy witness in the set and should not appear in any argument until it is re-measured on the tree that argument is about.

## 5. ⭐ What the duration data hands the next investigator

The Cluster-B m3 behaviour was recorded in the baton as *"flips between HANG(>10s) and FAIL(rc=0, clean exit, wrong output)"*. That is now sharper: **0.02s or unbounded, with nothing between.** This is not a program that is *sometimes slow*; it is a program that **sometimes enters a loop it never leaves**, and takes the fast exit otherwise.

A binary terminate-instantly / never-terminate split points at a **single nondeterministic value being consumed as a continuation or loop bound** — one uninitialized word, read once, deciding the branch — rather than at accumulated timing drift. `scrip` is built `-no-pie`, so its own ASLR is excluded; the remaining candidates are heap/`libscrip_rt.so` placement and a genuinely uninitialized read in the ARBNO reentry path. ⛔ Note this must be chased **without** the witness set as a grading arm, because Cluster B has none — mint the arm first, or cure blind and grade on `fz_segv_09` only, which is Cluster A and will not move.

## Receipts

- `SCRIP/scripts/util_fuzz_witness_predicate_ladder.sh` (`085274b1`) — exercised in all three directions: rc=2 (N=1, missing dir, empty dir), rc=0 (synthetic deterministic control set), rc=1 (the real witnesses). `one_run` copied verbatim from the stability runner so the two differ in exactly one axis.
- Duration histograms from a throwaway probe (`.scratch`, not committed — it exists to be re-run, and its numbers are all in §0).
- ⚠️ The ladder run in §1 was made with the script as committed except for its **header comment and one `echo` line**, edited afterwards to remove a load warning that §0 had by then disproved. The measurement path (`one_run`, the ladder, the counting) is byte-identical to the committed version.
