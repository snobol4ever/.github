# FINDING 2026-09-05 (seat01): the ladder walk has no methodology for a "book-named failure case" that is a fatal interpreter ERROR, not a pattern-match failure -- hit twice independently in one session, will recur at rung24

Written 2026-09-05 19:1x CDT. Surfaced while minting rung12's `FENCE(P)` form
(row `snobol4-ladder-every-feature-in-isolation-with-variations`, hq_P lane).
Not fixed -- flagged for whoever next wants fatal-error-code coverage as its
own methodology question.

## CLAIM
The ladder recipe asks each rung to cover "every operator spelling, argument
shape, boundary and failure case the book names." For most constructs
"failure case" means a pattern-match `:F()` branch, which the existing
byte-exact `.ref`-comparison methodology handles perfectly (every witness so
far does exactly this). But several primitives have a book-named failure
case that is instead an **uncaught fatal interpreter ERROR** -- the program
does not continue, it halts with a diagnostic banner. That shape has no
working home in the current methodology, and this is not a one-off: it has
now surfaced independently in two adjacent rungs in one session.

## EVIDENCE
- **rung12** (this session): `FENCE(pattern)`'s own formal definition (SPITBOL
  manual Ch19 "SPITBOL Functions" p.222-223) is paired with ERROR 259 ("fence
  argument is not pattern") in the manual's own error appendix. Oracle-verified
  the trigger precisely: `FENCE(5)` does NOT error (a scalar silently coerces
  to a literal-match pattern, `DATATYPE` reports `PATTERN`); `FENCE(ARRAY(3))`
  DOES raise it. A real, book-named, oracle-confirmed boundary case.
- **rung13** (seat15, same file, pre-existing NOTE cell, found independently
  before this session): "the Error #239 case (indirecting through an
  undefined name yields the null string, which is not a valid variable name,
  p.82) deliberately excluded from this base witness -- a fatal runtime error
  would halt the program before later statements run." Same shape, same
  reason for not minting, arrived at independently.
- **Why the existing methodology cannot just absorb it as another witness,
  checked rather than assumed**: grepped the ENTIRE snobol4 suite
  (`corpus/tests/snobol4/ALL.ref`, 1881 entries after this session) for any
  ERROR-banner-shaped content or the oracle's stats-footer text
  (`execution time msec`) -- zero hits, in either direction. No existing
  witness anywhere in this corpus uses a fatal-error transcript as its
  reference. Captured the raw oracle output for a triggering case directly
  (`sbl -bf` on `X = FENCE(ARRAY(3))`): the banner includes a per-run
  `execution time msec` and `memory used/left` footer (non-deterministic
  across runs/machines), and its exact wording has no reason to match
  scrip's own error-reporting text byte-for-byte even when both correctly
  detect the identical fault -- the whole point of this corpus's grading
  model is byte-exact behavioral comparison, not error-string-format parity.
- **rung24 will hit this at scale, not as an edge case**: rung24
  ("primitive patterns complete, every SPITBOL primitive pattern as a
  construct" -- LEN/TAB/RTAB/POS/RPOS/REM/ANY/NOTANY/SPAN/BREAK/BREAKX/BAL/
  ARB/FENCE/etc.) is exactly the census of primitives whose manual entries
  are heaviest with argument-type and boundary ERROR codes. Whoever opens
  that rung will hit this gap repeatedly, not once.

## WHY THIS ISN'T A QUICK FIX (AND WHY NOT MINTING WAS THE RIGHT CALL BOTH TIMES)
A workable methodology for this class of form needs a decision this row's own
SCOPE (isolation forms, byte-exact `.ref`) does not make: whether to (a)
match on exit-code + a normalized/truncated prefix of the error banner
(stripping the non-deterministic footer and any oracle-vs-scrip wording
difference), (b) catch the condition from *inside* the program instead of
letting it go fatal (SPITBOL's own tools for this, if any, are unread as of
this Finding), or (c) accept these forms as permanently out of the
byte-exact model and track them in prose only (LADDER.tsv NOTE cells, as
both rungs already do). Each option is a real design choice with test-harness
consequences beyond one rung -- worth a ruling, not a rung's improvisation.

## LESSON FOR THE STANDARD
"The book names a failure case" is not the same claim as "the book names a
pattern-match failure." A recipe step written against the common case
(:S()/:F() control flow) silently assumes it every time it says "failure
case," and two independent sessions found the same uncovered shape from two
different primitives before anyone said so out loud. Worth a line in the
ladder recipe itself once a ruling lands, so a third rung doesn't rediscover
it a third time.
