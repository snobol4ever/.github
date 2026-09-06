# FINDING: IPL RUN-tier STEP-2 census — 11 classes named across 28 m3 / 28 m4 non-passes, plus a 186-file population gap outside this row's own scope

Task `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class` (hq_I lane). Resumed under live MODE
FLEET-12 (seat07's own prior session left this claimed, STEP-2 census not started). Fresh measurement on
SCRIP `f88053b38` (post-rebase, incremental `make`, RT_OPT=-O0), corpus post-rebase + this session's
`UNGRADED.tsv` relocation:

```
IPL_SUITE_BOARD total=851 compile_graded=851 compile_pass=615 compile_fail=236 run_graded=64
mode-3 (--run):     RUN_PASS=36 RUN_FAIL=17 RUN_CRASH=10 RUN_HANG=1 / 64
mode-4 (--compile): RUN_PASS=36 RUN_FAIL=24 RUN_CRASH=4  RUN_HANG=0 / 64
```

## Headline: the linkgap class is retired as a cause within this 64-population — the old census is stale

Seat03's original 2026-09-05 census (60-population) attributed **≥24 of 36** m3 FAILs to `linkgap` (SCRIP's
link resolver being single-directory-only). That resolver was cured the same day (hq_I,
`FINDING-2026-09-05-hq_I-ipl-linkgap-was-one-single-directory-resolver...`) by exporting `ICONPATH` across
both the compile and run tiers. The compile-tier board now reads `linkgap=2` over the full 851 — confirmed
directly: every name from the old linkgap list that is still in today's 64-population (`ibrow`, `envelope`,
`toktab`, `diskpack`, `oldicon`, `deal`, `itrcsum`, `makepuzz`, `isrcline`, `conman`, `scramble`,
`ilnkxref`) now compiles and links CLEANLY once `ICONPATH` is correctly exported — confirmed by direct
standalone re-invocation, not by trusting the board's aggregate number alone. **A first draft of this
session's own investigation initially misread these as still-linkgap, because the ad hoc standalone check
did not export `ICONPATH` — corrected before any row was minted off it.** The practical consequence: most
of what used to be "known, out of scope, not this row's to cure" is now either passing outright or failing
for a **different, newly-exposed** reason. This is why a fresh per-name census was necessary rather than
reusing the 2026-09-05 classification.

## Stability check

Every name below was checked at least twice via direct standalone re-invocation (`lib_icon_ipl_isolation.sh`,
1s-spaced repeats) in addition to the full-suite run, specifically because the prior session recorded real
run-to-run crash-count volatility (m3 RUN_CRASH read 4 one run and 10 minutes later, unchanged tree) —
attributed to shared-box contention across FLEET-12's concurrently-running seats. All classifications below
were stable across repeats; the full-suite aggregate may still show run-to-run variance under heavy load
even though the underlying per-program behavior is deterministic.

## Full classification, m3 (17 FAIL + 10 CRASH + 1 HANG = 28 of 64)

| Name | Signal | Class | Status |
|---|---|---|---|
| irunerr | FAIL | `&error`-scoped runerr aborts | known (E) |
| declchck | FAIL | system() unimplemented | known (D) — **signature drifted, see below** |
| banner | FAIL | system() unimplemented | known (D) — drifted |
| oldicon | FAIL | system() unimplemented | **NEW 3rd witness of D** |
| ibrow | FAIL | pipe-mode open() silent failure | **NEW witness of C, mode "rp"** |
| kwicprep, cwd, procprep, fileprep | FAIL | pipe-mode open() silent failure | known (C), mode "p" |
| diskpack | FAIL | pipe-mode open() silent failure | **NEW 5th witness of C, mode "p"** |
| envelope | FAIL | pipe-mode open(), mode "pw" | **NEW witness of C, mode "pw" (branch not confirmed to fire)** |
| igrep, roffcmds | FAIL | parseerr | known, unchanged, out of scope |
| gftrace | FAIL | date format extra space | known (F) |
| ifncsgen | FAIL | `function()` builtin unimplemented | **CONFIRMED (was "unconfirmed class G"), split to own row** |
| toktab | FAIL | showtbl() invalid-sort-order abort vs oracle's graceful zero-report | **NEW class, minted** |
| lisp | FAIL | CAR/QUOTE evaluates wrong | **NEW class, minted** |
| miu, genqueen | CRASH sig11 | real-program SIGSEGV | known (H) |
| parse | CRASH sig11 | generator call-path ABI misalignment | known, already root-caused by hq_I, awaiting cure |
| deal, itrcsum, makepuzz, isrcline, conman, scramble | CRASH sig6 | `IR_REV_ASSIGN` no LOWER-granted varslot (`l_POS`) | **matches existing `te4-lower-varslot-gap` (hq_P) — added as witnesses, not re-minted** |
| ilnkxref | CRASH sig6 | `IR op=122` has no emit template | **NEW class, minted** (distinct from te4-varslot: different guard, different message) |
| vnq | HANG (m3) / CRASH sig11 (m4) | plausibly same nested-reverse-assign family as miu/genqueen (identical 3-deep chain construct at vnq.icn:76) | **added as a flagged-not-absorbed note on the H row** — mode manifestation differs (hang vs crash), so not folded into H's own DONE-WHEN population |

m4's FAIL list adds exactly the te4-varslot six plus `ilnkxref`, each suffixed `(compile/link)` — consistent:
those seven crash at RUNTIME in m3 (which lowers/emits on the fly) but refuse CLEANLY at compile time in m4
(which compiles ahead of running). Real, reported, not double-counted.

## Signature drift: class D's original "ERROR 005" text is now "ERROR 022" — same defect, different text

The 2026-09-05 census recorded declchck/banner's `system()` failure as `ERROR 005 -- Undefined function or
operation`. Today, declchck, banner, oldicon, AND ifncsgen all read `ERROR 022 -- Undefined function called`.
SCRIP's undefined-name error reporting appears to have unified since the original census. **`system()` and
`function()` remain two unrelated missing builtins that now happen to share one generic surface signature —
curing one will not affect the other.** Updated `icon-ipl-system-builtin-unimplemented-error-005`'s own task
file with this drift note so a future grep for "005" doesn't read as cured-and-gone.

## New instrumentation: `scripts/util_icn_class_witness.sh` gained one entry

Added `icon-ipl-function-builtin-unimplemented` — a 5-line synthetic witness (`x := function(); write(x)`),
proven against the real icont oracle (prints `abs`) and against SCRIP (prints the ERROR-022 text, both
modes). The other three new classes (toktab, lisp, op122) were not given synthetic witnesses this session —
each needs either reading two more IPL library sources (`options.icn`/`showtbl.icn`) or a `gdb` backtrace to
name precisely (toktab, ilnkxref respectively), or is already about as minimal as its corpus form gets
(lisp's one-line input) — left as corpus-file-based DONE-WHENs, matching how classes C–H originally shipped
before hq_I's later hardening pass added synthetic witnesses to them.

## A second, larger, separate gap: 186 main-bearing files never triaged (hq_I's find, this session)

Mid-session, hq_I landed `corpus/packages/icon/ipl/UNGRADABLE.tsv` (390 no-`main` files, CONTAINER_OR_LIBRARY)
and flagged by direct message that `851 shipped = 64 graded + 211 (this row's own UNGRADED.tsv, scoped only
to progs/) + 390 UNGRADABLE.tsv = 665`, leaving **186 main-bearing files in NO census file at all** — every
one of them in `gprogs/` (177) or `procs/` (9), since this row's STEP-1 work (seat01/seat03/seat07, prior
sessions) only ever walked `progs/*.icn`. Confirmed the exact count directly:
`grep -lE '^procedure[[:space:]]+main[[:space:]]*\(' procs/*.icn gprogs/*.icn`, diffed against both existing
census files → exactly 186.

Quantified the shape before handing it off (NOT triaged this session — real, separate STEP-1B work):
- **130 of the 177 gprogs-with-main** call `WOpen`/`WAttrib`/`EvGet`/`GetEvent` directly — very likely
  genuinely X11-dependent, same shape as the already-classified 390, pending oracle confirmation.
- **~56 remain plausible headless candidates**: 47 gprogs files with no direct graphics call, plus all 9
  procs-with-main (`emptygen`, `gen`, `eventgen`, `ichartp`, `identgen`, `dijkstra`, `tokgen`, `recog`,
  `sandgen`). These need the same STEP-1 triage `progs/UNGRADED.tsv` already did: run against the real
  oracle, apply the (now `sleep`-hardened) determinism check, cut a ref or name a reason.

Also per hq_I's message: moved `progs/UNGRADED.tsv` → package-root `UNGRADED.tsv` (corpus, this session) to
match every other package's convention (beside `UNGRADABLE.tsv`, where `hq_T`'s instrument reads it) — no
script hardcoded the old path, clean move, confirmed via grep before moving.

## Not attempted this session

- The ~56-file STEP-1B triage above.
- Synthetic witnesses for toktab / lisp / op122 (would need `options.icn`/`showtbl.icn` reads or a gdb
  backtrace).
- Any src/ cure — per this task's own GOAL ("the HQ cures src/, a seat cures fixture- and instrument-level
  reds") and the live MODE file's own division of labor under FLEET-12 ("Sonnet seats walk, census, witness
  — Opus HQs cure"), nothing in `src/` was changed this session. The one SCRIP-repo change is the witness
  script addition (instrument-level).

## Repo state

SCRIP: `scripts/util_icn_class_witness.sh` (+1 witness entry). Corpus: `packages/icon/ipl/UNGRADED.tsv`
relocated (rename only, no content change). `.github`: this finding, `SCORE.md` IPL/vendor cell (auto-written
by `test_icon_ipl_suite.sh`'s own `util_score_row.py` call during this session's measurement run), and the
task-file edits listed above (postoffice, not git-tracked).
