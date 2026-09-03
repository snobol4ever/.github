# FINDING — three of the six "run-graded reds" this row was assigned were never real defects on the
# OFFICIAL Icon master board: two are missing-companion-file artifacts of the ad hoc census script
# (`scratchpad/icon_census.sh`, not the hardened harness), and the third is an entry ALREADY marked
# XFAIL in both its origin family and the master suite itself, whose expected output (a CLI-argv-
# dependent line) is structurally unreachable under the invocation convention every grading path
# — official board AND this task's own DONE-WHEN — actually uses. None of the three needed, or could
# have taken, a compiler fix.

**seat03 · 2026-09-03 · row `icon-master-six-run-graded-reds-cured`**

## Why this matters beyond just these three entries

The task's own GOAL text names all six as "the whole Icon-master gap" on the authority of a scratch
census script. Two of the three real defects (the `&level` bug and the `*&subject` bug — see the
companion FINDINGs) were genuine and are now fixed. But half the assigned list turned out to be the
instrument, not the compiler — the same class of lesson this project has paid for repeatedly (ORACLE-
DIALECT, TRANSCRIPTION, the "correct procedure/false explanation" and "signal reachable by two causes"
FACT RULES). Recorded here so the next census this thorough gets checked against the actual grading
mechanism BEFORE its list is treated as a work order.

## 1. `procedure_record_limit_replace_1` and `procedure_record_every_replace_2`: missing companion files

Both witnesses need runtime companion data files that live in `corpus/tests/icon/config/`:
`prepro.dat` (`$include "prepro.dat"` in the first) and `fncs1.dat` (`open("fncs1.dat")`, several times,
in the second). The OFFICIAL grading path (`corpus_suite_harness.py`'s `run_suite_entry`, what
`board_icon_master.sh` actually calls) copies companions into each entry's isolated temp dir via
`_copy_companions()`, which searches both the suite's own directory AND its `config/` subfolder —
confirmed by reading the function directly (`corpus_suite_harness.py:1150-1206`). The `extract`
subcommand (`cmd_extract`, what this task's own GOAL text instructs witnesses be pulled with, and what
this task's own DONE-WHEN script uses) does **not** call `_copy_companions` at all — it only
materializes the `.icn`/`.ref`/`.in` files named in its arguments.

Verified directly: both witnesses, extracted via `corpus_suite_harness.py extract` into an isolated
scratch directory with NO companion files present, fail (missing-file errors surface as ordinary wrong
output). The SAME two witnesses, in the SAME scratch directory, with `config/prepro.dat` and
`config/fncs1.dat` copied in by hand, **match their `.ref` byte-for-byte on the current tree, before
either of this session's compiler fixes** — i.e., these two were never broken to begin with; they were
red only under an extraction method that the official board does not use.

**Not a defect anywhere in `src/`. Not touched.** Flagging as a possible harness gap: `cmd_extract`
could optionally call `_copy_companions` too (its docstring already positions it as "materialize ONE
suite entry back into a standalone file... for consumers that need per-witness standalone access"),
but that is a `scripts/corpus_suite_harness.py` change, a different lane than this row, and is not
made here.

## 2. `procedure_scan_while_1`: already XFAIL, expects CLI argv no grading path ever supplies

Full witness (origin `probe_witness__witness_icn_options_dash_branch`):
```icon
procedure main(args)
   local r
   r := opt2(args)
   write("flist size=", *r)
end
procedure opt2(arg)
   local x,i,c,otab,flist,o,p
   otab := table(); flist := []
   while x := get(arg) do
      x ? { if ="-" & not pos(0) then { write("dash") } else put(flist,x) }
   return flist
end
```
`.ref` expects `dash` then `flist size=0` — reachable ONLY if `args` (Icon's real process-argv list) is
non-empty at the call to `opt2`. Confirmed SCRIP's argv passthrough works correctly and as designed:
`./scrip --run file.icn -- -n10 foo` correctly populates `args` with `["-n10","foo"]` (verified
directly). But **no grading path — not `board_icon_master.sh`'s `run_suite_entry`/`run_m3`
(`argv = [scrip_bin, "--run", Path(sno_path).name]`, no trailing args ever appended), and not this
task's own DONE-WHEN (`./scrip /tmp/w6_$$.icn </dev/null`, likewise) — ever passes anything after the
filename.** With zero real argv, `args` is `[]`, `get(arg)` fails immediately on the very first
iteration, the loop body (containing the `write("dash")`) never executes once, and `flist size=0` is
the ENTIRE correct output for that invocation — which is exactly, byte-for-byte, what SCRIP prints,
both before and after this session's changes.

This is not a fresh discovery of brokenness: the witness's own banner, in BOTH its origin family
(`corpus/tests/icon/probe_witness.icn:108`) and the consolidated master
(`corpus/tests/icon/ALL.icn:6193`, `ALL.ref:4630`) already reads
`#-------------------------------------- 10 witness_icn_options_dash_branch XFAIL` — **whoever
converted this witness into the suite already knew, at conversion time, that it cannot be graded
straight, and marked it accordingly.** The master's own XFAIL marker means the OFFICIAL harness (which
parses banners via `BANNER_RE`'s `(?P<xfail> XFAIL)?` group and buckets XFAIL entries into
`xfail`/`xpass` columns, never `pass`/`fail`) does not count this entry as a plain red at all. It
reached this task's "six run-graded reds" list only through a census/DONE-WHEN mechanism that does a
raw run-and-`cmp`, blind to the XFAIL marker both instruments actually carry.

**Not a compiler defect; nothing to fix.** No witness minted (nothing new to regression-protect: the
`.ref` already correctly describes the reachable-with-real-argv case, which SCRIP has always handled
correctly per the `--` test above; the unreachable-without-argv case is not a bug, it is the documented
XFAIL). Flagging for whoever owns the master-board census script: this entry should not be re-listed
as a run-graded red without first checking `ALL.csv`'s own `xfail` column (already `1` for this row) or
the banner it's sourced from.

## 3. Net effect on the assigned row

Of six named entries: 2 were one root-cause compiler bug (`&level`, both now fixed — see companion
FINDING), 1 was a second root-cause compiler bug (`*&subject`, now fixed — see companion FINDING), and
3 were never real defects (2 companion-file extraction artifacts, 1 pre-existing correctly-marked
XFAIL). `procedure_every_alt_replace_4` additionally carries an UNRELATED, pre-existing `&progname`
line mismatch — a suite-consolidation pinning artifact (the master assigns each entry a synthetic
per-entry filename at grading time, and `&progname` is compile-time-baked from the actual invoked
filename per `lower_icon.c:333`'s `icn_pp_source_base()`, so it legitimately differs from the
origin family's pinned name) — separate from `&level`, not a compiler defect, and not closable by any
code change since it is invocation-name-dependent by design (Icon's own `&progname` semantics).

## 4. Independent convergence with hq_B's same-day, larger-scale finding

While this write-up was in progress, ceo and hq_B messaged this row directly (`grade-with-the-honest-
board-the-six-names-stand`, `icon-board-numbers-changed-today-use-by-modes-column`, both 2026-09-03
~14:45 CDT) reporting the SAME class of defect at the scale of the WHOLE master board, landed on origin
at SCRIP `668b308b`: 153 of the master's 534 entries are parser-ladder fixtures whose `.ref` is a
`scrip --dump-ast` dump, and `board_icon_master.sh` was grading them by RUNNING them — their reds were
inevitable and never meant anything, exactly the same shape as this FINDING's §1 (a witness graded
through a method that cannot produce its expected output, independent of any compiler defect). hq_B's
honest re-measurement (pristine, corpus `353cd537`): ast-graded 153/153 PASS, run-graded 377/381 both
modes (3 FAIL, 1 XFAIL, zero crash, zero hang) — i.e. the TRUE run-graded gap this row should be
chasing is three m3 fails and three m4 fails over a 381 population, not six names pulled from the
pre-fix 398/534 board. Per ceo's routing, this row re-measures against the corrected instrument
(`SUITE_LIST_ALL=1 bash scripts/board_icon_master.sh`, `--by-modes-column`) before closing, and hq_B is
now the ask target for any further Icon-board-instrument question. This section is added as the
connective tissue between two independently-found instances of RULES.md's own TRANSCRIPTION/
signal-reachable-by-two-causes class, found on the same tree the same day by two different sessions
neither aware of the other's work until this message.

## 5. State

Filed alongside the two compiler-bug FINDINGs from this same row. Recommend routing this file's summary
to ceo (row owner) and to whoever owns `scratchpad/icon_census.sh` and the task's DONE-WHEN authoring,
so the six-count is corrected before it is re-quoted.
