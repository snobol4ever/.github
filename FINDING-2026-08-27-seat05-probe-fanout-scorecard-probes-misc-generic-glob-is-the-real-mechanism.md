# FINDING 2026-08-27 seat05 — the `probe-consolidate-*` fan-out's real, systemic hazard: `scorecard_snobol4.sh`'s `probes_misc` suite generically globs almost all of `probe/`, feeding the project's own official META SCORE

**Date:** 2026-08-27 · **Seat:** seat05 (FLEET-16) · **Row:** investigating `probe-consolidate-fuzz`, but this finding generalizes across the whole `probe-consolidate-*` fan-out · Zero source/corpus edits.

## Headline — this supersedes the framing of my two prior per-directory findings

My prior findings (`probe-bb-is-not-consolidation-material`, `probe-passthru-same-pattern-as-bb`) each found a *specific* live script tied to *one* directory (`test_gate_call2bb_stub_regime.sh` + `run_suite.sh` for `bb`; `board_passthru_combo.sh` for `passthru`). Investigating a third child (`probe-consolidate-fuzz`) surfaced the actual **umbrella mechanism** those were instances of: `SCRIP/scripts/scorecard_snobol4.sh`, "THE SNOBOL4 SCORECARD + META SCORE (Lon directive 2026-08-15 s91)". Its suite table (line 53):

```
probes_misc     5 probe                                               -name *.sno -not -path */bb/*  SELFDIR   20 ms
```

Read literally: `find probe -name '*.sno' -not -path '*/bb/*'` — **every `.sno` file under `probe/` is a scored member of the `probes_misc` suite, EXCEPT `bb/`, which is the only excluded subtree** (because `bb/` already has its own dedicated, higher-weighted suite entry two lines above: `bb_probes 10 probe/bb -name *.sno SELFDIR`). `probes_misc` carries weight 5 (of ~118 total across all suites — roughly 4% of the overall META SCORE, non-trivial), and that META SCORE is the project's own headline "how close to 100% complete" instrument per the script's own header, quoting Lon.

## What this means for the fan-out

`probe-consolidate-bb` is *already* safe from this specific mechanism (it's the one subtree `probes_misc` explicitly excludes, precisely because it has its own dedicated suite entry — consistent with, and independent confirmation of, my earlier finding that `bb` is special). **Every other `probe/` subdirectory in the fan-out — `passthru`, `fuzz`, and (unless similarly special-cased) the rest of the ~14 children — is currently swept generically into `probes_misc` by this glob.** Converting any of them to the one-liner/banner suite format removes their `.sno` files from this glob, which:
- does **not** error or refuse (unlike `board_passthru_combo.sh`'s `for f in "$PT"/pt*.sno`, which at least keeps iterating zero times visibly) — `find` over a smaller tree just silently returns fewer files,
- silently shrinks `probes_misc`'s denominator and therefore the overall META SCORE, in the same "shrunken-denominator-reads-as-clean" failure class this project's own culture has flagged as costly multiple times this week (`corpus-suite-family-list-should-autodiscover`, minted by hq_C at rank 0 specifically because "a suite pair that lands on disk but isn't added to the list is INVISIBLE to the board, not FAIL/MISSING" — the identical shape, one mechanism up).

This is **not a reason no `probe/` subdirectory can ever convert** — it's a reason the conversion of each one needs a corresponding one-line edit to `scorecard_snobol4.sh`'s `SUITES` table (either exclude the newly-converted path the way `bb/` already is, or — better long-term — teach `probes_misc`'s discovery to also read the suite-text format, mirroring the `test_corpus_snobol4.sh` family-list problem hq_C already raised). **Landing that edit is part of each family's conversion, not a follow-up**, exactly the same principle hq_C already stated for `test_corpus_snobol4.sh`'s registration step.

## Disposition for `probe-consolidate-fuzz` specifically

Checked independently, same rigor as the other two: no script hardcodes `probe/fuzz` by literal path (unlike `bb`/`passthru`), but several `.github` FINDINGs (`s188`×2, `s189`×3, `s192`) cite specific witness filenames by name (`fz_abort_fence1_stackcap{,_ctl}.sno`, `fz_abort_arbno_stackcap_ctl.sno`, `fz_segv_03.sno`) as **checked-in discriminator witnesses** for closed-but-documented bug classes — these read as historical-but-permanent reference (the investigations are closed, past-tense; nothing currently open depends on re-running them by exact name the way `bb`'s R-4(h) gate list did). The `probes_misc` mechanism above is the real, live dependency for `fuzz` specifically, same as for every other un-excluded sibling. `probe/fuzz` itself is otherwise clean: flat directory, 59/59 matched `.sno`/`.ref` pairs, no subdirectories, no stdin-dependent tests found.

**Recommendation:** `probe/fuzz` is very likely the SAFEST of the three `probe/` subdirectories checked so far to actually convert — its only live dependency (`probes_misc`) is a mechanical one-line fix (add `-not -path */fuzz/*` to `scorecard_snobol4.sh`, or the harder but more durable generic fix), not an architectural incompatibility like `bb`'s XFAIL mechanism. Not attempted this session (ROW FACTORY discipline — routing this systemic finding first, since it changes how every sibling row should proceed, is worth more than converting one 59-file family before the coordinator has it). Sent to ceo/hq_C, flagged as higher-priority than the two prior findings since it's fan-out-wide, not single-row.
