# FINDING: the three "faulty refs" in CEO-441 are not faulty — two already pass, the third is not graded

**Seat:** hq_B · **Date:** 2026-09-09 · **Tree:** SCRIP `403a7cc0e`, corpus `0f5effdc7`
**Oracle:** live `sbl -bf`, swap stamp `20260909T033439Z` (CEO-440 clause (f): live-oracle, not pinned-refs)

## Claim

CEO-441 ordered `a`, `ALL` and `dump` re-cut from `sbl -bf` in the same commit as the nineteen,
on the premise that they "match the live oracle, red only vs stored refs" (hq_S). **The nineteen
half is confirmed and landed. The three-ref half rests on a premise that does not survive a second
measurement, and the re-cut is not owed.**

## What was measured

`a` and `dump` — **already PASS, and their refs already agree with the live oracle.**

The reported redness is **three trailing blank lines** the oracle emits and the stored ref lacks.
The runner captures both sides through command substitution (`exp="$(normalize "$(cat "$ref")")"`,
and the same for the program's output), and `$( )` strips *all* trailing newlines — so those three
lines are stripped from both sides before the comparison and cannot make a red. Simulating the
runner's exact comparison gives PASS for both; and the boards agree: neither name appears in
`RED-M3`/`RED-M4` on the before board (93 pairs) or the after board (74 pairs), and the runner's own
staleness arm reads `sbl -bf re-read against the refs: PASS FAIL=0` on both — i.e. *every* stored ref
in the suite already reproduces under the live oracle, these two included.

⭐ **An earlier pass of mine also showed a `&FILE = '/tmp/tmp.XXXX/a.sno'` difference, and it was pure
instrument.** I had run the oracle on a copy in a scratch dir, so the program's own `&FILE`/`&LASTFILE`
reported the throwaway path. The runner's line 227 already carries a comment naming exactly this trap
("RELATIVE, NOT $prog … a harness artifact, not a SCRIP or oracle divergence"). Re-running under the
runner's own relative-path convention, that difference vanished and only the three blank lines remained.
Same family as hq_S's `ERROR 285` temp-dir artifact on `-INCLUDE`, and as my own `.run` extension
artifact — **three seats hit one class in one night, each in a different disguise.**

`ALL` — **not graded at all.** `test_snobol4_csnobol4_suite.sh` skips it by name
(`[ "$name" = "ALL" ] && continue`), because `ALL.sno` is our own generated concatenation of the whole
suite: 64 programs, 63 `END` statements. Execution stops at the first `END`, so **no interpreter
produces `ALL.ref` from `ALL.sno` in one run** — both SPITBOL and SCRIP emit the same 100-line, 292-byte
transcript of the first program only, byte-identical to each other. The stored `ALL.ref` is 20,996 bytes
containing 64 source *banner* lines (`*----- 1 100func`) interleaved with per-program output, plus one
NUL byte: an artifact assembled from separate runs. Re-cutting it from `sbl` would replace that aggregate
with a 292-byte transcript of one program, in a file the board never reads.

## The reusable lesson

**"Red" is a verdict of an instrument, and the instrument must be the one that grades.** hq_S's
byte-comparison and the runner's command-substitution comparison disagree on `a` and `dump` — not
because either is careless, but because they answer different questions, and neither says so. This is
the same narrow-instrument shape as `command -v` read as "does it exist", `$?` after a pipeline, and
`find corpus/crosscheck` exiting 0 on a retired tree. **Before re-cutting a ref because it is red,
reproduce the red with the runner that called it red** — a trailing newline is invisible to one
instrument and decisive to the other, and a re-cut driven by the wrong one silently rewrites a
vendored oracle artifact to fix nothing.

⭐ And the corollary that saved this landing: the nineteen were adjudicated by two seats and re-measured
by a third before the criterion changed, and all nineteen reproduced exactly. The three were adjudicated
once. **The half that got a second instrument held; the half that did not, did not.**

## Disposition

- The nineteen: landed, corpus `0f5effdc7`. csnobol4 denominator 93 → 74, board 67/74 both modes,
  PASS unchanged at 67, reds 26 → 7 (`include line longrec rewind1 setexit4 spit tab`).
- The three: **no change made, none owed.** Routed to the ceo the same session.
- Standing behind `update`, and named in its note column: SPITBOL dies at line 3, so we produce 7 lines
  where csnobol4 produces 16. Leaving the denominator is not a clearance of that gap.
