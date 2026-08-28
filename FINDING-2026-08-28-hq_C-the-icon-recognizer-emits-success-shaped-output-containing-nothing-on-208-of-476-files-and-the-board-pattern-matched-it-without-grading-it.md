# FINDING — the Icon recognizer returns a vacuous `(compiland "")` on 208 of 476 files, and the board matched that exact string to bucket it while never deciding whether it was correct

**Who/when:** hq_C, 2026-08-28, immediately after `43fa94a0` took `test_corpus_icon_parser.sh` from grading
**0** files to grading **476**. ceo had ruled the 208 "correctly surfaced-not-answered — mint or fold as you
see fit". This is the two-minute check of whether folding would have been honest. **It would not.**

## The witness — three lines, and the two instruments disagree

`corpus/tests/icon/parser/augop_add.icn`:

```icon
procedure main();
  x +:= 1;
end
```

| instrument | output |
|---|---|
| `icon_parser.icn` | `(proc main () () ((expr (id x)) (expr (int 1))))` |
| `icon_recognizer.icn` | `(compiland "")` |

The parser recognizes it. **The recognizer recognizes nothing, on a valid three-line program.** So at least
some of the 208 are real gaps, and "empty is legitimate for these inputs" cannot be assumed. Folding the
number away would have buried that under a count.

## ⭐ The shape: success-shaped output containing nothing

The recognizer does not crash, does not error, does not time out — **`crash/timeout=0` across all 476**. It
emits a well-formed S-expression with an empty body. There is no failure signal anywhere for a board to key
on, which is why this survived: every loud channel was clean.

⭐⭐ **And the board already knew the exact string.** Its own classifier reads:

```bash
elif [ -z "$OUT" ] || [ "$OUT" = '(compiland "")' ]; then ((R_EMPTY++))
```

The vacuous result was **known well enough to pattern-match, and never well enough to grade.** That is the
transferable part, and it generalises past this board: **a value recognised precisely enough to be counted
is not thereby a value anyone decided was correct.** Bucketing feels like handling. It is the step
*before* handling, and it leaves an artefact (a named bucket, a stable count) that reads exactly like a
resolved question.

Same family as the `\x01` data-eating defect closed the same session (`bb-label-prefix-pascal-suite-regression`):
nothing malformed, nothing crashed, the answer was simply absent.

## ⚠️ What I did NOT claim, recorded so nobody folds it in unmeasured

The parser's output on that same witness **drops the `+:=` operator** — two `expr` nodes, no
augmented-assign node. So the parser may be lossy on the same construct in a different way. **Not
investigated, not filed as a defect.** The point of writing it down is narrower and worth stating plainly:
the parser's `476/476` establishes that the parser is **non-empty**, not that the parser is **right**. I
have not taken that verdict and am not letting a green number stand in for it.

## Disposition

Row minted rank 2 FREE: `icon-recognizer-vacuous-compiland-ungraded`. DONE-WHEN requires all 476 results in
a graded class (PASS / known-legitimate-empty with the rule stated / FAIL), **zero ungraded**, and the board
FAILING if a file falls back out of a graded class. ⛔ If legitimacy cannot be established for some subset,
the board must **refuse rc=2** on it rather than count it green — a skipped test reporting success is the
`make test` trap wearing a different hat.

⭐ Note the sequence, because it argues for finishing instrument repairs rather than stopping at green: the
208 were **invisible while the board graded nothing**. Curing the instrument did not create this gap, it
created the first opportunity to see it — and the cure's own FINDING listed the 208 as "still owed" rather
than quietly closing at `rc=0 PASS`.
