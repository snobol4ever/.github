# FINDING — `kalah-crlf-parse-failure` cured by corpus normalisation; its own DONE-WHEN was measured passing on the unfixed tree

## THE RESULT
`corpus/packages/snobol4/aisnobol/KALAH.sno` (and 7 sibling `.sno` files in the same package) had CRLF line
endings. STEP 1 of the row asked a single decisive question: does the oracle tolerate CRLF? **No.**
`/home/resources/x64/bin/sbl -bf`, run unmodified against the CRLF file, reports **480× `ERROR 230 -- syntax
error: illegal character`** — one per source line, each pointing at the exact column of the trailing `^M`
(e.g. `KALAH.sno(57,13)` on `&ANCHOR	= 0^M`) — plus one cascade `ERROR 214` once parser state desyncs, ending
`No END statement found in source file(s)`, rc=1. Per the row's own ruling text, an oracle refusal makes
corpus normalisation the legitimate cure, not a SCRIP lexer change. Cured: `sed -i 's/\r$//'` on all 8 files
in the package (ATN, BUILDLIB, ENDING, HSORT, KALAH, SIR, TEST, WANG — all 8 carried CRLF, not just the named
file). SCRIP `error:` counts before → after: 79→2, 12→0, 16→0, 19→0, **39→0 (KALAH, this row's target)**,
12→1, 11→3, 12→2. Verified the diff is line-ending-only two independent ways: `git diff
--ignore-space-at-eol` is empty, and `git show HEAD:<f> | sed 's/\r$//' | diff -` against the new content is
identical, for all 8 files. Pushed `corpus` `e63fb055a` (rebased cleanly onto 8 upstream commits; re-verified
0 errors and DONE-WHEN still passing on the rebased tree per the REBASE-BASELINE COROLLARY before trusting
the pre-rebase measurement).

## ⛔⛔ THE ROW'S OWN DONE-WHEN WAS DOUBLY VACUOUS, AND IT WAS MEASURED PASSING ON THE BROKEN TREE
Before touching anything, per RULES.md's TWO-PART PROOF duty, I ran the row's existing DONE-WHEN verbatim
against the still-broken file:
```
test -f corpus/packages/snobol4/aisnobol/KALAH.sno && test -x SCRIP/scrip && ! ( cd corpus/packages/snobol4/aisnobol && timeout 30 SCRIP/scrip --dump-ast KALAH.sno < /dev/null 2>&1 | grep -qiE "parse error|cannot open" )
```
**It exited 0 — DONE — on the completely unfixed file.** Two independent bugs, either alone sufficient:
1. **Path bug.** `SCRIP/scrip` is a relative path evaluated *after* the `cd` into
   `corpus/packages/snobol4/aisnobol`, where no `SCRIP/` directory exists. `timeout` printed `failed to run
   command 'SCRIP/scrip': No such file or directory` and exited 127 — **the compiler never ran, at all,
   ever, since this DONE-WHEN was authored.**
2. **Pattern bug, independent of (1).** Even with the path fixed, SCRIP's actual message is `error:
   unexpected char`, which contains neither literal substring the grep looked for (`parse error`, `cannot
   open`).
Either bug makes the grep find no match, and the `!` wrapper reports success. This is the exact "instrument
cannot distinguish MEASURED-AND-CLEAN from NEVER-RAN" shape RULES.md's INSTRUMENT LAWS name, and it evaded
`s4e_msg.sh done`'s own vacuity probe because that probe deliberately skips any criterion containing `/` or
`$` (a path or a variable) — this one names both, for a legitimate reason, so the probe could not have caught
it either. **Repaired:**
```
R="$PWD"; test -f "$R/corpus/packages/snobol4/aisnobol/KALAH.sno" && test -x "$R/SCRIP/scrip" && ! ( cd "$R/corpus/packages/snobol4/aisnobol" && timeout 30 "$R/SCRIP/scrip" --dump-ast KALAH.sno < /dev/null 2>&1 | grep -qiE ": error:|cannot open" )
```
`R="$PWD"` is captured before any `cd`, and the pattern now matches SCRIP's real wording. Two-part proven,
neither arm assumed: replayed against the pre-fix blob (`git show HEAD~1:...` into a scratch dir) → **exit 1,
correctly refuses**; against the fixed tree → **exit 0, correctly passes**. `s4e_msg.sh done
kalah-crlf-parse-failure` then computed the same verdict independently and closed the row.

## WHAT WAS DELIBERATELY NOT TOUCHED, AND WHY
- `ATN.sno` (2), `SIR.sno` (1), `TEST.sno` (3), `WANG.sno` (2) still carry a handful of SCRIP parse errors
  after the CRLF fix — confirmed CRLF-unrelated (0 `\r` bytes remain in any of the 8). Pre-existing, never
  visible before because the CRLF error fired first on every one of these files. Not this row's GOAL ("has
  never been able to PARSE `KALAH.sno`" — specifically); flagged here rather than filed as new rows, since I
  have not root-caused any of the four.
- With KALAH.sno now parsing, the oracle gets further and hits `KALAH.sno(68) : ERROR 160 -- inappropriate
  file specification for output` at `OUTPUT(.SHADOW,1)`, rc=0. A runtime I/O-association defect, pre-existing
  (content diff before/after this fix is empty — see above), newly *visible* rather than newly *caused*. Not
  a parse defect, not investigated further, named here so it isn't mistaken for a regression from this
  commit by whoever meets it next.

## BONUS: CLAUDE.md's `x64/` PARAGRAPH WAS STALE AND ACTIVELY MISLEADING FOR THIS ROW'S OWN STEP 1
`/home/claude12/CLAUDE.md`'s Workspace map still described the s255-era oracle model (HQ-only clone at
`/home/claude`, `S4E_ASSETS` fallback for numbered seats). RULES.md's s259 (asset consolidation) and s261
(*"Ensure that no root have x64. Everyone must share." / "Do not use symlinks."*) rulings deleted that
fallback — verified on disk: `/home/claude/x64/bin/sbl` absent, `/home/resources/x64/bin/sbl` present, and
`lib_oracle_flags.sh`'s `sbl_correctness_bin()` resolves only the latter, refusing loudly rather than falling
back. Corrected the digest paragraph to match and to point at the resolver function instead of a hand-rolled
path — this is also why this row's own STEP 1 measurement above used `sbl_correctness_bin()` rather than
assembling `x64/bin/sbl` by hand.

## TRANSFERABLE PART
A DONE-WHEN is itself an instrument and is subject to the same duty as any board or gate: prove it can say
NO before trusting that it ever says YES. This one was authored inside a `cd` subshell with a
path meant to resolve from the ORIGINAL cwd — a natural mistake, since the surrounding prerequisite checks
(`test -f`, `test -x`) *do* correctly run before the `cd` and read fine on inspection. A criterion that
"looks right" and has never been run against known-broken content is not a criterion, it is a hope.
