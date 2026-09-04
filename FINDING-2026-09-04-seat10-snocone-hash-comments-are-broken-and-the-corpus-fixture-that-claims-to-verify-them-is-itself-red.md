# FINDING 2026-09-04 seat10 — Snocone `#` comments are broken (not a comment introducer at all), and the corpus's own fixture that claims to verify them is itself currently RED

**Row:** snocone-ladder-top-rung-census-from-the-snocone-manual-is-the-score (seat10, lane hq_P)
**Tree:** SCRIP `2cd69baa` (rebuilt, incremental `make`, RT_OPT=-O0) · corpus `3573ed14a`

## THE CLAIM THIS CORRECTS

`FINDING-2026-09-03-seat12-snocone-master-70-of-273-reds-were-the-wrong-instrument-real-board-is-7-of-206.md`
measured the Snocone master's genuine runtime board as 206 entries, 7 reds, cleanly classified into **two**
classes (A: `procedure` keyword not implemented, 5 entries; B: pattern CAPTURE not wired for `subject ?
pattern`, 2 entries). **There is a third class that finding did not catch**, and the master's own fixture
built to verify it is itself red — meaning "7 reds, 2 classes" undercounts by at least 1 entry / 1 class as
of this tree. Not a contradiction of that finding's method (which was sound and is what caught this one, by
example) — a regression or a pre-existing miss surfacing now.

## THE FIXTURE, MEASURED

Entry `simple_output_124` (origin `crosscheck_rungB11__B11_comment_hash`, CSV row 261, `modes=m3,m4` — a real
run-graded entry, not an AST fixture the earlier finding's `--by-modes-column` instrument would have skipped):

```
# B11_comment_hash: # is also a line-comment introducer
x = 7; # ignored
OUTPUT = x; # also ignored
```

Expected ref: `7`. **Actual, both modes:**

```
$ ./scrip --run  simple_output_124.sc   # extracted via corpus_suite_harness.py extract
simple_output_124.sc:1: snocone parse error: syntax error
$ ./scrip --compile simple_output_124.sc
simple_output_124.sc:1: snocone parse error: syntax error
```

Hard parse error, both modes, at line 1 — the file does not even survive parsing far enough to reach the
`x = 7` line. Reproduce:

```bash
cd SCRIP
python3 scripts/corpus_suite_harness.py extract ../corpus/tests/snocone/ALL.sc ../corpus/tests/snocone/ALL.ref \
  simple_output_124 /tmp/e.sc --out-ref /tmp/e.ref
./scrip --run /tmp/e.sc </dev/null       # parse error
./scrip --compile /tmp/e.sc </dev/null   # parse error
```

## ROOT CAUSE — confirmed, not guessed

`#` is not a comment introducer in SCRIP's Snocone at all. Two independent pieces of evidence agree:

1. **The lexer.** `src/parsers/snocone/snocone_lex.c:183`: `if (PEEK(0) == '#') goto S_OP_POUND;` — `#` lexes
   as an **operator token**, matching `.github/ARCH-LANGUAGES.md`'s own operator table ("Undefined binary
   operators (available for `OPSYN`): `&` `@` `#` `%` `~`", priority 7, left-assoc) — `#` is a **reserved
   OPSYN slot**, not whitespace-equivalent comment syntax.
2. **The spec.** `ARCH-LANGUAGES.md`'s own `## Comments` section (line 575-578) names exactly two forms:
   `// to end of line` and `/* ... */` block comments. It does not mention `#` anywhere. Both forms work,
   verified directly (leading, trailing, and block, native `--run`):
   ```
   // a line comment          -> OUTPUT = 'ok';  prints ok, rc=0
   /* a block comment */      -> OUTPUT = 'ok';  prints ok, rc=0
   OUTPUT = 'ok'; // trailing -> prints ok, rc=0
   ```

So `simple_output_124`'s premise ("# is also a line-comment introducer") is not merely unimplemented, it
contradicts the language's own current spec — `#` was never a comment character in this dialect; it is an
operator slot. Minimal ablation (this session, not guessed): comment-with-`#` fails identically whether the
`#` line is first, last, mid-file, or trailing on a code line — always a parse-time failure, never a codegen
one, consistent with "reserved operator token used where the grammar expects a comment" rather than a
lowering bug. One two-consecutive-`#`-lines variant produces a plain "syntax error" (line 2) instead of the
single-`#` variant's more surprising `FATAL lower_snobol4 ... SN4-REPL slice 1: replacement subject must be a
plain variable` — both are the SAME root cause (an `S_OP_POUND` token appearing where an expression is
expected), just different downstream failure shapes depending on what garbage token stream results; did not
chase why the single- and double-`#` shapes diverge downstream, since parsing already failed either way and
that's a cure-level dig, not a census one.

## WHY THIS WASN'T IN THE 7/206 COUNT

Unknown — did not have time to bisect whether this regressed since the 2026-09-03 measurement (SCRIP
`b625b9c1`) or was always red and missed by that finding's sampling (it printed "~20 sampled fail lines," not
an exhaustive per-entry dump). Worth a `git bisect` on this one entry if someone wants the exact landing
commit; not attempted here.

## RECOMMENDATION, NOT A CURE

Two honest options, HQ's call: (a) delete/rewrite `simple_output_124` to test the REAL comment syntax
(`//`/`/* */`) instead of a false premise, since `#`-as-comment is not a gap to fill, it's a wrong test — `#`
is correctly reserved for `OPSYN` and teaching the lexer to ALSO treat it as a comment character would create
an ambiguity the language doesn't have today; or (b) if `#`-as-comment is actually wanted (Koenig's 1985
original uses it, and the self-hosting `snocone.sc` might too — not checked), that is a language-design
decision belonging to Lon/ceo, not something to infer from one 2026-08-27-vintage fixture whose own premise
may itself have predated the OPSYN reservation. Did not touch the fixture or the lexer — outside this row's
scope (walker, not cure) and this is exactly the kind of call FINDING-2026-09-03-...-Class-A (the `procedure`
keyword gap) left to whoever cures it, for the same reason.

## FOR THE LADDER (this row's own use of this finding)

`config/LADDER.tsv` rung10 (`lexical_conventions`) cites this as the rung's REFUSE case (the task GOAL
requires at least one construct-must-REFUSE witness per rung) rather than inventing an artificial one — a
real, verified, currently-true refusal is stronger evidence than a contrived one.
