# FINDING — LOWER L-4/061 closed; fix found already uncommitted in the tree, provenance unknown, independently verified before landing

**Session:** Claude Sonnet 5, 2026-08-13. SCRIP `6d804efd` (fix) + `f25a5448`/artifact commits (regen).

## The discovery

Orientation cloned the standard three repos plus `x64` (PLAN.md step 1b). `git status` on a
fresh clone should be empty. It wasn't: `src/emitter/emit.cpp` had one modified, unstaged hunk.
`git blame -L` on the changed line returned `Not Committed Yet`. No `.github` cursor entry
anywhere referenced it.

`git diff` showed the change was a complete, working implementation of exactly what s45's
LIVE CURSOR had proposed and left undone: at the `g_zd_read[k]` staging site (`emit.cpp`
~line 2725), backward-scan from consumer to producer and add 32 for every run-local
`IR_MATCH_BEGIN` crossed (gated by the identical predicate `bb_match_begin.cpp`'s own `hfc()`
uses), summed across every head found. The replaced comment it displaced cited a `zd_ud`/`zdh`
formula that — per s45's own finding — exists nowhere in the codebase. The new comment
explicitly corrects s45's hand-derived deficit (48 = 32+16) to the gdb-measured true value
(32 flat), and cites verification "on a real linked mode-4 binary, not hand-derived" at
N=0 and N=2 on the `061` witness.

No commit, no author, no cursor entry, no FINDING. Just present.

## What I did about it

Did not assume either extreme — did not treat "looks plausible and well-commented" as
sufficient, and did not discard it as untrusted. Verified it as if I were reviewing someone
else's unreviewed patch, because that is what it was.

**Baseline reproduction (`git stash`, rebuild):** confirmed the committed HEAD (`5547de99`)
reproduces s44/s45's claim exactly — `crosscheck/capture/061_capture_in_arbno.sno` under `scrip
--run` prints nothing, rc=0. Oracle (`x64/bin/sbl` — corrected from an earlier path error of my
own, see below) and scrip m3/m4 all print `a\na\na` with the fix applied; the three-way is
byte-identical.

**Gate A/B (stash-based, own HEAD, before commit):**

| suite | without fix | with fix |
|---|---|---|
| `crosscheck/capture` (9) | 8/9 (`061` FAILs) | 9/9 |
| `crosscheck/patterns` (78 w/ `.ref`) | 61/78 | 61/78 — byte-identical set |
| `probe/bb` (166) | 160 pass, 5 pre-existing regressions `{D12,D13,H31,X01,X10}` | identical |
| l3 board (14) | 14/14 | 14/14 |

Only `061_capture_in_arbno` moves. Zero collateral anywhere else tested.

**Codegen-touched ⇒ regen required (RULES.md step 4).** Ran benchmark/feature/demo `.s`
regen per the mandated order. Blast radius is large — `test_string.s` alone changed ~6800
lines — because the fix's own comment is honest about its scope: it is "the ONE authority
for every ZD-armed cross-head read in the tree." A large `.s` diff is not evidence of a
behavior change; the offsets shift for any node with a cross-head `MATCH_BEGIN` in scope,
whether or not that particular program's correctness depends on it.

**Closed the loop on the two places a large diff could hide a real regression:**
- `board_sno15_ident.sh` (the sanctioned demo instrument) — still `2/15 TRI-IDENTICAL`
  (claws5-match, claws5-match-fence), matching the long-documented floor exactly. The 13
  failures are the already-named FEATURE-gap / arena-exhaustion / wild-rbx classes
  (GOAL-SN4-HOME.md §DEMOS) — unrelated mechanisms, unmoved.
- `test_string` (L-5's own open witness, `crosscheck/library/test_string.sno`) — confirmed
  byte-identical against a **true** pre-fix build via `git worktree add ... HEAD~1` (the
  `git stash` A/B above stopped being meaningful for this check once the fix was committed).
  **L-5 is not incidentally fixed. It remains open, separate, unconvicted**, exactly as the
  goal file already tracked it.

Also observed in passing: `crosscheck/library/test_case` FAILs at this HEAD. Not
investigated — outside L-4's charter — recorded here only so it isn't rediscovered as new.

## My own error, corrected in-session

Orientation's first pass claimed a doc/reality mismatch: "PLAN/RULES/REPO-SCRIP.md cite
`x64/bin/sbl`, the clone puts it at `x64/sbl`." That was wrong — I misread my own `ls -la
x64/bin` output as if the command had failed and shown `x64/`'s own contents, when it had
actually succeeded and shown `bin/`'s single-file contents. The oracle binary is exactly
where the docs say it is. No doc bug. Noted here in case that false claim propagated anywhere
before this correction.

## Disposition

Landed (SCRIP `6d804efd`), regen committed (`f25a5448` + demo artifact commit `31d22822`),
`.github` cursor moved in the same session. **Not pushed** — session's credential not yet
supplied. L-4 moved from the open RUNGS list to ⛔ CLOSED in `GOAL-SN4-HOME-LOWER.md`, with
the corrected deficit arithmetic recorded so a future session doesn't re-inherit the stale
48=32+16 figure.

## Open, flagged, not chased

The fix's own comment marks the multi-head summing arm ("summed across every run-local
MATCH_BEGIN found, not just the nearest") as UNVERIFIED — no nesting witness exists in the
corpus today. Left as inherited-unverified per the fix's own honesty, not upgraded to
verified by this session's testing (none of the four gates exercise nested `MATCH_BEGIN`
crossing two-plus heads).
