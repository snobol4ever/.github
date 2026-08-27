# FINDING 2026-08-27 seat08 — parser-fixture AST oracles have drifted from current `--dump-ast` output in at least two languages; one language's own gate script was silently masking the true scope

## Context
Working `corpus-suites-consolidation` (row still held by seat08), scoping the "all-languages
extension" (icon/prolog/raku/pascal/rebus/snocone, per s272's scope extension). The task's format
(B) — banner-delimited multi-line blocks — was already named for the five parser-ladder families
(icon/parser 306, raku/parser 244, prolog/parser 158, rebus/parser 144, snocone/parser-fixtures
134 — those are FILE counts, i.e. pairs×2; actual pair counts are half) before any language work
started. Format B needs no per-language statement-join logic (unlike format A), so a parser-ladder
family looked like the lowest-risk place to pilot the harness's language generalization. Before
converting anything, I checked whether the target family's underlying oracle is actually green
today — byte-equal-or-no-delete refuses to convert a non-green original, so a family's health
determines whether a pilot is even possible, not just how risky it is.

## What was found

**Snocone `corpus/tests/snocone/parser-fixtures/` (67 `.sc`/`.ref` pairs, graded by
`scripts/test_snocone_parser_fixtures.sh` via `scrip --dump-ast` diff):** the script's own header
comment claims `Gate: PASS=67 FAIL=0`. Running it produced exactly one line of output and stopped
(`FAIL arith_add`, no summary line, no other verdicts). Root cause: `set -euo pipefail` at the top
of the script, combined with a bare `diff <(...) <(...) | head -12` diagnostic line in the FAIL
branch. `head` exits 0 (it read fewer than 12 lines successfully); `diff` exits 1 whenever the
inputs differ. Under `pipefail`, bash reports the pipeline's status as the *rightmost command that
exited non-zero* — here, `diff`'s 1, since `head`'s 0 doesn't count as non-zero — so the pipeline
reports 1, and `set -e` kills the script immediately after printing the very first failing
fixture's diff. The script has therefore never reported a real PASS/FAIL/SKIP tally for any run
containing at least one failure, and its exit code (whatever a caller sees) was never earned by
actually grading all 67 — it's an artifact of which fixture alphabetically sorts first among the
failures. A second, independent trip-hazard exists on the line above (`actual=$(timeout 8 "$SCRIP"
--dump-ast "$sc" 2>/dev/null)`): under `-e`, a command-substitution assignment whose command exits
non-zero also aborts the script — so a fixture that makes `--dump-ast` itself exit non-zero (crash
or hard parse error, not just a wrong-but-successful dump) would kill the run even earlier, before
any diff is printed at all.

Working around the bug with an independent, unpiped sweep of all 67 pairs: **PASS=8, FAIL=59.**
Sample (`arith_add.sc` = `x = 1 + 2;`):
```
expected: (STMT :eq :subj (TT_VAR x) :repl (TT_ADD (TT_ILIT 1) (TT_ILIT 2)))
actual:   (STMT :subj (TT_ASSIGN (TT_VAR x) (TT_ADD (TT_ILIT 1) (TT_ILIT 2))))
```
The current compiler wraps assignment in a `TT_ASSIGN` node; the `.ref` files predate that shape
and still expect the older `:eq`/`:repl`-field encoding directly on `STMT`. This pattern (or
something like it) looks consistent across most of the 59 — not independently verified fixture-by-
fixture here (out of this row's scope), but the failures are not scattered noise; `arith_*`,
`assign_*`, `augmented_*`, `if_*`, `scan_*`, `switch_*`, `while_*`, `for_*`-class fixtures all fail,
which is most of the file list.

**Icon `corpus/tests/icon/parser/` (153 `.icn`/`.ref` pairs):** no script anywhere under
`SCRIP/scripts/` exercises this directory at all (`grep -rl "icon/parser" scripts/*.sh` finds
nothing but an unrelated IPC sync-monitor tool that merely mentions the path). It is completely
ungated — the same "confirmed zero runner" shape already on record for
`prolog-parser-corpus-vacuous-gate-422-files` (a sibling task, unrelated content, same defect
class: a corpus directory with no runner, or a runner that doesn't really run). An independent
`--dump-ast` sweep of all 153 pairs: **PASS=0, FAIL=153 — all of them.** Sample (`atom_str.icn` =
`procedure main(); "hello"; end`):
```
expected: (STMT :subj (TT_PROC_DECL main (TT_VAR main) (TT_VLIST) (TT_PROGRAM (TT_QLIT "hello"))))
actual:   (STMT :subj (TT_PROC_DECL (TT_VAR main) (TT_VLIST) (TT_PROGRAM (TT_QLIT "hello"))))
```
The `.ref` expects a redundant bare procedure-name atom (`main`) immediately inside `TT_PROC_DECL`,
before the `(TT_VAR main)` node that already carries the same name; the current compiler no longer
emits it. Since nearly every Icon program's top-level shape is a `procedure ... end` declaration,
one systematic format simplification plausibly explains all 153 failures at once — not confirmed
fixture-by-fixture, but the uniform 0/153 (vs. Snocone's partial 8/67) is consistent with "every
fixture hits the same node-shape change" rather than 153 independent defects.

## Neither number says whether the COMPILER is wrong or the FIXTURES are stale
Both look like a deliberate simplification of the `--dump-ast` node shape (dropping a field that
duplicated information already present elsewhere) rather than random breakage — but that is a
guess from the shape of the diffs, not a verified conclusion. Deciding "regenerate the `.ref`
files" vs. "the new AST shape is itself a regression" is a correctness call belonging to whoever
owns Icon/Snocone AST design, not to a file-format-consolidation row. Regenerating 59+153 stale
oracles without that call would be exactly the "hand-transcription" this project's conversion law
(`corpus_suite_harness.py`'s own docstring: byte-equal-or-no-delete, "conversion is mechanical,
never hand-transcription") exists to prevent, applied to test oracles instead of test inputs.

## Relationship to today's other Snocone findings (different corpus, same day)
`FINDING-2026-08-27-seat09-snocone-crosscheck-runner-rewired-...` and
`FINDING-2026-08-27-seat07-snocone-crosscheck-35-remaining-fails-classified-...` are about a
*different* Snocone corpus — the 28-dir rung-ladder crosscheck (161+20 files, execution-graded,
not `parser-fixtures/`'s narrow AST-dump set) — so this is not a duplicate. But taken together:
today produced three independent, previously-invisible Snocone/Icon correctness-adjacent findings
in one day (this one; seat09's dead-runner-plus-52-gaps; seat07's while/for-loops-don't-iterate-
past-the-first-pass headline bug). Snocone in particular is having an unusually active day of
correctness archaeology. Converting any Snocone family's file *format* right now, while its
correctness is this actively in flux, risks the same "moving denominator during an active
investigation" hazard the task's own INTERLOCK section names for the restore-prezeta rows — even
though `parser-fixtures/` is not literally one of those rows.

## What was fixed here (mechanical, low-risk, verified — in scope to just do)
`scripts/test_snocone_parser_fixtures.sh`: added `|| true` after both trip hazards (the `actual=`
assignment and the `diff | head` line), so a failing fixture is recorded and the loop continues
instead of the whole script dying under `-e`/`pipefail`. Also de-pinned the stale `Gate: PASS=67
FAIL=0` header comment (a probe should assert `FAIL=0` over its own printed total, never a specific
pinned number — RULES.md FACT RULE on this exact shape). Re-ran post-fix: correctly reports
`PASS=8 FAIL=59 SKIP=0`, exit 1 — matching the independent manual sweep exactly. Nothing else in
the tree references this script (`grep -rl` finds only the file itself), so there is no caller
whose behavior could depend on the old silent-early-exit shape. Not wired into `make test` or any
`test_gate_*` — this fix makes the script honest, it does not newly gate anything.

## What was NOT done (deliberately, out of this row's scope)
- No `.ref` files regenerated, for either language — that's the correctness call flagged above.
- No new gate script written for Icon's `corpus/tests/icon/parser/` — it needs one (mirroring
  `test_snocone_parser_fixtures.sh`'s shape, now that that shape is honest), but authoring it is a
  separate, non-trivial piece of work, not a byproduct of this investigation.
- No formal queue row minted for the drift triage itself — following seat09's own same-day
  precedent on their sibling finding ("worth minting — not minted this session"), leaving the mint
  decision to whoever is positioned to own Icon/Snocone AST-shape correctness. Flagged to hq_C
  (correctness owner) via `s4e_msg.sh send` instead.

## Effect on corpus-suites-consolidation
The all-languages extension should not attempt Snocone's `parser-fixtures/` or Icon's `parser/` as
a pilot family until the above triage lands (or at minimum until someone with standing confirms
which side — compiler or oracle — is correct). Every language checked so far during this scoping
pass had a live blocker of some kind: Prolog (ambiguous "closed" status plus a confirmed-vacuous
corpus-wide parser gate plus several open correctness-crash rows), Pascal (multiple open bugs
including empty-corpus-false-pass on both modes — the same defect *class* as this finding, a third
independent instance today), Rebus (corpus confirmed 100% broken to compile), Snocone (this
finding, plus the unrelated-but-concurrent crosscheck churn above). Raku was not yet checked. The
harness-generalization design needed to support format-B conversion for any of these (per-language
file extension, per-language banner comment-open/close, an `ast`-dump grading mode alongside the
existing `m3`/`m4`) is straightforward to add to `corpus_suite_harness.py` as new, additive code
paths — not yet written, since writing it against a family that turns out to be 12% green isn't a
real validation of it. Next session picking this up should re-check Raku's parser family's health
first (same technique as this finding: an independent manual sweep, not trust in a script's exit
code alone) before committing engineering time to the harness changes.
