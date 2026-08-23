# FINDING 2026-08-23 seat08 — SPITBOL manual conformance sweep, wave 2 (Chapter 19 complete — SWEEP OF THE ENTIRE MANUAL IS NOW DONE, 168/168)

Row: `conformance-sweep-spitbol-manual` (rank 0, "the highest-yield row factory we have"). This wave finishes what wave 1 (`FINDING-2026-08-23-seat08-spitbol-manual-conformance-sweep-wave1.md`, Ch15/16/18, 85 constructs) left open: the 83 built-in functions of Chapter 19. **With this wave, all 168 constructs enumerated by wave 1 across Chapters 15/16/18/19 have been swept.**

Executed as an 8-way parallel fan-out (one fork per Function-Summary category cluster) against the live `x64/bin/sbl -bf` oracle via `scripts/test_one_witness.sh`, following wave 1's exact methodology: witness sourced from the manual's own worked example wherever one exists, oracle's own raw output checked before ever concluding a SCRIP bug, no cures attempted mid-sweep (row factory discipline).

## Headline

| | Wave 1 (Ch15/16/18) | Wave 2 (Ch19) | Total |
|---|---:|---:|---:|
| Constructs swept | 85 | 83 | **168 / 168** |
| AGREE | 50 | 55 | 105 |
| DIVERGE (constructs) | 11 | 27 | 38 |
| New queue rows minted | 9 | 19 (+1 folded into an existing wave-1 row) | 28 distinct rows |
| Explicitly UNTESTABLE-HERE | 16 | 2 (1 full construct + 1 partial overload) | 18 |

83 witnesses added this wave (`corpus/probe/conformance/f01_*.sno` … `f83_trim.sno`, one `EXIT` overload got a second file `f65b_exit_savefile.sno`), bringing the sweep's total to 61 (wave 1) + 83 = 144 checked-in witness files covering 168 constructs.

## Results by category (Function Summary order)

| Category | # | AGREE | DIVERGE | Untestable | Notes |
|---|---:|---:|---:|---:|---|
| Arrays and tables | 6 | 3 (ARRAY,ITEM,PROTOTYPE) | 3 (RSORT,SORT,TABLE) | 0 | |
| Compilation | 2 | 2 (EVAL,CODE) | 0 | 0 | |
| Function control | 7 | 3 (APPLY,ARG,DEFINE) | 4 (LOAD,LOCAL,OPSYN,UNLOAD) | 0 | |
| Input/output | 8 | 0 | 7 | 1 (SET) | worst category this wave — 3 independent root causes |
| Memory | 3 | 0 | 3 (CLEAR,COLLECT,DUMP) | 0 | |
| Miscellaneous | 6 (excl. EVAL, already counted) | 5 (CHAR,CONVERT,DATATYPE,SIZE,TIME) | 1 (DATE) | 0 | |
| Numeric | 9 | 9 | 0 | 0 | clean sweep |
| Numeric comparison | 7 | 7 | 0 | 0 | clean sweep |
| Object comparison | 2 | 2 (DIFFER,IDENT) | 0 | 0 | |
| Object creation | 2 | 0 | 2 (COPY,DUPL) | 0 | |
| Pattern match | 12 | 11 | 1 (FENCE — folded into existing wave-1 row) | 0 | |
| Program control | 5 (unique names) | 1 (HOST) | 4 (EXIT,SETEXIT,STOPTR,TRACE) | partial (EXIT launch-form) | |
| Program-defined data type | 2 (excl. DATATYPE) | 1 (DATA) | 1 (FIELD) | 0 | |
| String comparison | 6 | 6 | 0 | 0 | clean sweep |
| String synthesis | 6 (excl. DUPL) | 5 | 1 (TRIM) | 0 | |

Cleanest categories: Numeric, Numeric comparison, String comparison — all fully AGREE, zero findings. Weakest: Input/output (0 of 8 clean) and Memory (0 of 3 clean).

## New queue rows minted this wave (19, all rank 1-2, none rank 0 — no crashes this wave)

| Rank | Row | What's broken |
|---|---|---|
| 1 | `conform-rsort-sort-array-noop` | `RSORT(array)`/`SORT(array)` don't sort — table-argument overload (via `CONVERT`) works fine |
| 1 | `conform-table-default-arg-ignored` | `TABLE(i,x,arg)`'s 3rd-arg default-for-missing-key is silently dropped (manual's own worked example) |
| 1 | `conform-clear-exclusion-ignored` | `CLEAR(s)`'s exclusion-list argument is silently dropped — behaves identically to bare `CLEAR()` |
| 1 | `conform-copy-table-aliases` | `COPY(table)` returns an alias, not a copy — mutating the "copy" mutates the original. `COPY(array)` is correct |
| 1 | `conform-unload-noop` | `UNLOAD(name)` is a complete no-op — the function stays callable afterward |
| 1 | `conform-field-never-succeeds` | `FIELD(s,i)` never succeeds, even on valid in-range indices |
| 1 | `conform-local-opsyn-m4-empty` | `LOCAL()`/`OPSYN()` correct in m3, silently empty in m4 — **m3≡m4 codegen-parity invariant violation** |
| 1 | `conform-io-write-read-same-run-empty` | writing a file then reading it back in the same run silently returns empty — breaks a foundational I/O contract |
| 1 | `conform-io-four-functions-unimplemented` | `BACKSPACE`/`DETACH`/`EJECT`/`REWIND` are all completely unimplemented (undefined-function error) |
| 1 | `conform-setexit-noop` | `SETEXIT(name)` traps nothing — a deterministic triggered error behaves identically with or without it armed |
| 2 | `conform-collect-huge-not-failing` | `COLLECT(i)` doesn't fail on an unreasonably large request |
| 2 | `conform-dump-function-noop` | `DUMP(i)` produces zero output (oracle's format is deterministic, not address-bearing — a real fix target) |
| 2 | `conform-dupl-pattern-overload-fails` | `DUPL(pattern,i)` fails outright; `DUPL(string,i)` is fine |
| 2 | `conform-load-missing-error-validation` | `LOAD` doesn't validate/error on a bad file argument (documented error path missing) |
| 2 | `conform-output-1arg-noop` | `OUTPUT(name)` 1-arg convenience form silently no-ops; 3-arg form is fine |
| 2 | `conform-date-format-wrong-length` | `DATE()` is 19 chars, not the documented 17 (likely 4-digit vs. 2-digit year) — tested structurally, not by literal value |
| 2 | `conform-exit-savefile-unimplemented` | `EXIT(n,s)` save-file overload doesn't write a file, exits rc=1 instead of rc=0 |
| 2 | `conform-trace-stoptr-inert` | `TRACE()` produces zero trace output; `STOPTR`'s own divergence is downstream of that, bundled as one row |
| 2 | `conform-trim-tabs-not-stripped` | `TRIM(s)` strips trailing blanks but not tabs, despite both being documented |

Each row's task file carries the measured oracle-vs-SCRIP output and a root-cause hypothesis where one was found. Per this row's brief, **none of these nineteen were cured** — discovery/classification/witness/row only.

## Folded into an existing wave-1 row (not a new row)

`FENCE(pattern)` (Ch19 function-call form) reproduces the identical symptom as wave 1's `conform-amp-abort-fence-broken` (keyword-form `&FENCE` losing its backtrack-suppression) — traced independently to the same behavioral signature through a completely different syntactic path (function argument vs. bare keyword), which raises confidence it's one shared root cause rather than three coincidences. Folded in as a third witness (`f57_fence.sno`) with a root-cause trace added to that row's `## NEXT`; DONE-WHEN extended to require it. No new row minted.

## Explicitly marked UNTESTABLE-HERE (with reason, not skipped silently)

- **`SET(channel,i,i)`** — fully documented (p.235-236) and not listed under Appendix C "Features Not Implemented," but the live oracle itself rejects any call with `ERROR 022 -- undefined function called`, reproduced in an isolated 2-statement repro. No oracle ground truth exists to diff SCRIP against, so per wave 1's precedent for similarly groundless constructs, no witness was filed as a queue row (see also the anomaly note below — a witness for this construct appeared in the working tree from an unexplained source after this sweep's own witness was deliberately removed twice; not filed as this sweep's finding either way).
- **`EXIT(s)` (launch-another-program overload)** — the oracle **segfaults unconditionally** on this construct in this sandboxed container (confirmed via three separate probes: a real command, an absolute-path command, and a guaranteed-nonexistent command that per spec should merely fail, not crash — all three crash identically). Stdout up to the crash point happens to match SCRIP's, but the oracle's rc is not trustworthy ground truth here. `EXIT`'s OTHER overload (save-file creation, `EXIT(n,s)`) IS cleanly testable and IS broken — see `conform-exit-savefile-unimplemented` above.

## Method notes worth restating for future sweeps

- **The "check the oracle's own output first" discipline caught real witness bugs again this wave**, exactly as it did in wave 1: an early `OPSYN` witness had a control-flow bug that skipped the `OPSYN` call entirely (making the oracle's own "undefined function" error *correct*, not a SCRIP bug); an early `SETEXIT` witness used raw arithmetic division-by-zero and the oracle itself misbehaved on it, fixed by switching to the manual's own documented error-class example. Both were caught before filing, not after.
- **Batch A's fork (Arrays/tables/compilation/memory/copy) and Batch E's fork (Numeric) both returned a garbled final summary** (a stray tool-blocking meta-comment instead of their actual report), despite having done complete, correct underlying work — all 22 witness files existed and were valid. Both were re-classified directly by the aggregator against the live oracle rather than trusting the broken report text, which is what surfaced Batch A's unusually high 8-of-13 divergence rate (real, not a reporting artifact) as well as Batch E's clean 9-of-9 agreement. **Lesson: a subagent's own summary can fail even when its work product is sound — verify against the actual artifacts on disk before trusting a report, especially an unusual one.**
- **An unexplained anomaly**: `corpus/probe/conformance/f23_set.sno` reappeared in the working tree (with different content than the sweep's own draft) after this sweep's `SET` witness was deliberately deleted twice upon confirming no oracle ground truth exists. Timestamped after every one of this wave's 8 fork batches had already finished, and no batch owned that filename. Left untouched (not deleted, not run, not committed, not claimed as this sweep's evidence) pending explanation — flagged to the human operator directly rather than investigated further, since root-causing it isn't this row's job and guessing wrong risks destroying someone else's in-progress work.
- **Unrelated but urgent**: while running this wave's batches, the host root filesystem was found at 100% (163M free of 125G) — unrelated to this row, not caused by this seat, reported to HQ separately (`q-disk-space-crisis`) per protocol item 3 (non-blocking FINDING, carry on with the row).

## The sweep is now complete

168 of 168 constructs enumerated in wave 1's Deliverable 1 (Chapters 15, 16, 18, 19) have been swept against the live oracle. 105 AGREE, 38 DIVERGE (across 28 distinct queue rows, one bundling three witnesses), 18 explicitly UNTESTABLE-HERE with stated reasons. This row's own `DONE-WHEN` (artifact existence) has passed since wave 1, but per this row's brief the real bar was sweeping the *whole* reference section — which is now genuinely true, not a technicality. Recommending this row be closed via `s4e_msg.sh done conformance-sweep-spitbol-manual` rather than left open, since there is no more manual left to walk; any further conformance work now belongs to the 28 individual DIVERGE rows this factory produced, not to this row.
