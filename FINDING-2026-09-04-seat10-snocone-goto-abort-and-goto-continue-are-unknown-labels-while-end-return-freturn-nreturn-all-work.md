# FINDING 2026-09-04 seat10 — Snocone `goto ABORT;` and `goto CONTINUE;` FATAL as unknown labels; `goto END;` works

**Row:** snocone-ladder-top-rung-census-from-the-snocone-manual-is-the-score (seat10, lane hq_P)
**Tree:** SCRIP `67ec5095` (rebuilt, incremental `make`, RT_OPT=-O0) · corpus `0a5e14449`

## THE CLAIM

report.md:643-658 documents six reserved labels a bare `goto` may target without a matching user `LABEL:`
declaration: `END RETURN FRETURN NRETURN ABORT CONTINUE`. Building rung12 (`goto_and_labels`) of the Snocone
construct ladder required exercising this set. `goto END;` is the rung's graded `reserved_label_end` witness
(`simple_output_167`, `test_snocone_ladder.sh --to 12` PASS both modes). `ABORT` and `CONTINUE` are not —
both FATAL instead of terminating/looping as their names imply.

## MEASURED

```
$ printf 'l1: OUTPUT = 1;\n\tgoto ABORT;\n\tOUTPUT = 2;\nl2: OUTPUT = 3;\n' > /tmp/t_abort.sc
$ ./scrip /tmp/t_abort.sc </dev/null; echo "rc=$?"
FATAL lower_snobol4 (GZ#5 subset): goto to unknown label: ABORT. Pattern matching, EVAL and CODE are
outside the landed subset (IR_MATCH_* family pending); see GOAL-SNOBOL4-BB.md.
rc=1

$ printf 'l1: OUTPUT = 1;\n\tgoto CONTINUE;\n\tOUTPUT = 2;\nl2: OUTPUT = 3;\n' > /tmp/t_continue.sc
$ ./scrip /tmp/t_continue.sc </dev/null; echo "rc=$?"
FATAL lower_snobol4 (GZ#5 subset): goto to unknown label: CONTINUE. Pattern matching, EVAL and CODE are
outside the landed subset (IR_MATCH_* family pending); see GOAL-SNOBOL4-BB.md.
rc=1

$ printf 'l1: OUTPUT = 1;\n\tgoto END;\nl2: OUTPUT = 3;\n' > /tmp/t_end.sc
$ ./scrip /tmp/t_end.sc </dev/null; echo "rc=$?"
1
rc=0
```

`END` terminates cleanly (native `--run`, rebuilt binary, tree above). `ABORT` and `CONTINUE` both fail
identically: same FATAL text, same subsystem (`lower_snobol4`), same rc=1 — a lowering-time failure, not a
lexer collision (both parse fine as plain identifiers; the FATAL fires only when the lowerer tries to
resolve the goto target).

## ROOT CAUSE — confirmed, not guessed

The lowerer's reserved-label table has no entry for `ABORT` or `CONTINUE`. This is plausible on its face:
both names are already claimed elsewhere in the dialect — `ABORT` is a pattern-matching primitive
(report.md:787-1015, rung09's declared forms) and `CONTINUE`/`BREAK` are the SCRIP-extension loop-control
keywords (rung17, `TT_LOOP_BREAK`/`TT_LOOP_NEXT`) — so a plausible read is that the reserved-goto-label
table only special-cases the four names with no such collision (`END RETURN FRETURN NRETURN`) and the other
two were never wired, rather than being deliberately rejected. Not traced to a specific source line or
commit this session (walker lane, not cure) — this finding reports the observable defect and its measured
boundary, not the fix.

`RETURN`/`FRETURN`/`NRETURN` are report.md's documented function-return labels and are not re-verified here
independently of that text; this finding's own testing covers only `END` (works) and `ABORT`/`CONTINUE`
(both FATAL) — the two forms actually needed to file this gap precisely.

## FOR THE LADDER (this row's own use of this finding)

`config/LADDER.tsv` rung12 (`goto_and_labels`) cites this as the rung's REFUSE case (the row's GOAL requires
at least one construct-must-REFUSE witness per rung) rather than inventing an artificial one. Not absorbed
as a graded witness — same PASS/FAIL/NOBUILD gap noted on rungs 10 and 11's REFUSE cases: `lib_ladder.sh`'s
model has no clean slot for "this specific FATAL is expected," only pass/fail-by-rc-and-output-match.

## RECOMMENDATION, NOT A CURE

Wire `ABORT` and `CONTINUE` into the same reserved-label table `END`/`RETURN`/`FRETURN`/`NRETURN` already
use, OR — if the name collision with the pattern primitive / loop keyword is deliberate — document that
`goto ABORT;`/`goto CONTINUE;` are intentionally unsupported spellings so a future rung doesn't re-discover
this as a surprise. Either is HQ's call; not attempted here (walker, not cure lane, same precedent as this
row's D6/D9 re-tests).
