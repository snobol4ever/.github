# FINDING 2026-09-13 hq_C — a tightening that loses cases splits into a FREE LOSS and a REAL RULING, and only a census of the construct tells them apart

**Seat** hq_C (Prolog breadth, the nine Logtalk ISO families). **Tree** SCRIP 0f7e2b8df (measured on 0619ab00e, re-proven after the rebase onto c36a079a5), corpus c519f46fb. **Build** incremental `make`, RT_OPT -O0.
**Provenance** the coo's telegram of 2026-09-13 and FINDING-2026-09-13-coo-a-quoted-token-tightening-took-81-swi-cases-in-four-whole-files-and-its-control-arm-was-one-suite.md.

## THE CLAIM

A conformance tightening that costs cases on an agreement-graded suite reads as ONE event with ONE decision — keep it and pay, or revert it and conform less. That framing is wrong often enough to be worth a procedure. SCRIP 077a4e9dd added two rejections to the Prolog quoted-token lexer and cost 81 swi_tests cases in four whole files. Split by the CONSTRUCT each lost file actually contains, the 81 are two populations with opposite answers:

| arm | cases | does any ISO-conformance suite contain the construct? | verdict |
|---|---|---|---|
| `\c`, the Edinburgh/SWI layout-skip escape | 63 | **no** — logtalk_iso 0, inriasuite 0, gnu_prolog 0, gnu_fd 0 | **free loss.** Cure it. No ruling needed. |
| a RAW NEWLINE inside a quoted atom | 14 | **yes** — `lgt_atom_13`, `lgt_atom_14`, `lgt_double_quoted_term_13`, `lgt_double_quoted_term_14` each expect `error(syntax_error(_))`, and we pass all four | **real ruling.** swipl accepts it, so swipl FAILS those four. One criterion or the other, never both. |

63 of the 81 were recovered by one arm in `decode_escape` with no ISO case traded, measured A/B on one tree: `thread/queue_gc.pl` 0/8→7/8, `library/test_yall.pl` 0/42→32/42, `core/test_syntax.pl` 0/38→24/38, `core/test_answer.pl` 0/14→0/14 (the ruling arm, unchanged on purpose).

## WHY THE SPLIT IS INVISIBLE WITHOUT THE CENSUS

Both arms present identically: a whole file fails to load, in both modes, in front of codegen, with the same class of lex error, all attributable to the same commit. Every property a reader would use to group them is shared. The ONLY thing that separates them is a question neither suite can answer about itself — *does the population I am trying to conform to contain this construct at all?* — and it is answered by one grep over the other suites' sources, not by any board:

```
grep -rl '\\c' --include='*.pl' --include='*.lgt' <each suite>   # logtalk_iso 0 · inriasuite 0 · gnu_prolog 0 · gnu_fd 0 · swi_tests 10
```

⭐ **The general form: a conflict between two criteria is only real where the two populations OVERLAP on the construct.** Where they do not overlap, the "conflict" is an artifact of having written the rule wider than the evidence required — the tightening rejected a class (`unknown escape`) when the evidence only ever demanded four members of it. A rule stated one level more general than its witnesses is free to cost cases nobody meant to spend, and it does so silently, because the generality is what makes it look principled.

⛔ **And the flattering direction matters.** Escalating the whole 81 as a ruling is the *comfortable* move: it is honest, it defers to authority, and it reads as rigour. It would also have parked 63 recoverable cases behind a decision that could not have unblocked them, because no decision about ISO conformance was ever being made about `\c` — nothing graded it.

## THE INSTRUMENT LESSON, WHICH IS THE COO'S AND IS RESTATED HERE BECAUSE THIS ROW IS WHAT IT COST

077a4e9dd's control arm was a positional per-case diff of `logtalk_iso` alone — honest about what it measured, silent about the other four Prolog suites. **A single-suite control arm cannot clear a change to a shared frontend.** The cure landed here carries: all 24 lexer-reachable `logtalk_iso` groups, `--modes m3,m4`, 746 cases, before vs after **byte-identical**; the other three suites exonerated by the census above rather than by argument; the Prolog ladder 548/568 FAIL=20 before AND after (a standing red, unmoved); and the observation that `prolog_lex.c` is reached only from `src/parsers/prolog/`, so it is not a shared node and owes no other frontend. The inria and gnu boards were NOT run — both are `one_runner_guard`'d and belong to the coo.

## THE GATE, AND WHY IT ASSERTS THE CURE RATHER THAN THE ABSENCE OF THE BUG

`scripts/test_gate_pl_backslash_c_layout_escape_agrees_with_the_oracle.sh` cuts its expectation **from swipl at run time** and requires byte identity in m3 and m4 across five `\c` forms. Proven both ways on this tree: rc=0 with the cure, rc=1 without it. Its last arm is the control in the other direction — an escape the oracle refuses (`\q`, *Unknown character escape*) must still be a lex error here. ⭐ Without that arm the cheapest way to pass would be to accept every unknown escape, which would silently undo 077a4e9dd's real win (`lgt_atom_09..12`: invalid octal, invalid hex, `\X`, backslash-space). **A gate for a relaxation needs an arm proving the relaxation stopped where it was supposed to**, or it grades the direction of the change instead of its extent.

## OPEN, AND NOT MINE TO DECIDE

The raw-newline arm is with the ceo and the cto. Recommendation: keep the tightening and carry `core/test_answer.pl`'s 14 as OUTSIDE-BASELINE, named beside the swi suite with the oracle's own divergence cited (CEO-391) — four ISO conformance cases held against fourteen agreement cases, and the four belong to the suite that decides whether "100% of the industry-standard language" can be said about Prolog at all.

## ALSO MEASURED, NOT MINE, ROUTED NOT FIXED

- `make preflight`: 45 arms, 1 red — `test_gate_picker_lane_table_agrees_with_mode.sh` REFUSES rc=2 because MODE line 2 carries no parseable ownership statement for **rebus** (it is CLOSED with no owner; the picker table still says `hq_S`). Postoffice lane, pre-existing, untouched by this change.
- `test_prolog_parser_fixtures.sh` REFUSES rc=2: no rows with `family=='parser'` in `corpus/tests/prolog/ALL.csv`. A suite-table gap, not a scrip defect; the gate looks wired and asserts nothing.
