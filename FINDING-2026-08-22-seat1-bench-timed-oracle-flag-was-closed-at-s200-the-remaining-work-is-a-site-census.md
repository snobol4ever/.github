# FINDING — seat1, `bench-timed-oracle-flag`: the row's main fix already landed at s200; what was left is the ~19-site census, done here

**Date:** 2026-08-22 · **Seat:** seat1 (`/home/claude1`) · **Topic:** `bench-timed-oracle-flag` (QUEUE rank 0) · **Status:** ROW CLOSED, NO CODE CHANGED. The census below is the deliverable.

## 1. The row is stale — the fix it describes already landed

The row's brief (still unchanged in `QUEUE.tsv`) describes `test_bench_snobol4_timed.sh` as hardcoding `sbl -b` with HQ working around it in-flight via `SBLFLAGS`. That was true when the row was written, but SCRIP commit `db8a9ced` (2026-08-21 18:55, **the evening before this session**) already closed it:

- `scripts/lib_oracle_flags.sh` created as **the sole authority** for the SPITBOL language arm (`sbl_lang_flags` → `-bf`, the s189 ruling).
- `scorecard_snobol4.sh`, `test_bench_snobol4_timed.sh`, and `bake_noise_floor_snobol4_timed.sh` all source it and **refuse (exit 3) rather than fall back to a private default** — verified by reading each file directly, not inferred from the commit message alone (`test_bench_snobol4_timed.sh:50-51,71`).
- `NOISE-FLOOR.tsv` was re-baked **today** (2026-08-22T01:03:36Z) under `-bf`, and its own header already states the delta in words, matching the row's own DONE-WHEN wording: *"-b vs -bf measured back-to-back on a quiet box is -0.3% (±2.6%), i.e. ZERO"* — plus a second, more important correction the re-bake surfaced: the *previous* floor was measured under 8-seat fleet load and its min-detectable (47.9%) couldn't have seen a 1.4x regression. The baker now records `nproc`/`loadavg` in the header so a loaded bake can never be silently compared against a solo one again.

I rebuilt none of this — reading the files was enough to confirm it's real, not a claimed-but-unverified commit message.

Two pre-existing FINDINGs (`FINDING-2026-08-20-s188-...` and `-s189-...`) already cover *why* `-bf` is correct; this document doesn't repeat that argument.

## 2. What was NOT closed by s200: the ~19 other `sbl -b` sites

CLAUDE.md and the row both cite "~19 unconverted `sbl -b` call sites" as known follow-up. That count was never itemized anywhere I could find, so I swept `SCRIP/scripts/*.sh` for every operative (non-comment) invocation of the oracle binary with `-b` and not `-bf`, cross-checked each against what it's actually used for, and corrected two false positives from a naive grep (`test_smoke_sn26_spl_bridge{,_d}.sh` — their `-b` hits are the substrings "coverage-b"/"bridge-b", not the flag).

**24 files reference `sbl`+`-b` in some form. They split cleanly into four groups:**

### Already correct (no action)
| File | Note |
|---|---|
| `util_crosscheck_two_oracle_census.sh` | `"$SBL" -bf` at line 37 — already right; its `$CSN -b` is CSNOBOL4 (`snobol4 -b`), a different binary with unrelated flag semantics, out of scope for the SPITBOL-specific s189 ruling. |
| `scorecard_snobol4.sh`, `test_bench_snobol4_timed.sh`, `bake_noise_floor_snobol4_timed.sh` | Fixed at s200 (§1). |

### Deliberately dual-arm — not a conversion candidate
| File | Note |
|---|---|
| `util_oracle_flag_sweep.sh` | Runs `-b` twice (its own control) + `-bf` once, **by design**, to measure the flag's own effect per program. Converting it to `-bf`-only would delete the tool's entire purpose. |

### Doesn't matter functionally (build smoke / dead code / caller-supplied)
| File | Line(s) | Why it doesn't matter |
|---|---|---|
| `build_spitbol_oracle.sh` | 36 | Post-build smoke check ("did the binary run at all"), doesn't compare output against SCRIP. |
| `build_official_oracles.sh` | 38, 82 | Same — build smoke + an echoed usage hint. |
| `util_bench_snobol4_engines.sh` | 9-10 (comments only) | The oracle command is a **caller-supplied argument** (`<cmd...>`), never hardcoded in this script. The header's example invocation is stale documentation (shows `-b`), not a functional defect — worth a doc fix, not a flag fix. |
| `test_crosscheck_all_backends.sh` | 23 | `SPITBOL=` is defined and then **never referenced again in the file** (verified: zero other hits) — grading here is entirely `diff vs .ref`. Dead variable; a cleanup candidate, not a correctness bug. |

### Live grading/timing sites — matters, genuinely not yet converted (16)
Each of these calls `"$SBL"`/`"$ORACLE"`/`"$SWEEP_ORACLE"` with `-b` to either grade SCRIP's output against the live oracle or time SCRIP against it, so the s189 semantics gap (and, for timing scripts, the same load-vs-flag confound §1 found) applies to every one:

`test_3way_snobol4.sh` · `board_sno15_ident.sh` · `test_arbno_radius_ab.sh` · `board_sno15_perf2.sh` · `bench_sno_rail.sh` · `board_sno_apps.sh` · `cmp3_snobol4.sh` · `test_demo_full_3way.sh` · `bench_sno_match4.sh` · `board_sno15_perf.sh` · `test_one_witness.sh` · `test_demo_descent_sweep.sh` · `test_smoke_snobol4_net.sh` · `test_rsp_descent_sweep.sh` · `test_smoke_snobol4_jvm.sh` · `test_smoke_snobol4_wasm.sh`

None of these route through `lib_oracle_flags.sh`; each still spells its own `-b`. **I did not convert them.** Doing so properly means, per file: swap the flag, then prove "no scoring change" the same way s200 did for the timed harness (a real before/after run, not an assumption) — 16 independent verifications is follow-up-row-sized work, not a same-sitting extension of a census. `test_smoke_snobol4_wasm.sh` is the lowest-priority of the 16: WASM is a dormant/stub backend per CLAUDE.md's X86-ONLY rule, so this path is rarely exercised.

## 3. Recommendation

Close `bench-timed-oracle-flag` as done — its actual subject (the timed harness) was fixed at s200 and re-verified here by reading the code, not trusted from the commit message. The 16-file list above is the accurate, named version of "~19 sites... NOT yet converted" and is ready to become its own queue row (or rows, split board/bench/smoke) if wanted; converting all 16 in one sitting was judged out of scope for a census.

## 4. What was not done

No `.sh` files edited. No NOISE-FLOOR re-bake triggered (already fresh from today). No FINDING claims about the 16 sites' actual behavioral impact — that requires running them, which is exactly the follow-up work being scoped out, not sneaked in unverified.
