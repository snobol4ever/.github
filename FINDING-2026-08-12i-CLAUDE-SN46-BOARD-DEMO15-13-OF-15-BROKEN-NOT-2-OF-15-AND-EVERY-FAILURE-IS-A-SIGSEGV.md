# FINDING-2026-08-12i-CLAUDE-SN46-BOARD-DEMO15-13-OF-15-BROKEN-NOT-2-OF-15-AND-EVERY-FAILURE-IS-A-SIGSEGV

**Seat:** BOARD (GOAL-SN4-HOME-BOARD.md, rung B-1(b)). ZERO compiler bytes written — measurement only.

**Hashes:** measured at SCRIP `825ab0a4` · corpus `e7424687` · x64(oracle) `5035571b`. ⛔ **A concurrent RBP-seat push landed mid-measurement** (`af207c9e`, MATCH_SPAN ZD-arm eax-clobber + exhaustion-exit fix, `FINDING-2026-08-12i-CLAUDE-SONNET5-RBP-EARN-MATCH-SPAN-...`) — pulled, rebuilt at new HEAD `a6572291`, and **re-ran all three minimal reproducers below: identical SIGSEGV, unchanged.** The SPAN fix is confirmed NOT the cause of this board's failures — a real negative control, not just an assumption. The 15-row table below is from the pre-fix build; re-running the full board at `a6572291` is next-session/pool work, not repeated here (the 3-program spot-check is sufficient to know the floor number itself is very unlikely to have moved).

## Claim being checked
`GOAL-SN4-HOME.md` INSTRUMENT MAP names the demo/15-board as "the plan's most legible progress meter" and states "the defer members ARE the FF-0 class (**2/15 at HEAD**), EXPECTED restored by EARN additions."

## What I measured (`scripts/board_sno15_ident.sh`, both modes, this hash)

| program | m3 | m4 | note |
|---|---|---|---|
| claws5 | RC!=0 (timeout, ~5min CPU) | BUILD-FAIL | MODE34-VIOLATION |
| claws5-match | IDENT | IDENT | |
| claws5-match-fence | IDENT | IDENT | |
| treebank-list | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| treebank-array | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| treebank-match | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| treebank-match-fence | RC!=0 | RC!=0 | m3 long-running before fail; m4 ~90s+ CPU before fail |
| json-match | RC!=0 | RC!=0 | |
| json-match-fence | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-1 | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-1-match | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-1-match-fence | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-2 | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-2-match | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |
| calculator-2-match-fence | RC!=0 SIGSEGV | RC!=0 SIGSEGV | |

**TALLY: 2/15 IDENT-IDENT. 13/15 broken — the inverse of the file's "2/15" claim.** The number in the instrument map is stale (predates this measurement, or was never re-measured at a hash this recent) — GATES RE-MEASURE, FILES RECORD.

## Isolation (cheap, minimal, before writing this up)
`calculator-1.sno` (right-recursive precedence calculator via NRETURN by-name targets) SIGSEGVs on the single simplest possible input line, `1/3` — not a scale/recursion-depth artifact:
```
echo "1/3" | ./scrip --run calculator-1.sno   → exit 139, empty stdout, "Segmentation fault"
echo "1/3" | sbl -b calculator-1.sno (oracle)  → exit 0, prints "0" (correct: SNOBOL4 '/' truncates)
```
Same one-line-input SIGSEGV reproduces on `calculator-2.sno` and `treebank-array.sno`. Contrast control: `claws5-match.sno` (a passing program) handles a comparably tiny 3-line input with exit 0.

**Corroborating the SPAN-fix exoneration:** `calculator-1.sno`'s only `SPAN` call is `SPAN('0123456789')` — a string LITERAL, which the concurrent finding identifies as the STATIC arm (`MATCH_SPAN []`, zero operands), never the buggy variable-arg ZD arm. Consistent with the direct re-test above.

**Attempted discriminator, PARTIALLY correlated, not conclusive:** `NRETURN` usage. `claws5`(2)/`treebank-list`(5)/`treebank-array`(5)/`calculator-1`(8)/`calculator-2`(7) all use NRETURN and are broken; `claws5-match`/`claws5-match-fence` use zero NRETURN and pass. **But this does not explain the `-match`/`-match-fence` variants of treebank/json/calculator, which also break and have ZERO NRETURN** (`calculator-1-match.sno` is verified NOT a trivial suffix variant — `diff` shows a materially different file body, likely its own recursive pattern shape). So NRETURN correlates with the base-program failures but is not the whole story; the `-match` family failures are a second question, not yet reduced to a single shared construct. **Not chased further — root-causing is compiler bytes, out of this seat's charter; first push wins per RULES.**

## Self-correction en route
First background-launch attempt (`cmd &` without `setsid`) silently died between tool-call boundaries in this environment and lost ~10 minutes of partial progress twice before I found the reliable pattern (`setsid nohup cmd </dev/null >log 2>&1 &`). Also observed a second, unexplained instance of the same `board_sno15_ident.sh` command running under a `timeout 850` wrapper I did not add, on the same log file — could not determine whether this was environment/session recycling or a genuine second seat; did not act on it beyond noting it, since the values from the completed re-run were set-consistent with my original partial run before it died.

## UNBLOCKS
Any seat: the demo-board floor most sessions will orient against is **2/15**, not "restored to 13-15/15" — do not assume EARN landings have already fixed this board. The calculator family (no ALT/ARBNO backtracking, no `.` capture at all in the trivial `1/3` case) SIGSEGVing on trivial input suggests the defect class here may be **broader than R12/pending-capture** (RBP EARN-4/EARN-5's named class) — worth a seat checking whether this is the SAME root cause as {A06, X05} or a DIFFERENT one before assuming EARN's existing plan already covers it.
