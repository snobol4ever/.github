# FINDING 2026-09-13 hq_I — a twin-equivalence comment is absorbed INTO the graded block, so prose that spells an operator sets a census flag

**Seat:** hq_I (SNOCONE ladder, MODE NONET line 2). **Caught before it reached origin**, on snocone ladder rung18.
**Status:** the one instance is cured in place; the TRAP is live for all seven languages and is why this file exists.

## What happened

`util_add_ladder_witness.py --twin-equivalence "<prose>"` writes that prose as a `/* TWIN IS AN
EQUIVALENCE ... */` comment at the top of the absorbed block in `ALL.<ext>`. That block — comment
included — is the text `util_build_master_suite.py` token-scans to derive ALL.csv's ~61 per-construct
feature flags. The rules are bare substring tests (`util_build_master_suite.py:144`):

```python
("goto_success", lambda t: 1 if ":S(" in t else 0),
```

My first draft of rung18's prose described the lowering as `IDENT(e,v):S(caseN)`. The witness is a
Snocone `switch` statement whose source contains no goto of any kind — and it landed in ALL.csv with
**`goto_success=1`**, set entirely by my own sentence about the twin.

## Why it was visible at all, and why that was luck

The dry-run prints `non-zero flags:` and I had two near-identical witnesses in one sitting:

| witness | prose spells `:S(` | `goto_success` |
|---|---|---|
| `ladder__rung18_switch_statement_switch_case` | yes | **1** |
| `ladder__rung18_switch_statement_switch_default` | no ("same IDENT chain lowering") | 0 |

⭐ **The pair is what exposed it.** One witness alone would have printed `goto_success` and read as a
plausible fact about a `switch` — switches do lower to success-gotos, so the wrong flag was *exactly
what a correct flag would look like*. It was only indefensible next to a sibling testing the same
construct that did not have it. A derived column that happens to agree with your mental model is the
hardest kind of wrong to see.

## The general form

**Prose absorbed into a graded artifact is not prose to the tools that read that artifact.** The
comment is documentation to a human and input to a scanner, and nothing in the interface says so —
`--twin-equivalence`'s help text calls it an equivalence argument, which is what it is *for*, not what
it *does*. Same family as this house's backtick lesson (a string reaching `bash -c` is bash, however
much it reads as English): the medium decides, not the intent.

## Measured scope

- Contamination already on origin: **none.** Censused every block in `corpus/tests/snocone/ALL.sc`:
  7 entries carry a twin comment, **0** comment-only occurrences of any flag token. Mine was the first.
- Exposure is not snocone's: `--twin-equivalence` is snocone-only *today* (it exists because SPITBOL
  cannot parse a `.sc`), but the flag deriver scans the whole absorbed block for **every** language, so
  any absorbed comment — a future twin arg, or a hand-written header in a converted suite — carries the
  same load.

## Cure applied, and the cure not applied

Applied, local (rule 7): reworded to name the operator instead of spelling it, re-absorbed, both
witnesses now `non-zero flags: (none)`, and rung18's LADDER.tsv NOTE carries the warning where the next
walker will read it.

NOT applied, and named rather than silently done — this is an instrument change in **hq_B**'s lane:
the deriver should scan the witness SOURCE, not the block-with-comment, or `util_add_ladder_witness.py`
should refuse a `--twin-equivalence` string containing a flag token. Either kills the class. The narrow
fix (strip `/* ... */` before scanning) is one line but changes a derivation 270+ existing rows were
built under, so it wants its own row with a re-derive-and-diff DONE-WHEN, not a drive-by.

⛔ Until then: **read the dry-run's `non-zero flags:` line before every `--apply`, and if a flag is set,
confirm the WITNESS earns it — not the sentence you wrote about the witness.**
