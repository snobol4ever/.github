# FINDING (hq_P/CEO, 2026-08-22 s257) — SCORECARD: FLEET 4 DAYS vs WATCHED 7 DAYS — MORE OUTPUT PER DAY, SAME DAILY RETRACTION RATE

**Commissioned by Lon in-chat, verbatim in substance:** *"how many bugs, flips, and speed bumps we got in last 4 days? Then do same for previous 7 days where I was watching. Let's compare."* Method: commit-subject scans over SCRIP+corpus+.github, `--no-merges`, local-time day buckets; Period A = 2026-08-19→08-22 (fleet, 4 days), Period B = 2026-08-12→08-18 (Lon watching, 7 days). ⛔ LAW 0 discipline: every count is a STATED-CLAIM count (what Lon asked for), pattern-tuned and spot-checked (10-sample audits; "prefix/fixed-point/fixed-work" excluded from `fix`; "mover" dropped as 28% build-determinism noise); each table's grep pattern is recorded in the scan transcript. Claim-counts are NOT verified-fix counts — the gap between them is measured separately below.

## PER-DAY RATES (raw totals never compared across unequal windows)

| metric (stated in commit subjects) | A fleet /day | B watched /day | ratio |
|---|---|---|---|
| non-merge commits (denominator) | 283.5 (1,134 total) | 132.3 (926) | 2.1x |
| bug-fix claims | **57.8** (231) | **38.4** (269) | 1.5x |
| .sno flip-to-working claims | **9.5** (38) | **3.0** (21) | 3.2x |
| speed-improvement mentions | 8.5 (34) | 0.86 (6) | 9.9x |
| new FINDINGs (knowledge capture) | 55.8 (223) | 2.7 (19; zero on 08-12→15) | 20.6x |
| revert/regress/VOID/retract mentions | **11.5** (46) | **11.3** (79) | **1.0x** |

## THE HONEST FLIP MEASURE (trajectory, not mentions)

- **Period A:** main-corpus watermark m3 **326→338** (m4 337, +12 both modes) on a near-stable denominator inside 2 days — **≈6 programs/day, receipted** (`84793d15` → `77185a99`/`1f6cea4d`).
- **Period B:** **no comparable measure exists.** The standardized `m3 X/Y m4 A/B` watermark convention appears ZERO times before the fleet era — it is a fleet invention. B's closest analogues (bb_probes 156/163→185/188; crosscheck 159/178→298/317) doubled their denominators mid-week via suite consolidation, so raw deltas conflate reorganization with cures. **The watched week's record cannot answer Lon's own question about itself; the fleet's can.** That asymmetry is itself a result.

## THE SPEED TRUTH (claims vs landed)

Spot-check: **9 of 10 Period-A "speed" hits are measurements, not speedups** (perf maps, ablations, instrumentation corrections). Genuinely LANDED in A: `byname-bake-cell-address` 1.75x + O(N)→O(1) index map 1.60x — compounding to beauty runtime **2.26x in one day** (4.81e9→2.13e9 Ir) — while roman/arith/string stayed ~1.00x (the finding that split HQ). Genuinely landed in B: ≈none found; B's biggest speed event is **`57f2c62a` — the "38x speedup" VOIDED as measurement error**, a claim minted and retracted entirely inside the watched week.

## INTERPRETATION — BOTH UNCOMFORTABLE DIRECTIONS, STATED

1. **The fleet produced more per day on every metric** — 1.5x fix claims, 3.2x flip claims, a receipted +12-program corpus gain, and the only real speedup of either period — at an UNCHANGED daily retraction rate (11.5 vs 11.3/day; per COMMIT, retraction mentions HALVED, 4.1% vs 8.5%).
2. **But the fleet's output was ~40% self-audit** (retrospective FINDING: 40–45% of its 222 FINDINGs chase its own false signals) — Lon's misinformation charge stands at that magnitude.
3. **And the watched week does not model the alternative Lon proposes.** Under full human watching: same daily retraction volume, the single largest false claim of the whole record (38x), and a record too unstandardized to audit afterward. Human eyes did not catch the 38x — a control-arm measurement did. **Neither autonomy-without-verification nor supervision-without-verification worked; the only thing that worked in either period was a command with a receipt.** (LAW 0's evidentiary basis, now measured on both sides of the fleet boundary.)

**Not measured here:** dollar cost per landed fix (seat-session pricing not in the record); verified-fix rate per claim (would require re-running each claimed cure — CEO audit-loop material, sampled not exhaustive).
