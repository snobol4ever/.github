# FINDING 2026-09-04 seat12: icn_scan/icn_var FENCE-gate discovery was broken by a SECOND, later migration — the row's original packages/icon cure is a dead end

Row: `icn-scan-var-buckets-find-a-fraction-of-their-floor-and-the-jcon-family-fails` (minted hq_C 2026-09-02, root cause credited to hq_B/hq_C: "repoint CORPUS at packages/icon/{jcon-ref,jcon-compiler,ipl}"). Closed this session with a different cure. Recording the correction and four incidental discoveries so nobody re-derives them.

## The prescribed cure does not work — verified, not assumed

`corpus/packages/icon/{jcon-ref,jcon-compiler,ipl}` (872 `.icn` files combined) carry **ZERO** `.expected` files and **ZERO** `rung*`-named files (`find ... -name '*.expected' | wc -l` = 0 for all three, checked individually). Repointing either gate's `CORPUS` there admits nothing to either bucket — `test_gate_icn_scan.sh`'s loop requires `${f%%.icn}.expected` to exist before counting a file, and `test_gate_icn_var.sh`'s walk is `-maxdepth 1 -name 'rung*.icn'` besides, which never reaches a subdirectory at all. Per CLAUDE.md's own corpus layout table, `packages/{lang}/` is vendored third-party reference material with its own dedicated graders (`test_icon_jcon_suite.sh`, `test_icon_ipl_suite.sh`, both with current SCORE.md rows) — it was never going to carry loose `.expected` twins.

## The real cause: a SECOND migration, after this row was minted

The row's diagnosis (2026-09-01/02) predates the MASTER-SUITE flattening (CLAUDE.md's "third reorg"). That reorg absorbed most of `tests/icon`'s scan/assign-touching loose files into `tests/icon/ALL.icn`/`ALL.ref`/`ALL.csv`, which is *why* today's loose-directory walk finds almost nothing (icn_scan N=3 of a required 26; icn_var N=12 of 62) regardless of which directory it points at.

**The cure:** `ALL.csv` already carries per-entry feature columns (`scan`, `assign`, ... 61 of them) tagging exactly which master-suite entries exercise which IR kind — no need to re-derive the filter with a `--dump-bb` sniff per file. Both gates now source their corpus-bucket population from `ALL.csv` (rows where the feature column is set, `modes == "m3,m4"` i.e. run-graded not ast-only, `xfail == 0`), materializing each via `lib_master_extract.sh`'s `master_extract_origin` — CLAUDE.md's own "ONE way" to pull a witness out of a flat suite, already precedented in `test_gate_udc.sh`. `CORPUS` itself did not need repointing; it already named `tests/icon`, which is where `ALL.csv` lives.

Verified end to end, fresh runs, 2026-09-04:
- `icn_scan`: N **3 → 55** (floor 26) · m2/m3/m4 PASS=55 FAIL=0, all three modes clean.
- `icn_var`: N **12 → 308** (floor 62) · m2/m3/m4 PASS=308 FAIL=0, all three modes clean (two exclusions below).

Applying the row's own DONE-WHEN logic (bucket N ≥ floor, no `FLOOR FAIL`, no `FAIL=[1-9]` in the bucket line) against both fresh runs: **PASS**. (Re-run through `s4e_msg.sh done` for the computed close rather than re-derived here a third time — a suite this size takes ~25 min combined and this project's own ECONOMY principle is "no suite re-runs to answer questions.") The gates' own overall exit code still reads FAIL — entirely from the unrelated, separately-rowed `src/contracts/` grep-path defect (`icn-tag-single-source-gate-greps-the-retired-src-contracts-path-and-reports-a-false-red`, section (a) of both scripts) that this row's own LINKS section already named as not-this-row; confirmed still present, untouched by this session.

## Part B was mostly already solved — it just wasn't cross-referenced

The row's five suspected "real entry failures" (cxprimes, genqueen, recogn, scan, var) were re-measured directly (not through the new bucket — these are loose KEEPER/DEFERRED files, see next section). `rung36_jcon_scan.icn` no longer exists at all (further drift since the row was minted). Of the remaining four, **all four already have live, named DEFERRED rows**, recorded in `corpus/tests/icon/ALL.excluded.txt` (which is *why* they're absent from `ALL.csv` and so never reached the redesigned bucket):

| entry | tracking row |
|---|---|
| `rung36_jcon_cxprimes` | `icon-coexpression-support-design` |
| `rung36_jcon_genqueen` | `icn-recogn-genqueen-suspend-shape` |
| `rung36_jcon_recogn` | `icn-recogn-genqueen-suspend-shape` (same row — genqueen/recogn share one cause, confirming the row's "one cause, not five bugs" hypothesis for at least this pair) |
| `rung36_jcon_proto` | `icon-v9gen-augmented-assign-and-unary-refresh-plus-two-emitter-gaps` |
| `rung36_jcon_var` | `icon-assign-nameless-emit-guard-var` |

None of these needed a fresh class row from this session — they were already filed, just not linked from this row. The redesigned bucket correctly does not re-surface them (KEEPER/DEFERRED loose files are deliberately excluded from `ALL.csv` by the absorption policy), so this FENCE gate is no longer the place any of the five get re-litigated under a different name.

## Two things that WERE new, not covered by an existing row

**1. `rung36_jcon_lgint` is broken and was untracked** (marked `KEEPER`, not `DEFERRED`, in `ALL.excluded.txt` — no PENDING.md row). Direct measurement: SCRIP wraps at signed 64-bit (`9223372036854775807 + 9223372036854775807 = -2`) where the expected output has ~46-digit results. `corpus/tests/icon/KEEP.md` already documents the identical class for `rung36_jcon_large`/`rung36_jcon_radix` ("checked, not assumed — `grep -rl bignum\|BIGNUM\|bigint src/` finds nothing real... not a Class-C bug, a missing feature") and a third witness was independently named-but-never-scoped by seat01 (`icon-arizona-class-bignum-not-implemented`, `FINDING-2026-09-03-seat01-...` §7: "needs its own scoping first"). Consolidated all three into one new row, **`icon-bignum-arithmetic-not-implemented`** (rank 2, owner hq_B, real oracle-verified DONE-WHEN: `write(9223372036854775807 + 1)` → icont/iconx print `9223372036854775808`, SCRIP prints `-9223372036854775808`, cross-checked directly against `/home/resources/icon-master/bin/icont -x`, not assumed).

**2. An instrument-integrity near-miss, moot for these two gates post-fix but worth a general audit.** Both gates' `run3()` does `timeout "$TO" "$SCRIP" --compile "$f" >"$s4" ... || true` — swallowing the exit status — then compares `A4` (empty if compile aborted and produced no usable `.s`) against `$exp`. Pre-fix, walking loose files directly, `rung36_jcon_proto.icn`'s mode-4 compile **SIGABRTs** (`scripts/test_gate_icn_scan.sh: line 86: NNNN Aborted`) — reproduced identically in both gates' baseline runs — yet was reported `m4=PASS`, because `proto.expected` happens to be empty and `A4=""` matches it. This is very likely just the visible shape of `proto`'s own already-tracked row (an emitter gap manifesting as an abort rather than a clean error), not a new defect — but the *false PASS* is a separate, real instrument bug: a crash should never grade as a pass regardless of what the oracle says. Post-fix this is moot for `icn_scan`/`icn_var` specifically (`proto` is DEFERRED, excluded from `ALL.csv`, never reaches the new bucket) — flagging because the identical `run3()` shape is duplicated verbatim across both gate files and plausibly elsewhere; a compile that aborts should count as a hard FAIL (or REFUSED) independent of the empty-string coincidence. Not fixed here — out of this row's scope, and touching shared `run3()` semantics deserves its own look rather than a drive-by edit.

## Two NEW false-failures the redesign itself introduced, characterized and excluded

Widening `icn_var`'s bucket from 12 to 310 surfaced two entries neither the old walk nor the row's diagnosis ever saw. Both root-caused to certainty, neither is a SCRIP defect:

- **`rung36_all__rung36_jcon_kwds`**: output is byte-identical to the oracle on every line **except** `&progname`, which legitimately varies with whatever filename a program runs under (a real Icon keyword, not a stored constant) — the `.ref` was captured under an unrelated name (`procedure_every_alt_replace_4`), which no extractor will ever reproduce. Test-oracle artifact, not gradable by identity regardless of correctness.
- **`rung36_all__rung36_jcon_fncs1`**: does real file I/O against a companion data file, `corpus/tests/icon/config/fncs1.dat`, that `lib_master_extract.sh` (by design — `.icn`/`.ref`/`.stdin` only) does not fetch. CLAUDE.md's own suite-eligibility rule states graded entries must be self-contained with "no file I/O" — this entry's presence in `ALL.csv`'s `assign==1` population is the pre-existing anomaly, not something introduced or chaseable here.

Both excluded by origin, with the full reasoning inline as a comment, directly in `test_gate_icn_var.sh` (not in the shared `ALL.csv`/`ALL.excluded.txt` — that's shared master-suite data used by many other boards; this exclusion is local to this one gate's bucket query, scoped to the two files actually changed this session).

## Files touched
- `SCRIP/scripts/test_gate_icn_scan.sh`, `SCRIP/scripts/test_gate_icn_var.sh` — discovery redesign + the two documented exclusions.
- `.github` — this FINDING, `SCORE.md` new row, task file LEDGER/NEXT.
- New task: `/home/resources/postoffice/tasks/icon-bignum-arithmetic-not-implemented.task.md`.
- No `corpus/` changes — `ALL.csv`/`ALL.ref`/`ALL.excluded.txt` read-only throughout, deliberately (shared, hot, and this session's findings don't require editing them).
