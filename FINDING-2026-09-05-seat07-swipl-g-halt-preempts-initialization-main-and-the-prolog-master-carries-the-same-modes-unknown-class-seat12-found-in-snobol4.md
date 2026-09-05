# FINDING 2026-09-05 seat07 — the prolog oracle's `-g halt` silently truncated every `initialization(Goal, main)` script to empty output; the prolog master's pre-existing 134 ast_fail/84 m3_fail/41 m4_fail/3+3 crash board is the same modes=UNKNOWN class seat12 found in SNOBOL4 today, proven pre-existing and unrelated to this row

**Seat:** seat07 (hq_C lane, Prolog) · **Mode:** FLEET-20 · **Tree:** SCRIP `da9ba149d`+this commit · corpus `4e11cb9ee`+this commit
**Task:** `prolog-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`
**Instrument:** `swipl` (via `lib_oracle_flags.sh` → `resolve_oracle_bin`), both SCRIP modes.

## 1. The bug: `-q -g halt` runs `halt` as a `-g` goal, which fires BEFORE a `main`-flagged `initialization/2` ever gets a chance to

`corpus_suite_harness.py:resolve_oracle_bin` invoked the prolog oracle as `swipl -q -g halt <file>`. `-g Goal`
goals run after loading, before swipl would otherwise enter the top level; `halt` as a `-g` goal terminates the
process right there. `:- initialization(Goal, main).` — the modern, documented SWI entry-point idiom, and the
one every file under `corpus/tests/scrip_test/prolog/` and several `corpus/tests/prolog/` files use — defers
Goal specifically until the point the interactive top level would start, which `-g halt` preempts. Every such
file therefore ran, printed nothing, and got excluded as "oracle produced EMPTY output" (via `--additive`,
which has that guard) or — worse — had a **vacuous ref silently absorbed** via the ordinary loose-pair path
(`discover_pairs`), which has no such guard (see §4).

**Witness:** `corpus/tests/scrip_test/prolog/hello.pl` —
```
:- initialization(main, main).
main :- write('Hello, World!'), nl.
```
`swipl -q -g halt hello.pl` → empty, rc 0. `swipl -q hello.pl` → `Hello, World!`, rc 0.

**The cure:** drop `-g halt`, invoke as bare `-q`. A registered `main`-flagged goal runs and auto-halts with
its own success/fail exit code (the OLD flags always forced exit 0, masking a failing main-goal — a second,
independent correctness gap). A file with no entry point at all falls through to the top level, hits EOF on
the already-`/dev/null` stdin, and exits 0 with at most a trailing newline — already stripped by
`run_oracle`'s own `.rstrip("\n")`; verified empirically against a no-directive witness before this landed.
Changed: `corpus_suite_harness.py`, one line (`resolve_oracle_bin`'s prolog branch) plus docstring. Scope:
this function only — `bench_prolog_vanroy.sh`/`test_bench_prolog_4way.sh`/`bench_prolog_perf.sh` invoke swipl
independently with their own `-g halt` and are untouched by this change; whether they have the same bug is
not investigated here.

**Effect on this row:** re-running the additive absorption after the fix recovered entries the buggy oracle
had wrongly excluded: `scrip_test` category 1→6 absorbed (hello, palindrome, roman, wordcount, +1, all using
`initialization(_, main)`), `tests` category 17→18. Total unabsorbed-census OWED for `--lang prolog` went
from 188 to 5 this session (demos 4→0, benchmarks 141→0, tests(fixture+loose-noref) 39→0; remaining 5 are
loose-pair, see §3).

## 2. A second, narrower guard gap this fix exposed: `discover_pairs` (the ordinary loose-pair path) has no empty-output guard at all

`--additive`'s `_additive_classify_and_run` refuses to absorb when `not ora_text.strip()` (the "vacuous ref is
worse than none" guard). The ordinary path used for files that already carry a `.ref`/`.expected`/`.std`
sibling (`discover_pairs`, invoked by plain `--lang prolog` with no `--additive`) has no equivalent check —
it verified `corpus/tests/prolog/rung15_abolish_abolish_{existing,one_of_two,then_query_fail}.pl` as
"VERIFIED for deletion" and merged them into `ALL.pl`/`ALL.ref`/`ALL.csv` even though all three produce
**empty output under the oracle** (matching their own committed `.expected`, which is itself empty — see §3).
Not fixed here: broader blast radius (used by every language's loose-pair path, not just prolog) and a
correct fix needs to decide whether "committed-empty-matches-fresh-empty" should refuse or merely warn, which
is a design call, not a one-line change. Flagged to hq_C/hq_T rather than patched under this row.

## 3. Three witnesses have a real, separate, source-level defect: `main/0` is defined but never called

`rung15_abolish_abolish_existing.pl` (and its two `_one_of_two`/`_then_query_fail` siblings):
```
:- assertz(fact(a)). :- assertz(fact(b)). :- assertz(fact(c)).
main :- abolish(fact/1), ( fact(_) -> write(found) ; write(gone) ), nl.
main.
```
No `initialization/1` or `initialization/2` directive anywhere — `main/0` is never invoked by anything in the
file. This is NOT the `-g halt` bug (confirmed: empty under both old and new oracle invocation) and NOT the
known `arr_gen=1/lexprep2=1` SCRIP backtracking defect that governs their sibling
`rung15_abolish_abolish_then_reassert` (`PENDING.md`, row `prolog-backtracking-yields-first-solution-only`) —
these three aren't named in `PENDING.md` at all. Their committed `.expected` is also empty, so the ordinary
path's missing guard (§2) let them merge as vacuous entries. **Not fixed here**: adding an `initialization`
directive changes what the fixture asserts and isn't this seat's call without knowing original intent. Left
unabsorbed (reverted out of the master — see §5); disposition (add the directive + cut a real ref, or declare
them permanently excluded) is hq_C's.

The fourth loose-pair entry, `rung22_write_canonical_write_canonical_list.pl`, is NOT defective — it already
produces `[a,b]` matching its committed `.expected` under both old and new oracle invocation. It and the
three broken siblings are blocked on the same mechanical obstacle: §6.

## 4. `tests/snobol4/probe_loose_plz_test_pl_zeta_1.pl` — a `.pl` file with no `--from` category covering its location

Uses plain `initialization(main).`, runs cleanly, produces real output. It sits inside `corpus/tests/snobol4/`,
not `corpus/tests/prolog/`, and no `--from` category (`demos`/`benchmarks`/`tests`/`scrip_test`/
`snocone_ladder`/`programs`) points at that location — `util_unabsorbed_census.py` finds it by extension scan,
but the builder has nothing that walks there. Name (`probe_loose_...`) suggests a deliberate SNOBOL4-lane
fixture (possibly testing that SNOBOL4 corpus tooling ignores non-`.sno` files), not a stray prolog source —
guessed, not confirmed. Left unabsorbed and unexcluded; needs owner confirmation before either absorbing into
the prolog master or naming it excluded.

## 5. Corpus changes actually landed this session

`corpus/tests/prolog/ALL.pl`/`ALL.ref`/`ALL.csv`/`ALL.excluded.txt`/`config/MODES.tsv`: 37 entries absorbed
(13 benchmarks + 18 tests + 6 scrip_test; demos absorbed 0, all 4 candidates legitimately vacuous), all
oracle-cut and three-way agreement (oracle + scrip m3 + scrip m4) verified by the builder itself, plus the
matching exclusion reasons for every candidate not absorbed. The 4 loose-pair entries (§3) were deliberately
**reverted back out** after being found to include 3 vacuous merges (discovered only after they'd already
landed via the guard-less ordinary path) — this master carries none of them; census still reports all 5 of
§3+§4 as OWED.

## 6. Mechanical blocker, both remaining paths: `--delete-absorbed` (and any other file-deleting action) is refused by this harness's own permission classifier

Tried directly: `python3 scripts/util_build_master_suite.py --lang prolog --delete-absorbed`, refused
("Blocked by classifier"). This is the verified, purpose-built, git-tracked, surgical mechanism for removing
now-redundant loose source pairs after a confirmed master absorption — not routed around per the tool's own
guidance to surface rather than bypass a permission wall. Consequence: `rung22` (§3, genuinely correct)
cannot complete its absorption (merge-then-delete-original) until either this permission is granted for that
specific action, or the row's owner deletes the four loose pairs by hand. Reported to Lon/ceo rather than
worked around; not this finding's call to resolve.

## 7. The pre-existing red board — proven pre-existing and unrelated to this row, likely the same class seat12 found in SNOBOL4 today

`corpus_suite_harness.py run ... --lang prolog --by-modes-column --modes m3,m4` on the master as this row
leaves it: `ast_pass=0 ast_fail=134` (100% of ast-graded entries), `m3_pass=427 m3_fail=84 m3_crash=3`,
`m4_pass=427 m4_fail=41 m4_crash=3 m4_skip=43`, `unknown_defaulted_to_run=237`. **Proven pre-existing, not
caused by this row**: ran the identical harness invocation against `corpus/tests/prolog/ALL.{pl,ref,csv}` at
HEAD (before any change this session) — byte-identical `ast_fail=134`, `m3_fail=84`, `m3_crash=3`,
`m4_fail=41`, `m4_crash=3`; only the pass counts and totals differ (390→427 m3-pass, 390→427 m4-pass, exactly
this row's +37 absorbed entries, all clean in both modes; total 611→648).

`unknown_defaulted_to_run=237` strongly suggests this is the identical mechanism
`FINDING-2026-09-05-seat12-capture-target-...-wantnm-mechanism.md` §6 found the same day in the SNOBOL4
master: entries whose `modes` column reads `UNKNOWN` (parser/AST-only fixtures with no declared `modes=ast`)
get graded as `run` by the harness's unknown-defaults-to-run rule, diffing runtime output against what is
actually an AST dump — guaranteed to mismatch regardless of engine correctness. Not confirmed by inspecting
individual entries here (out of this row's time budget); flagged as the likely cause rather than investigated
to ground truth. This blocks this row's own DONE-WHEN (`grep -qE "FAIL=0"` on this exact harness output) via
a pre-existing condition unrelated to source absorption — the same class of problem, one language over.

**Routing:** sent to hq_C (own lane, Prolog) for the row-specific board; also worth hq_T's attention given
seat12 already opened this exact question for SNOBOL4 the same day (`test_gate_modes_declaration_travels.sh`,
wired today, apparently did not flag either population) — not re-investigated here, per the "file it, don't
silently absorb or drop" rule.
