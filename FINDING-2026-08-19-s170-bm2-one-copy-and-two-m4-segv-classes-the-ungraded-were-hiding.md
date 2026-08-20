# FINDING — s170 (seat4, Claude Opus 5, BM lane): BM-2 finished, and the twelve ungraded programs were hiding two m4 SEGVs — one of them ablated to a three-ingredient witness

**Date** 2026-08-19 · **Queue row** `bm-2-one-copy` (rank 11) · **Brief** GOAL-SNOBOL4-100.md s166 SEAT-BM-3 **item 2 only**
**Landed** corpus `5aa297d3` · SCRIP `e4449403` · .github this commit
**Build discipline** every number below is from a `make pristine` build (HQ-27), stated with the SCRIP commit it was measured at.

---

## 1. What the brief asked, and what the end state is

Lon's *"enough variations"*: delete nine redundant benchmark variants, convert `roman` and `mixed_workload` to harness bodies, `indirect_dispatch` is the seat's call. **END STATE: every `.sno` in `benchmarks/snobol4` harness-driven AND graded; the ungraded list prints empty.**

| | before | after |
|---|---|---|
| `.sno` in `benchmarks/snobol4` | 24 | **15** |
| harness-driven (graded) | 12 | **15** |
| ungraded, silently skipped by the runner | **12** | **0** |
| timed runner verdict | ok=12 (12 skipped, invisible) | **ok=13 bad=0 xfail=2 xpass=0, rc=0** |

**Deleted (9):** `arith_int` `arith_mixed` `arith_str` `cap_imm_nret` `cap_imm_nret2` `eval_dynamic` `func_call_overhead` `pattern_bt_deep` `table_churn` — each a redundant twin of a surviving row.
**Converted (3):** `roman` (check 1102), `mixed_workload` (check 12100), `indirect_dispatch` (check 125750) — every check value read from the live `x64/bin/sbl` oracle, and every one predicted arithmetically **before** it was read (`20*(550+55)=12100`; `sum(i+1, i=1..500)=125750`).

### `indirect_dispatch` — the seat's call was KEEP AND CONVERT, and here is the reasoning
1. **Its xfail premise was dead.** The 2026-06-20 marker said `$FN(X)` makes the oracle raise ERROR 022, so the row was excluded from the denominator. Re-measured today: **the oracle does raise 022 on `$FN(X)` — but the file has not contained `$FN(X)` for some time.** It calls `APPLY(FN, X)`, which the oracle executes correctly (`apply: 6`). The exclusion was inherited from a program that no longer existed. *VERIFY-INHERITED-BLOCKERS, one command, again.*
2. **It has no surviving twin.** The other nine were variants of rows that remain; this is the only row measuring **by-name dispatch** — the class named as the B1 beauty blocker (FINDING-s156). Deleting it would have removed the only throughput measurement of the thing the project calls its top blocker.
3. **It is now gradeable**: oracle green, m3 green, m4 red for a named compiler reason (below), which is what an `.xfail` is for.

---

## 2. ⛔ THE REAL FINDING: an ungraded program is one nobody looks at, and two m4 SEGVs were living there

Both SEGVs are **pre-existing** — neither was caused by the conversion — and both were invisible because the runner's s156 guard (`e57330ff`, correct in itself) **skipped** non-harness programs silently.

### 2a. `mixed_workload` m4 SIGSEGV — ablated to three simultaneous ingredients
Measured at pristine SCRIP `b7e10d3c`: the **pre-conversion** program (corpus `a3604cc9`) SEGVs in m4 exactly as the converted one does, and **so does the same program with its loop count set to 0 — one pass.** Scale is not the trigger; shape is.

`corpus/probe/mwseg/`, four witnesses, **all four green in m3 and on the oracle**, `.ref`s from live `sbl`:

| witness | self-recursive DEFINE | capture + destructive replace | TABLE store of the capture | m4 |
|---|---|---|---|---|
| `mwseg_recfn_capture_table` | ✅ | ✅ | ✅ | **SIGSEGV** |
| `mwseg_flatfn_capture_table` | ❌ | ✅ | ✅ | rc=0 |
| `mwseg_recfn_capture_novar` | ✅ | ✅ | ❌ | rc=0 |
| `mwseg_recfn_table_nopat` | ✅ | ❌ | ✅ | rc=0 |

Remove **any one** ingredient and m4 is green. The first two rows are a **one-ingredient asm-diff pair**: they differ by the single self-call `F = N + F(N - 1)` versus `F = N + 1`.
⛔ **The function is never called.** Its mere presence changes the codegen of the rest of the program — that is where the asm diff starts.
Prior art the census confirms: `bench_sno_rtx.sh`'s s203 comment already recorded *"mixed_workload segfaults on pristine main rc=139"*. It was written into a comment and never became a witness or a board row. **Not hunted further — routed** (END-OF-CONTEXT LAW); this is not the BM lane.

### 2b. `indirect_dispatch` m4 SIGSEGV — B1, in three lines
`corpus/probe/b1/`, new pair, refs from live `sbl`:
* `b1_apply_snodef_target.sno` — `APPLY('ADD1', 5)`, a **SNOBOL-defined** target: oracle 6 · m3 6 · **m4 SIGSEGV**
* `b1_apply_builtin_target.sno` — `APPLY('SIZE', 'abcd')`, a **built-in** target through the same dispatch call: oracle 4 · m3 4 · **m4 4**
* a direct `ADD1(5)` is green in m4 as well.

So **the APPLY machinery is exonerated and the SNOBOL-defined TARGET is the defect** — exactly FINDING-s156's *"by-name dispatch cannot reach SNOBOL-defined targets in m4"*, now reproducible in 3 lines and reachable from a benchmark row that will go green on its own when B1 lands (the runner will say XPASS).

---

## 3. ⛔ THE OLD BENCHMARKS SUITE WAS PASSING ROWS FOR AGREEING THAT A LOOP TOOK ZERO MILLISECONDS

A/B of the scorecard `benchmarks` suite (weight 10), **both arms at one build, SCRIP `b7e10d3c`**, corpus `a3604cc9` (24 programs, in a worktree) vs this change (15 programs):

| | programs | m3 PASS | m4 PASS | suite score (mean) |
|---|---|---|---|---|
| before | 24 | 14 (58.3%) | 13 (54.2%) | **56.3%** |
| after | 15 | **15 (100%)** | **13 (86.7%)** | **93.3%** |

The m4 numerator is unchanged (13) — **no program was made to pass by deleting anything**; the denominator lost nine rows that could never pass and gained three that now do.

And the mechanism of the old PASSes is worse than "they failed". The nine legacy programs print a **bare** `T2 - T1` — no `ms:` prefix — so the suite's `norm=ms` line-stripping does not touch it and the number is compared as if it were output. `indirect_dispatch` scored **PASS in m3 before this change** because the oracle printed `0` and SCRIP printed `0`: *a loop that took zero milliseconds, on both engines.* Its own `.ref` said `6` and matched neither side. **That is a correctness PASS awarded for a timing coincidence** — the same instrument-lies class as s148's global noise floor and s154's `NOISE-FLOOR.tsv` name mismatch, and it is now impossible in this directory because every row's graded line is a deterministic `check:` census.

---

## 3b. RE-PROVED AFTER THE REBASE, PRISTINE, AT THE PUSHED HEAD

Four commits landed in SCRIP during this seat (B1c parity flipped DEFAULT ON `c6245f60`, medium-retire
rung 1 `bcd3984e`, CN-15 `924cf16a`, B1c R1 `dbb6b98d`), so the gate was re-proved from a fresh
`make pristine` at **`e4449403`** rather than quoted from the pre-rebase build (HQ-27):

* timed suite **ok=13 bad=0 xfail=2 xpass=0**, `ungraded: none`, **gc 0 rows**, rc=0.
* all six new witnesses unchanged: `mwseg_recfn_capture_table` and `b1_apply_snodef_target` SIGSEGV in m4,
  the other four green in both modes, all six green in m3 and oracle-identical. **The B1c default flip did
  not clear either SEGV.**
* `.s` artifacts: **0 of 15 moved** at the new HEAD, so the three regenerated artifacts are current and this
  session leaves no regen debt.

---

## 4. Instruments changed (SCRIP `e4449403`)

* **`test_bench_snobol4_timed.sh` — the UNGRADED census, owed since the s158 brief.** Names print under the summary and a non-empty list **fails** the suite. **Proven non-vacuous:** one legacy-shaped program dropped into a scratch `BENCH_DIR` prints `⛔ UNGRADED … legacy_shaped` and exits 1.
* **The same runner gains the corpus-wide XFAIL lane** (`CORPUS-LOCATIONS.md`: `.xfail` counts XFAIL, not FAIL) plus **XPASS** detection: a row that passes with a marker present prints a loud retire-the-marker line and does **not** redden the suite — a defect getting fixed must never read as a suite failure. Both lanes proven non-vacuous against a scratch corpus.
* **`cmp3_snobol4.sh`** — `ORDER` was a typed list of 16 names, six of them deleted today; now computed from the directory.
* **`board_denominators.sh`** — the bench row's xfail count was typed into its own note text; now computed (15 `.sno`, 2 xfail ⇒ 13 graded).
* **`bench_sno_rtx.sh`** — `ARITH` and `ALLOC` named two deleted programs. Repointed, **with the loss named in place**: `arith_mixed` was the ONLY program reaching `rt_num_arith` (40M calls/run, RTX-0d s204) so **nothing measures `rt_num_arith` any more**, and `table_churn` was the densest alloc row so `ALLOC` stays valid but **less sensitive**. Re-minting a mixed int/real timed row is the repair and it is **not done** — it is a new benchmark, outside a "delete the variations" brief.

`NOISE-FLOOR.tsv` re-baked whole (reps=5, 15 rows × 3 engines, one timestamp, one condition); the two m4-dead rows bake as `reps=0/NA` rather than as a silent zero. `roman.s`, `mixed_workload.s`, `indirect_dispatch.s` regenerated — a dry sweep confirmed the other **12 of 15 are byte-identical**, so the artifact delta is exactly the three converted programs.

---

## 5. Owed to HQ / open

1. **`rt_num_arith` is now unmeasured by any benchmark.** Deleting `arith_mixed` was directed; replacing its measurement property was not in the brief. A mixed int/real **harness body** is the repair — a queue row, not a drive-by.
2. **`corpus/probe/mwseg/` is unowned.** Three-ingredient witness, one-ingredient asm-diff pair, m3-vs-m4 divergence ⇒ a MODE34 violation as well as a crash.
3. **`indirect_dispatch` m4 goes green when B1 lands** and the runner will announce it as XPASS; retire the marker then.
4. `scorecard_snobol4.sh report` needs `gawk` (absent here); the raw `results.tsv` was read directly. Not fixed — noting it so the next seat does not read a blank board as a zero.
