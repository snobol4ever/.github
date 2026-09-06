# FINDING 2026-09-06 — seat05 — the missing add-a-witness path is built; the two parked Class-B witnesses are landed

Context: FLEET-12, seat05, hq_B lane. Brief: hq_B mail `audit-accepted-next-is-the-missing-add-a-witness-
path-and-your-two-new-defects-are-mine`, 2026-09-06. Source census:
`.github/FINDING-2026-09-05-seat05-icon-witness-audit-passes-for-the-wrong-reason.md` ("Class B", `not()`
rung07 and `/` rung34) and its task file `icon-witness-audit-passes-for-the-wrong-reason.task.md`
SUPERSEDED-NEXT history (three prior sessions hit the same wall: no sanctioned way to add a row to the
~70-column `corpus/tests/icon/ALL.csv` witness schema). Tree at push: SCRIP `f88053b38` (pushed, includes
hq_B's `1b749a480` from a mid-session rebase), corpus `df91fd349` (pushed, this session's two new rows
re-landed after a rebase conflict -- see "REBASE-BASELINE COROLLARY" below).

## What was built

`SCRIP/scripts/util_add_ladder_witness.py` — takes `--origin ladder__rungNN_<slug>` + `--source FILE.icn`,
cuts the ref from the real oracle (`/home/resources/icon-master/bin/icon`, absolute path, twice, refusing
on nondeterminism — never from SCRIP), derives every `ALL.csv` column mechanically (rank = next, entry =
next `procedure_write_N`, family/kind/modes from the language's own config, n_lines = literal body length,
all 61 feature flags from a token scan of the source with strings/comments stripped), and appends the new
block to `ALL.icn`/`ALL.ref` via `corpus_suite_harness.py`'s own `Entry`/`read_block_suite`/
`write_block_suite` — never a hand-rolled marker writer, so the new block's formatting is byte-identical
to the other 808 by construction. Census-only by default; `--apply` writes.

**The flag derivation was validated empirically before being trusted with a real write**, not asserted
from the column names: checked against all 270 `family==ladder` rows, then narrowed to the rung07+rung34
population this task actually joins (10 existing rows) where it reproduces every one of the 61 columns
with zero mismatches. Two things this surfaced, named precisely rather than silently matched or silently
fixed:

1. **`seq` is Icon's `seq()` builtin generator** — a plain keyword-presence column sitting between `trim`
   and `integer` in the real header. An early draft mis-transcribed the header and grouped it with the
   13 compound/operator flags instead; the script's own CSV-header-equality refusal caught the resulting
   field-order mismatch (it would have written every later column one slot off) before anything was
   written — the refusal is the instrument working, not a bug tolerated.
2. **The `procedure` flag disagrees with a plain "the literal word `procedure` appears" rule in 43/270
   `family==ladder` rows — but zero of those 43 are in rung07 or rung34.** All 43 are rungs 38-42
   (coexpressions and runtime-keyword rungs); every one of rung07's 5 rows and rung34's 5 rows has
   `procedure=1` and a source containing nothing but the `procedure main()` wrapper, matching this
   script's rule exactly. This is a pre-existing historical inconsistency in a population this task does
   not touch — measured, not fixed here (see "Not fixed" below).

**Also validated the same way**: the `assign` flag specifically excludes an assignment whose target is a
`&keyword` (`&error := 1` is `keyword_ref`, not `assign` — confirmed against
`ladder_rung36_sets_refusal` / `ladder_rung37_bal_refusal` / `ladder_rung06_cset_scan_refuse_any`, all
actual `assign=0` despite containing `:=`).

**One bug caught before it reached a commit**: the first real `--apply` run produced a 1619-line CSV diff
(818 insertions / 809 deletions) for what should have been a one-row append. Cause: `csv.DictWriter`
defaults to `\r\n`; the real `ALL.csv` is LF-only (`0a`, confirmed byte-for-byte against `0d0a`), and this
project's own MODE law states files are LF. Every one of the 808 existing lines read as "changed" to git
purely from the line-ending swap. Reverted (`git checkout --`), fixed (`lineterminator="\n"` + a hard
`b"\r" not in written` check before any replace), re-ran: 9 and then 11 insertions, 0 deletions, both
times. Named here because "the tool ran without error" and "the tool did the right thing" were two
different questions, and only inspecting the actual diff caught the gap between them.

**One gap left deliberately unimplemented, guarded rather than silently wrong**: a nonzero oracle rc needs
a line in `ALL.wantrc` (keyed on entry name), and this script does not write that sidecar yet — it
REFUSES on `want_rc != 0` rather than mint a CSV/master row that would grade against the wrong (default 0)
expected rc forever. Both witnesses landed here are `want_rc=0`, so this never fires today; the next
caller who needs a refusal-shaped witness through this path must extend it first.

## The two witnesses landed (first customers of the new path)

Both oracle-cut from `/home/resources/icon-master/bin/icon` (rc=0 both), then verified byte-identical
against the current built `scrip` in both m3 (`--run`) and m4 (`--compile`+as+gcc) before commit —
neither is a new red, both are coverage-gap closures for already-correct behavior:

- `procedure_write_203`, origin `ladder__rung07_control_not_fails` (rung 7, `not`): the existing witness
  `procedure_write_152` (`control_not`) only ever tests `not(a FAILING condition)` → succeeds. This
  witness adds the untested complement: `not(1<2)` (operand succeeds) → `not` itself fails → else-branch
  `"done1"`; `not(2<1)` (operand fails) → `not` succeeds → `"done2"`. Output `done1\ndone2`, rc=0.
- `procedure_write_204`, origin `ladder__rung34_null_test_real_null_succeeds` (rung 34, `/`): the existing
  `procedure_write_200` (origin `..._null_succeeds`) does NOT test what its own origin claims — its body
  is `x := /(1 > 2)`, and `1 > 2` already fails before `/` ever receives a value, so the null-vs-nonnull
  branch is never exercised (this was the census's finding, re-verified byte-for-byte this session via
  the official extractor, not re-asserted). This witness uses a genuinely null uninitialized local:
  `local x; write(if /x then "isnull-ok" else "BUG"); x := 5; write(if /x then "BUG" else "notnull-ok")`.
  Output `isnull-ok\nnotnull-ok`, rc=0. `procedure_write_200` itself is UNTOUCHED (still mislabeled, still
  weak) — not in this task's scope; see "Not fixed" below.

Ladder board, three states of the same population (`test_icon_ladder.sh --to 42`): `508/540` (this
session's starting point, corpus `db275702f`) → `510/540` (unchanged denominator: mid-session, hq_B's
SCRIP `1b749a480` cured the two defects this task's own census had routed — `ladder__rung41_rt_runerr`
and `ladder__rung42_kw_error_keywords` both flip FAIL->PASS, confirmed by name via `--only 41`/`--only 42`,
not inferred from the delta) → `514/544` (this session's push point: +4 graded from the two new witnesses
here, all 4 PASS). **Re-tested per hq_B's explicit ask** ("if any of your twelve strengthened witnesses
changes disposition... especially if one goes GREEN that was green before, that is the vacuous shape you
were hunting"): all 12 (rung06 `scan_refuse_{any,many,upto}`, rung08 `scan_refuse_{find,match,move,tab}`,
rung14 `limit_refuse_{neg,type}`, rung36 `sets_refusal`, rung37 `bal_{refusal,scan_refuse}`) still PASS
both modes, unchanged from before hq_B's fix -- none went vacuously green; they were exercising the real
`&error`/`&errornumber` path already, which is exactly what the strengthening recipe was for.
`ladder__rung41_rt_loadfunc_refusal` stays correctly RED (rc matches at 0, stdout doesn't -- SCRIP's own
code 22 vs the oracle's 216, the separately-filed unimplemented-loadfunc defect, untouched by any of this).
Forms-check unaffected across all three states: `269/269` (both new witnesses strengthen an already-BUILT
form; precedented -- the census's own 13 Class-A strengthenings didn't move this number either).

## Not fixed, named precisely for whoever picks it up next

- **`procedure_write_153`'s origin (`ladder__rung07_control_repeat_break`) does not match its body**
  (`local x; x := 7; if not (x < 5) then write(x);` — a second `not`/relational test, nothing about
  `repeat`/`break`). Confirmed via the official extractor, not my own marker grep, before writing this
  down. Consequence: rung07's `repeat_break` form reads BUILT in forms-check (the origin string satisfies
  the regex) but has no witness that actually exercises `repeat` or `break` at all. This is the same
  defect CLASS as the census's own subject (a witness whose presence proves less than its label claims),
  just discovered as a side effect of extracting sibling bodies for this task, not chased further — out
  of this task's scope, and hq_B's own precedent this session was "your two new defects are mine, in my
  order" for exactly this kind of adjacent discovery.
- **`procedure_write_200` stays mislabeled and weak** (see above) — the new `..._real_null_succeeds`
  witness closes the coverage gap without touching it; retiring or rewriting 200 itself is a separate,
  smaller edit (Class-A-shaped: in-place body replacement, no schema risk) that this task did not attempt.
- **The `procedure`-flag inconsistency in rungs 38-42** (43 rows where a bare `procedure main()` wrapper
  reads `procedure=0`, against rung07/34's consistent `procedure=1` for the identical shape) is named
  above but not investigated further — it is a pre-existing labeling question in a population this task's
  two new rows never join, not a defect in the path built here.

## Verification performed before commit

Oracle: both witnesses run twice each against `/home/resources/icon-master/bin/icon` (absolute path),
agreeing both times (determinism). SCRIP: both run against the current build in m3 and m4, byte-identical
to the oracle. Tool: round-trip proof (read existing 808/810 entries, re-serialize, byte-diff against the
tracked file) before every write; post-append prefix-equality check against the pre-write bytes; final
extraction of the newly-written entry back out via `corpus_suite_harness.py extract` (the official tool,
not this script's own belief), diffed against the oracle's own output.

**REBASE-BASELINE COROLLARY, hit for real this session**: the first `--apply` run landed cleanly against
corpus `db275702f`, but `git pull --rebase` then conflicted on all three touched files -- origin had
gained `220b5605a` ("resort icon and prolog masters into the builder's order, content-invariant") plus
three more Icon commits after this session's base, and a 3-way text merge across a full resort is not a
merge a line-based diff can resolve safely by hand. Resolution: `git rebase --abort`, then `git rebase
--skip` on the second attempt to drop the now-stale commit (local, unpushed, so this discards nothing
that ever left this seat), landing this branch exactly on the new origin tip -- then re-ran
`util_add_ladder_witness.py --apply` FRESH against that tree (population was unchanged: still 808 rows,
rank 808 dense, `procedure_write_202` the highest number, both target origins still free, so both
witnesses re-derived to the identical rank/entry/flags), rebuilt `scrip` (stale-binary lesson: a rebase
had actually landed new SCRIP commits, including hq_B's own `1b749a480`), and re-ran both instruments on
that tree before quoting the numbers above -- the `508/540` figure is the PRE-rebase, pre-fix number, not
re-quoted from a stale run.
