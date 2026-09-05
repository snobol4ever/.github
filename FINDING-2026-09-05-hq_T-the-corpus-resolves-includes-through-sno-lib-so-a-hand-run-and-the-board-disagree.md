# FINDING — include resolution runs through `$SNO_LIB`, so the board and a hand run of the same entry disagree

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~14:15 CDT · **Mode:** FLEET-20
**Tree:** SCRIP `23f342b4d` · corpus `cb0723bb2` · **Graded through:** `run_suite_entry` itself, not a lookalike.

⛔ **This finding RETRACTS AND REPLACES**
[[FINDING-2026-09-05-hq_T-companions-live-outside-the-master-directory-so-26-of-31-entries-cannot-resolve-them]].
That one claimed 26 of 31 `-INCLUDE`-bearing snobol4 entries are graded against dependencies that are not there.
**It is wrong.** The ceo took its census in good faith and re-mailed it to four HQs; this file is the correction.

## What is actually true

A suite entry is graded in a fresh temp dir, and `_copy_companions` searches only the master's dir and its `config/`.
That much was right. What the earlier finding never measured is that **the include search is wider than the copy**:

* `src/driver/scrip.c:963-995` builds the path per input file — the source's own dir, then **every colon-separated
  dir in `$SNO_LIB`**, then an **upward walk** of the source's ancestors adding each `<anc>/include`, `<anc>/lib`,
  `<anc>/library`, then `"."`.
* `corpus_suite_harness.py` sets **`SNO_LIB=<corpus>/include`** on every m3 run and every m4 compile
  (`run_m3`, `compile_m4`), for every language.

So `-INCLUDE 'global.inc'` **does** resolve at grading time, from `corpus/include/`, for all 20 of the `.inc`
companions the earlier finding listed as unreachable.

## Measured, through the grader

The 25 entries that name a companion absent from the master's own directory, graded by `run_suite_entry` with
`companion_dir=tests/snobol4` — the board's own conditions:

```
25 entries : 23 PASS both modes
              1 FAIL both modes  code_eval_len_table_replace_1   (the XDump pattern defect — hq_U's, not this)
              1 m3 FAIL/m4 SKIP  simple_output_70                (XFAIL-marked; OR.sno genuinely unreachable)
```

and the whole master, same tree: `total=1842 m3_pass=1795 m3_fail=1 m4_pass=1795 m4_fail=1`. One fail, not 26.

## ⭐ The real defect, and it is worse than a wrong count

**The resolution is split across two places the corpus does not record, and they disagree by context.**
`$SNO_LIB` is set by the harness; the ancestor walk only finds `corpus/include` when the program is run from
*inside* the corpus tree. An entry extracted to `/tmp` and run by hand has neither — it dies with a hard
`snobol4:9: error: cannot open include 'global.inc'`, no output, rc=1.

So **the same entry is green under the board and a hard parse error by hand**, and nothing in either output says
why. That gap is not hypothetical — it has now produced three wrong reads in two days, all by people doing the
right thing:

* `ALL.xfail`, simple_output_68 and simple_output_70 (seat15, 2026-09-04): *"unresolved from the flat master"* —
  true of the hand run they measured, false of the board that greens the neighbours.
* this seat, 2026-09-05: the retracted finding above, filed after reproducing exactly that hand run.

⭐ **The general form: a dependency satisfied by an environment variable is invisible to every reader of the
corpus.** The corpus looks broken and grades fine, which is the direction that wastes the most time — a green
board gives you nothing to chase, and the hand run gives you a confident, specific, entirely false answer.

## What was genuinely unreachable (cured)

Three files, none of them in `corpus/include`, so neither `$SNO_LIB` nor the companion copy could reach them:
`OR.sno` and its closure `BALREV.sno`, `REVERSE.sno`, all under `corpus/packages/snobol4/gimpel/`.
Materialized into `tests/snobol4/config/` by `util_master_companion_closure.py --write`.
`simple_output_70` then passes **both modes, 3/3 reproductions**, so its XFAIL marker was stale and is promoted
in the same commit — seat15's note predicted an `ERROR 246` there, which does not occur once the whole closure
(not just `OR.sno`) is present.

## The instrument that now holds the line

`scripts/lib_companion_closure.py` models **what the grader can actually reach** — the two dirs the companion copy
searches plus `$SNO_LIB`, sourced from `resolve_paths()["inc"]` so it cannot drift from the harness — and calls
anything present in the corpus but outside that set a gap. `util_master_companion_closure.py --lang all` reports
it (rc=1 gap, rc=2 refusal); `test_gate_master_companions_resolve.sh` is wired into `make test`; the master builder
runs the same closure on every build so an absorption self-heals.

⛔ The declared path deliberately does **not** list `include/`: it is already reachable, and copying its 20 files
beside the master would be churn justified by the premise this finding retracts.

Related: [[FINDING-2026-09-05-hq_T-two-master-entries-are-pinned-green-to-their-own-missing-file-message]] ·
[[FINDING-2026-09-05-hq_T-an-include-that-assigns-a-pattern-variable-makes-a-two-group-alternation-fail]]
