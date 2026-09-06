# FINDING: icon-ipl-851 "needs individual follow-up" batch — 8 confirmed LIVE-capable (4 minted), 11 resolved non-gradeable, 1 still open, plus a determinism-check recurrence and a new SCRIP defect

Continuing task `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class`, STEP 1: seat01's `UNGRADED.tsv` triage left 20 programs marked with the placeholder reason "needs individual follow-up" (its own ~194/215 already-resolved rows were fine). This session read the source of all 20, tested candidates empirically in the established isolated-sandbox pattern (`lib_icon_ipl_isolation.sh` / `util_cut_icon_ipl_refs.sh`'s own `run_isolated`), and resolved every row.

## 8 confirmed LIVE-capable; 4 minted this session

`cross.icn`, `turing.icn`, `parse.icn`, `lisp.icn` were pure stdin cases — minted via a new `NAME.dat` stdin-sidecar convention added to both `util_cut_icon_ipl_refs.sh` (ref-cutting) and `test_icon_ipl_suite.sh`'s RUN tier (grading), mirroring the convention `test_icon_arizona_suite.sh`/`test_icon_jcon_suite.sh` already use. Both scripts now agree (per RULES.md's FACT RULE). `.dat` fixtures come straight from each program's own documented header example (`cross.icn`'s crossword word list, `turing.icn`'s 3-state busy-beaver machine, a valid statement for `parse.icn`, `(CAR (QUOTE (A B C)))` for `lisp.icn`). All four confirmed byte-identical across the census script's real 4-run determinism check, `--apply`-minted as `.std` refs.

`filecnvt.icn`, `gediff.icn`, `huffstuf.icn`, `iiencode.icn` are also confirmed deterministic (2-run checks in an ad hoc sandbox, same isolation pattern) but need an actual **fixture file** present in the run directory and referenced by fixed argv — not just piped stdin — which the `.dat`-as-stdin convention alone doesn't cover:
- `filecnvt.icn fixture.txt -` (the `-` sends output to stdout)
- `gediff.icn fixture_a.txt fixture_b.txt` (spawns the system `diff`; a designed rc=1 "files differ" is the correct, gradeable outcome)
- `huffstuf.icn -o fixture.txt` (compresses to stdout; **`-i`/`-o` are backwards from the obvious reading** — `-o` is encode, `-i` is decode-an-already-encoded-file)
- `iiencode.icn fixture.txt` (uuencode-style, defaults to stdout; its sibling `iidecode.icn` does not — see below)

None of these four are minted yet. Extending the harness with a fixture-file convention (copy named files into the isolated run dir, pass fixed argv) is real remaining STEP-1 work, not attempted this session.

## 11 resolved as genuinely non-gradeable (real reasons now in UNGRADED.tsv, replacing the placeholder)

Grouped by root cause:
- **Prints wall-clock/hostname/date literally**: `based.icn` (`&host`/`&dateline`), `when.icn` (shells to `ls -al`, computes ages from `&date` vs mtimes), `lister.icn`/`listviz.icn` (identical `main()`, both print `&dateline` in their startup banner). Same class as the already-excluded `shar.icn`/`filexref.icn`/`solit.icn`.
- **Randomness by design**: `csgen.icn` — confirmed empirically (2 runs, same input, different output); calls `randomize()` (real entropy), not a fixed seed.
- **Prints real elapsed time**: `fuzz.icn` — last line is `&time - start_time` in milliseconds; can never be stable regardless of input.
- **Needs an unavailable proprietary binary fixture**: `ddfdump.icn` (ISO 8211 DDF / USGS geo format), `extweave.icn` (Mac Painter 5 MacBinary weave format). Neither is vendored; fabricating a spec-valid instance is out of proportion to this row.
- **Structurally unscriptable (not a missing-input problem)**: `wshfdemo.icn` — its seed/size/percentage prompts work fine via stdin (blank seed uses Icon's fixed, non-clock default seed, itself reproducible), but the final "Do another [Y/N]?" prompt uses `getche()`, which fails deterministically (`Runtime error 103`, confirmed 2/2) over any non-tty stdin regardless of buffered content.

## 2 structural harness gaps found (not fixed this session — span multiple programs, worth a deliberate design decision)

1. **File-output, not stdout**: `versum.icn`, `iidecode.icn`, `iplweb.icn` all produce their real result via a side-effect file (`versum.icn` appends to a `.vsq` file; `iidecode.icn` writes the file named in its input's "begin" header; `iplweb.icn` writes HTML files) rather than stdout. The ref-cutting harness's LIVE/EMPTY taxonomy is stdout-only (`util_cut_icon_ipl_refs.sh`'s own header: "EMPTY -- rc=0, zero bytes of stdout"), so none of these three can ever register as LIVE without extending grading to check a named output file's content post-run. `versum.icn` additionally loops forever by design absent `-t`/`-m` bounds (that part IS traced and confirmed, independent of the file-output issue). `iplweb.icn` has a second, independent problem too: its output is coupled to the size of the *entire* vendored IPL tree, which this very task's census work is actively changing (LIVE count moved 0→9 this session) — not a stable target for a fixed ref even setting file-output aside.
2. **Same-invocation determinism-check blind spot, recurrence**: see below.

## Recurrence: the 4-run determinism check can still false-accept clock-seeded output

Running `util_cut_icon_ipl_refs.sh --apply` this session re-minted `filexref.std`/`gcomp.std`/`qt.std`/`shar.std`/`solit.std` as LIVE — the exact 5 (of 6) programs `FINDING-2026-09-05-seat01-icon-ipl-same-invocation-determinism-check-has-a-blind-spot.md` already proved are genuinely time/clock-seeded. Root cause: the script's 4 total runs fire back-to-back in well under a second, so a second-granularity `&dateline`/`&clock` read can agree by coincidence across all 4 — more agreeing runs alone never closes this gap, they just repeat the same coincidence faster. Verified directly: `solit.icn` run three times with 1-second spacing disagreed every time (a real shuffled deck each run) despite passing the original back-to-back check.

**Fix applied**: `util_cut_icon_ipl_refs.sh`'s confirmation loop now does `sleep 1` before each of its 3 confirm runs, forcing all 4 total runs to span at least 3 real wall-clock seconds — a second-granularity clock dependency cannot survive that. Verified against `solit.icn` post-fix (correctly rejected every time). The 5 bad re-mints from this run were deleted before committing; they were never pushed.

## New SCRIP defect discovered: `parse.icn` SIGSEGVs in both modes

Minting `parse.icn` as LIVE (it passes cleanly against the real Icon oracle, 4/4 agreeing runs) exposed a genuine SCRIP crash: `./scrip --run` and the mode-4 compiled/linked binary both SIGSEGV (rc=139, 3/3 reproducible via `lib_icon_ipl_isolation.sh`) on this program. `parse.icn`'s own header: "It provides an interesting example of the use of co-expressions" (`create`/`@`/`suspend` implementing a co-expression-based lexer feeding a recursive-descent parser). An ad hoc minimal co-expression witness attempted this session hit only this dialect's own semicolon-placement parse errors, not a reduced repro of the crash itself — root-causing and a proper minimal ablation are owed, out of scope for this seat (hq_I census lane, not a src/ cure lane). Filed as `icon-ipl-parse-icn-coexpression-sigsegv-both-modes` (rank 1, owner hq_I per hq_I's own current instruction on the parent baton), flagged UNCONFIRMED against a possible shared cause with the already-recorded `icon-ipl-miu-genqueen-sigsegv-both-modes` row (also SIGSEGV both modes, also generator/backtracking-heavy) — not pre-absorbed into it.

## Population accounting

Before this session: 60 LIVE / 215 UNGRADED (of 275 `progs/*.icn`).
After: 64 LIVE (60 + cross/turing/parse/lisp) / 211 UNGRADED (4 resolved-and-removed, 16 given real reasons in place of the placeholder — 4 of those 16 are verified-LIVE-capable-pending-fixture-harness-support, 11 are genuinely non-gradeable, 1 (`press.icn`, an 896-line custom LZW archiver) remains honestly unresolved for scope/time reasons).
Fresh `test_icon_ipl_suite.sh` measurement (SCRIP `b6c17b331`, corpus with this session's mints, incremental make): m3 RUN_PASS=36 RUN_FAIL=23 RUN_CRASH=4 RUN_HANG=1 / 64; m4 RUN_PASS=36 RUN_FAIL=24 RUN_CRASH=3 RUN_HANG=1 / 64.

STEP 2 (per hq_I's baton note, written concurrently with this session): the remaining ~22-23 run-graded FAILs (excluding the now-4 crashes/1 hang) still need per-class root-cause census with minimal witnesses, owned hq_I. Not attempted this session — this finding is STEP-1-shaped (growing/correcting the graded population itself), which is complementary but distinct from that ask. Left as real remaining work on the parent baton's `## NEXT`.
