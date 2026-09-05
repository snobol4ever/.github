# FINDING (seat02, 2026-09-05): the aisnobol runner wrote a blank board to SCORE.md when the harness refused over a missing `modes` column

**Seat:** seat02 · **Mode at measurement:** FLEET-16 · **Tree:** SCRIP `d541c082c` (fix), corpus `911c49b77`, RT_OPT=`-O0`, incremental `make`
**Row:** `snobol4-aisnobol-and-dotnet-suites-to-100-percent` (this row's own DONE-WHEN re-verification is what surfaced this)

## THE SYMPTOM

Re-running this row's own literal DONE-WHEN today produced a REFUSE(2) whose tail read:

```
- csnobol4_suite 52/118 PASS · 25 FAIL · 40 REJECT · 1 CRASH both modes (...
⛔ NOT DONE UNTIL PUSHED: commit .github/SCORE.md with the landing that carried this measurement.
```

— text about a *different* suite (csnobol4_suite), not aisnobol, with no obvious connection to the DONE-WHEN
that produced it. Running `scripts/test_snobol4_aisnobol_suite.sh` directly showed why: it printed

```
⛔ REFUSING: .../aisnobol/ALL.csv has no `modes` column -- nothing to honour
AISNOBOL_BOARD shipped=6 scored= excluded=6 m3_PASS= m3_FAIL= m3_CRASH= m3_HANG= m4_PASS= m4_FAIL= m4_CRASH= m4_HANG=
```

and then proceeded to write that exact blank-field text into `.github/SCORE.md`'s shared snobol4/vendor
cell via `util_score_row.py write`, unconditionally.

## ROOT CAUSE, LOCATED EXACTLY

`corpus_suite_harness.py`'s `modes_declarations()` (landed today, `c3948a321`, "the modes declaration must
travel with the suite") now calls `refuse()` when a suite's sibling `ALL.csv` exists but has no `modes`
column at all:

```python
if rdr.fieldnames and "modes" not in rdr.fieldnames:
    refuse(f"{_csv_path} has no `modes` column -- nothing to honour")
```

`corpus/packages/snobol4/aisnobol/ALL.csv` is exactly such a CSV — confirmed directly (`head -1`): it has
no `modes` column, and neither does `corpus/packages/snobol4/gimpel/ALL.csv` (same builder). This is a
pre-existing CSV, not something the aisnobol runner script itself changed; `test_snobol4_aisnobol_suite.sh`
was last touched by `df9fe6af0` (unrelated, this seat's prior session), so the refusal is entirely new
harness behavior meeting an unchanged, always-columnless CSV.

**This refusal correctly returns rc=2** (verified with `$?` captured directly, not through a pipe -- an
earlier ad hoc test of mine mismeasured this via `... | tee ...; echo $?`, which reports `tee`'s exit code,
not the harness's; that mismeasurement is mine, not a defect, and is not repeated in the fix below).

**The actual defect** is in `test_snobol4_aisnobol_suite.sh`, which captured that `rc` but never checked it
before computing `AISNOBOL_BOARD` from the harness's stdout. With no `^SUITE_BOARD` line to parse, every
`field()` lookup returned empty, and the script both printed and *persisted* a board whose every count is
blank -- indistinguishable, downstream, from "measured and everything came back zero." This is exactly the
class RULES.md's THE INSTRUMENT LAWS names: *"AN INSTRUMENT MUST DISTINGUISH 'MEASURED AND CLEAN' FROM
'NEVER RAN.' The two states may not share an output."* Here they did.

Confirmed this is a fresh regression, not a stale local artifact: this same row's own NEXT block recorded a
clean `AISNOBOL_BOARD shipped=8 scored=2 excluded=6 m3_CRASH=2 m4_CRASH=2` reading as recently as ~11:20 CDT
today, before the pull that landed `c3948a321`.

**Blast radius, checked directly, not assumed:** `test_snobol4_dotnet_suite.sh` does its own live-oracle
diff loop and never calls `corpus_suite_harness.py` at all -- unaffected. `test_snobol4_csnobol4_suite.sh`
computes its own `CSNOBOL4_SUITE_BOARD` directly and also never calls the harness's `run` subcommand --
unaffected (an earlier grep match on "SUITE_BOARD" was a coincidental substring hit inside
`CSNOBOL4_SUITE_BOARD`, checked and ruled out). Five scripts do call `corpus_suite_harness.py run`:
`test_snobol4_aisnobol_suite.sh` (this one), `test_icon_rung_suite.sh`, `test_icon_x64_all_rungs.sh`,
`test_icon_all_rungs.sh`, `test_prolog_rung_suite.sh`. Whether the other four share the same
unchecked-`rc`-before-board pattern is **NOT checked here** (time-boxed; those are rung-ladder harnesses
with a different shape, likely reading generated/extracted content rather than a persistent `ALL.csv`) --
flagged as an open question for whoever owns each, not asserted as a confirmed defect anywhere but aisnobol's.

## FIX APPLIED (in this lane, low-risk, does not touch the shared harness)

`scripts/test_snobol4_aisnobol_suite.sh` (SCRIP `9955270e0`, pushed `d541c082c` after a rebase): when
`$board` is empty after the harness call, print `AISNOBOL_BOARD REFUSED -- ...` and write an honest REFUSED
text into SCORE.md instead of fabricating blank counts, then exit non-zero (preserving the harness's own
`rc` if already non-zero, else forcing 2). Verified end to end: real exit code is 2, console output now
reads REFUSED instead of printing blank counts, and the SCORE.md write correctly find-and-replaced only the
`aisnobol: ...` clause inside the shared multi-suite cell -- confirmed via `git diff --word-diff` (one
sentence changed) and by diffing against a concurrent hq_T rewrite of the same cell's *other* content (a
rebase conflict on the same physical line; resolved by taking upstream's fresher content and re-running this
row's own regenerated write on top of it, rather than hand-splicing the conflict, landed `.github` `af419873`).

The prior (correct, pre-regression) reading -- `aisnobol 0/2 m3 . 0/2 m4 SCORED (of 8 shipped, 6 excluded and
named) . m3 FAIL=0 CRASH=2 HANG=0 . m4 FAIL=0 CRASH=2 HANG=0` -- is not lost; it is superseded in SCORE.md's
own history by this landing, same as every other reading in that cell.

## WHAT IS NOT FIXED HERE, AND WHY

The missing `modes` column itself is not added. `util_build_package_suite.py` (the tool that built
aisnobol's and gimpel's containers) has no concept of a `modes` column at all -- regenerating the container
would not add it. Fixing the root cause means either (a) teaching `util_build_package_suite.py` to emit an
empty `modes` column for packages with no ast-typed entries, or (b) relaxing `corpus_suite_harness.py`'s
`refuse()` to treat a wholly-absent column the same as a present-but-empty one for a family that declares no
ast entry -- which is what the landing commit's own Arm D claims already happens ("a family declaring no ast
entry still grades normally"), but does not, empirically, for a CSV missing the column outright. Both routes
touch a shared file (`util_build_package_suite.py` is used by every package suite; `corpus_suite_harness.py`
is today's freshly-landed, heavily-tested shared harness with its own 186-line gate) rather than anything
scoped to aisnobol alone, so this is reported rather than patched unilaterally from this lane.

## ROUTING

Minted `snobol4-aisnobol-csv-missing-modes-column-blocks-measurement` (owner hq_T, instrument/harness lane
per the current 16-seat cut) with full reproduction steps. Sent hq_T the handoff. Sent hq_B (this seat's own
HQ, aisnobol's suite owner) a heads-up that aisnobol is currently unmeasurable pending that cure, and that
the honest REFUSED cell is what will sit in SCORE.md meanwhile rather than a stale or fabricated reading.
