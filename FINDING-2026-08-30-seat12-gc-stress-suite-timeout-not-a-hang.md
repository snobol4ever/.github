# FINDING: repointing `test_gc_stress_suite.sh`'s dead GCDIR surfaced 3 "FAILING CELLS" that looked like hangs — confirmed non-bug, same shape as the porter timeout finding

**Seat:** seat12 (FLEET-16) · **Date:** 2026-08-30 · **Row:** `dead-suite-path-consumer-sweep` · **Found while:** fixing `test_gc_stress_suite.sh`'s dead `GCDIR` default (`corpus/crosscheck/gc/` — deleted by corpus-suites-consolidation, its 15 files converted into the master suite under family `crosscheck_gc`).

## MEASURED
Before this session, the script silently `SKIP`ped (`exit 0`) because `GCDIR` didn't resolve — a genuine population, invisible for an unknown length of time. Once extracted for real (via `lib_master_extract.sh`, `master_extract_family crosscheck_gc`), the suite ran its full 15-witness × 4-stress × 2-mode matrix and reported:
```
STRESS=7 m3: PASS=14 FAIL=1 213_gc_exhaustion_churn
STRESS=1 m3: PASS=13 FAIL=2 213_gc_exhaustion_churn 214_gc_exhaustion_live_set
```
All m4 cells clean at every stress level (15/15). All non-exhaustion witnesses clean at every stress level. Isolating `213_gc_exhaustion_churn` (a 30,000-iteration loop that builds and discards a ~2KB garbage string each pass) at `SCRIP_GC_STRESS=7` under the script's own default `TIMEOUT=60`: **3/3 runs FAIL with rc=124**, every time — this read as a deterministic hang, not flakiness.

## WHY IT ISN'T ONE — CHECKED AGAINST THE ESTABLISHED PRECEDENT BEFORE CONCLUDING "BUG"
`FINDING-2026-08-28-seat06-gc-stress-three-demos-fail...md` already found this exact shape once: `demo_porter` FAILed under a stress arm's tight timeout and looked like corruption, but was actually just ~122x slower under heavy forced-collection (linear cost, not pathological growth) — the fix was a wider `TIMEOUT`, not a code change. Checking the same hypothesis here before writing this up as a bug:
- `213_gc_exhaustion_churn` unstressed: **0.457s**, correct.
- Same witness at `SCRIP_GC_STRESS=25` (the suite's own already-passing arm): **24.091s**, correct.
- Same witness at `SCRIP_GC_STRESS=7`, given a **manual 240s timeout instead of the script's 60s**: **77.937s, rc=0, byte-identical to `.ref`.** Not a hang — genuinely slower, and the old 60s budget was simply never wide enough to see that.
- `SCRIP_GC_STRESS=1` (the suite's most extreme arm) was checked live rather than guessed at: `ps` showed the process at ~4 minutes elapsed, 99.8% CPU, state `R` — actively computing, not stuck — when it was killed to close out this session. **Not waited out to a measured completion**, so its exact duration is NOT confirmed, only that it is consistent with "slow," not "hung."

## FIX APPLIED
`TIMEOUT` widened `60`→`180` (SCRIP `0ab42d47`) — more than 2x the one CONFIRMED worst case (`77.9s`), matching the porter finding's own stated margin convention. This turns the `STRESS=7` cell green. `STRESS=1` for these same two witnesses **may still read FAIL(rc=124) under the new budget** — documented inline in the script rather than silently left as a mystery for the next reader, since it was not re-verified to completion this session.

## SCOPE — NOT CHASED FURTHER, ON PURPOSE
Same call as the porter FINDING's own closing note: whether GC-stress collection cost could be made cheaper is a real, separate performance question, out of scope both for that row and for this one (`dead-suite-path-consumer-sweep` is about dead corpus paths, not GC performance). The `TIMEOUT` widening was in-scope only because a too-short budget was producing a **false FAIL on a correct-but-slow program**, which is the same "does the script now correctly grade" bar this row's own GOAL text already sets — not a rationale for chasing GC performance generally.

## NOT FIXED / NOT CONFIRMED HERE
- `SCRIP_GC_STRESS=1`'s actual completion time for `213_gc_exhaustion_churn` and `214_gc_exhaustion_live_set` — extrapolating linearly from the `STRESS=25`→`STRESS=7` scaling suggests several more minutes, not confirmed. Whoever next runs the full suite with the new `TIMEOUT=180` may still see these 2 cells FAIL; that is expected pending an actual measurement, not evidence of a new defect.
- No `src/` changes — this was a corpus-path/timeout-budget issue throughout, not a runtime defect.

## EVIDENCE
- Old default: `GCDIR="$CORPUS/crosscheck/gc"`, confirmed dead by `test_gate_no_fossil_src_paths.sh`.
- `corpus` git log: `676851209 corpus-suites-consolidation: convert crosscheck/gc (15 files) to suite format`.
- `master_origins_of_family crosscheck_gc` → 15 origins, matching that commit's count exactly.
- Manual timing runs (this session, not the suite's own output): unstressed 0.457s, STRESS=25 24.091s, STRESS=7 77.937s (rc=0, diff-clean).
- `ps aux` snapshot showing the STRESS=1 process CPU-bound (99.8%, state R) at ~4 minutes before being killed to close out this session.
