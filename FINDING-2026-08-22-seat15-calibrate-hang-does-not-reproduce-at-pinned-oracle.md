# FINDING — seat15: `rung-calibrate-hang` CLOSED — the CALIBRATE hang does not reproduce at the pinned oracle commit, and never needed a clock-shaped fix

**Date:** 2026-08-22 · **Seat:** seat15 (`/home/claude15`, Claude Sonnet 5) · **Row:** `rung-calibrate-hang` (rank 1) · **Status:** CLOSED — does not currently reproduce. Zero code touched, per the row's own "do not touch anything clock-shaped until it says you must."

## 1. The brief

Per `FINDING-2026-08-22-s256-hq-both-oracles-already-return-nanoseconds-and-the-2-3x-overhead-reproduces-on-a-wall-clock.md`: seat06's original COARSE-CLOCK diagnosis (`TIME()` reads `0/0/0` under `x64/bin/sbl`) was measured FALSE by HQ — both oracles read real, monotonically-increasing nanoseconds. HQ's own replacement hypothesis, explicitly flagged **unmeasured**: `x64/bin/sbl` runs `harness.inc`'s CALIBRATE ladder 2.30x slower per unit of work, so it needs more doublings, each 2.3x costlier, which against a fixed `timeout` "reads as a hang." First step assigned to whoever took the row: **print `ZK` (and elapsed time) per doubling round** — settle converging-slowly vs. not-converging vs. stuck — before touching anything clock-shaped.

## 2. Method

One-line diagnostic, no other change. Scratch copy only (not committed, per the same convention seat06 used for its own era-matched control build — reproducible from this recipe):

```
ZCAL    ZT = TIME()
        ZBODY(ZK)
        ZE = TIME() - ZT
        OUTPUT = "probe-cal ZK=" ZK " ZE=" ZE " ZFLR=" ZFLR      <- the one added line
        ZK = LT(ZE, ZFLR) ZK * 2                        :S(ZCAL)
```

Applied to a scratch copy of `corpus/benchmarks/snobol4/demo/harness.inc`, included from a scratch copy of `corpus/benchmarks/snobol4/demo/claws5.sno` (the exact "standard, untouched" witness named in seat06's own report). Run against the real `claws5.dat` (66,757 bytes, md5 `8a53f970849d5d030daadeb7803ca368`), oracle invoked the one correct way for a correctness run (`scripts/lib_oracle_flags.sh`): `sbl_lang_flags()` → `-bf`, plus `-s16m` sizing (borrowed from the family's own timed-harness sizing convention, `test_bench_snobol4_timed.sh`).

## 3. Result — two rounds, sub-second total, EXIT=0

```
$ time timeout 20s /home/claude/x64/bin/sbl -bf -s16m claws5_probe.sno < claws5.dat
check: 6469
probe-cal ZK=1 ZE=16991568 ZFLR=20000000
probe-cal ZK=2 ZE=33061621 ZFLR=20000000
iters: 66
ns: 1010609666
ms: 1010
EXIT=0        real 0m1.083s  user 0m1.051s  sys 0m0.031s
```

`ZK=1` costs 16.99ms (under the 20ms floor → double). `ZK=2` costs 33.06ms (crosses the floor → stop, proceed to MEASURE). MEASURE then runs its own `ZBUD=1000ms` budget and reports `iters: 66`, `ms: 1010`. **This is neither "converging slowly" nor "stuck" — it is the ladder behaving exactly as designed, in the number of rounds a healthy calibration is supposed to take.**

**Control, zero modification** (the literal, byte-for-byte corpus files, no probe copy at all):

```
$ time timeout 65s /home/claude/x64/bin/sbl -bf -s16m claws5.sno < claws5.dat   # run from corpus/benchmarks/snobol4/demo/
check: 6469
iters: 39
ns: 1005757470
ms: 1005
EXIT=0        real 0m1.070s
```

Same clean, sub-1.1s completion. The one-line `OUTPUT` add is not the reason it's fast — the unmodified file is exactly as fast. (`iters:` differs 66 vs. 39 between the two runs only because CALIBRATE's `ZK` landing value is load-sensitive at the millisecond scale, same as any wall-clock calibration; both are correct, unremarkable single-run noise, not a discrepancy.)

## 4. Why: the oracle binary in use is already past the bug, and has been since seat06's own session

Checked the exact oracle asset this and every numbered seat resolves to (`S4E_ASSETS` fallback to HQ, per `lib_oracle_flags.sh` / CLAUDE.md D-17b):

```
md5sum /home/claude/x64/bin/sbl        -> 0d1173f910b2570567163c66feb59202
git -C /home/claude/x64 rev-parse HEAD -> ec80390e35f5732abdf77ec7c66090503e5abc78
```

This is **exactly** the binary CLAUDE.md's Workspace map cites as "pinned byte-identical everywhere (commit `ec80390` / md5 `0d1173f9`)" — i.e. the fleet-standard oracle, not a stale or unusually-fresh copy local to this seat.

It is also **exactly** the commit seat06's own report (`FINDING-2026-08-22-seat6-table-flat-1level-segv-does-not-reproduce.md`, §"side discovery") already fast-forwarded to and re-tested against, in the *same* session that first noticed the hang — a detail present in that FINDING but not carried into the row's brief or into HQ's s256 measurement: *"`x64` repo fast-forwarded to `ec80390e` during this session's own handoff (`bin/sbl` rebuilt, `osint/systm.c` reverted `zystm()` from milliseconds back to nanosecond `CLOCK_MONOTONIC`...). Reconfirmed the oracle completes vanilla `claws5.sno` cleanly (1.1s, `iters: 120`)."* Root cause, per that same report: the hang was real, but it was a **stale oracle binary** (repo HEAD `5035571`, dated May 2 2026, binary mtime Aug 19 — predating the s249 NS-TIME migration by two days) reading millisecond-scale or zero `TIME()` deltas against a harness that had already been rescaled to assume nanoseconds. Rebuilding the oracle at `ec80390e` fixed it directly, two days before this row's brief was written.

This measurement is the third independent confirmation of the same fact, by three different methods, on three different days/sessions: seat06 (wall-clock end-to-end, pre/post rebuild), HQ s256 (3-sample `TIME()` probe, post-rebuild only), and this session (per-round `ZK`/`ZE` instrumentation plus a from-scratch control, post-rebuild only). All three agree: **at `ec80390e`, there is no hang.**

## 5. HQ's unmeasured hypothesis is now measured, and is also false

"2.30x slower ⇒ more rounds, each 2.3x costlier ⇒ reads as a hang against a fixed timeout" predicts a *materially* longer CALIBRATE phase than a healthy run. Measured instead: **2 rounds**, the same order of magnitude a fast oracle would take (doubling from a 1-count batch to cross a fixed 20ms floor is a `log2` climb — a constant-factor 2.3x slowdown costs at most one extra doubling round, not an unbounded ladder). Total wall time (1.07s) is explained entirely by `ZBUD=1000ms`'s own MEASURE-phase budget plus process/link/GC overhead — there is no hidden CALIBRATE cost anywhere in the trace. The 2.30x instrumentation overhead measured elsewhere (`FINDING-2026-08-22-seat2-clean-oracle-monitor-overhead.md`, this session's own parent FINDING) is real and reproducible, but it was never the mechanism of *this* symptom — the symptom was a stale binary, already rebuilt.

## 6. Disposition

**CLOSE `rung-calibrate-hang` as does-not-reproduce at the pinned oracle (md5 `0d1173f9` / x64 HEAD `ec80390e`).** No `harness.inc` change, no clock-shaped change, no SCRIP change — none was ever needed once the oracle binary itself was current. Nothing committed to `corpus` (the probe copy is throw-away scratch, reproducible from §2 above, same convention seat06 used for its own control build). **Residual, flagged not fixed:** this is an *asset-freshness* hazard, not a code bug — any seat whose `S4E_ASSETS`-resolved `x64` predates `ec80390e` will still see the exact hang seat06 first reported, with no code-side signal that the oracle itself is the stale ingredient. A future row could have `scripts/lib_oracle_flags.sh` (or a build/setup script) assert the `x64/bin/sbl` md5 against the pinned value and refuse loudly on mismatch, the same "CALLERS MUST REFUSE, NOT FALL BACK" shape that file already uses for the clean-oracle path — not done here, out of this row's scope.

**Watermark:** SCRIP `3cf83181` (untouched) · corpus `2655ee52` (untouched) · `.github` this commit. No regen owed (no codegen/corpus files touched).

**Routed:** this FINDING · `s4e_msg.sh send hq calibrate-hang-closed` pointing here.
