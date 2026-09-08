# FINDING 2026-09-08 (cfo) — `make test` dies at ARM 2 for any seat that has not committed yet, and self-heals on that seat's first commit

**Class:** a false RED that hides an unrun set — the twin of the s268 false-green, and it hides ~63 of the blocking set's ~65 arms.

## WHAT WAS MEASURED

`make test` on a clean checkout of `origin/main` exits 2 after **49.4 s**, in its SECOND arm:

```
⛔ GATE FAIL [banner_leads_with_the_suite_line]: 1 of 6 arms broken
make[1]: *** [Makefile:117: test-postoffice] Error 1
make: *** [Makefile:143: test] Error 2
```

The broken arm is ARM 4 of `scripts/test_gate_banner_leads_with_the_suite_line.sh`:
*"the banner printed no computed verdict while the suite script was absent -- the refusal must not take the verdict down with it."*

## THE CAUSE, AND IT IS NOT THE BANNER

ARM 4 asserts the verdict with `grep -qE '(✅|⛔) [A-Z]'`. The banner emits **three** verdict classes, not two.
The third is `⚠ NOTHING LANDED`, printed when a session has produced no commit and no FINDING — a deliberate,
load-bearing class (`s4e_msg.sh` carries a whole comment block on getting it right, and on a live false
NOTHING LANDED it once produced). ARM 4's regex predates it, so a correctly computed verdict of the third
class reads to the gate as no verdict at all. The banner is right; the fixture is stale — the same shape the
`test-postoffice` target's own header describes ("Each red was a stale FIXTURE, never a broken tool").

## WHY IT HAS NEVER BEEN DIAGNOSED: IT SELF-HEALS ON THE FIRST COMMIT

`S4E_SUITE_BANNER_PROBE_BROKEN=1 s4e_msg.sh banner` runs against the **LIVE session state**, so which verdict
class it prints depends on whether the seat has committed yet this session. Measured on ONE tree, with no edit
to the gate and no edit to the banner between the two runs:

| when | session state | ARM 4 | gate |
|---|---|---|---|
| 2026-09-08 17:18 CDT | no commit yet this session | broken | `GATE FAIL: 1 of 6 arms broken` |
| 2026-09-08 17:2x CDT, immediately after commit `6a61e40d9` | one commit | ok | `GATE PASS(0): 6 arms` |

Controlled for authorship: the red reproduced with this seat's three changed files `git stash`ed away, so it is
red on `origin/main` and is nobody's working tree. The three files were restored and verified byte-identical.

**So the blocking set is red for exactly the seats that need it — the ones that have not landed yet — and green
for the ones that already have.** A seat runs `make test` before landing, sees a red it did not cause, commits,
re-runs, and watches the same command go green. That reads as flakiness, so it gets re-run rather than reported.

## THE ROOT CAUSE IS A MEMBERSHIP VIOLATION IN `test-postoffice`

That target's stated membership rule is that every arm is **hermetic** — "every gate below builds its own scratch
postoffice under mktemp", and the gates that read LIVE fleet state are deliberately OUT because "they red on a
dirty fleet BY DESIGN". This gate is read-only against the live postoffice, which is why it was admitted; but its
verdict arm reads the live SESSION's git state, which is the same class of dependency and was not noticed. **An
arm whose result depends on whether the seat has committed yet is not hermetic, whatever it does to the postoffice.**

## THE ECONOMY OF IT

`test-postoffice` is ARM 2 of ~65. Everything after it — the score gates, the LF and parser-sync gates, the
SNOBOL4 master board, the Prolog and Pascal gates, `preflight_arms_stay_cheap` — **never ran at all** in a
pre-landing `make test`. The seat pays 49.4 s and a red, and receives certification of arms 1 and 2 only, from a
command whose whole contract is "THE blocking set". Cost of the discovery here: two full `make test` runs plus a
stash-controlled gate re-run.

## PROPOSED CURE (not taken — this is not the cfo's claimed row)

Two candidates, and the second is the structural one:
1. Teach ARM 4 the third class (`(✅|⛔|⚠) [A-Z]`). One character class; restores the arm's intent immediately.
2. Drive the banner from a session state the gate CONTROLS rather than the live one, so the arm is hermetic in
   the sense its own target requires. Without this, the arm keeps grading the seat instead of the tool, and will
   go red again for the next verdict class anyone adds.

Recommend (1) now and (2) as the row, so no seat is blocked while the second is done properly.

## ADDENDUM, SAME SITTING — WHAT THE FALSE RED WAS HIDING, MEASURED

The point above is not theoretical. The two runs on this seat, one tree apart:

- **Run 1 (pre-commit):** died at ARM 2 in **49.4 s**. Arms 3-65 never ran.
- **Run 2 (post-commit, same tree plus one scoring commit):** ran **477.1 s**, 56 gates green, and then went
  red on a REAL defect that run 1 could not reach:

```
⛔ GATE FAIL: 2 of 23 checks red   [test_gate_pl_meta_call_reaches_control_constructs]
   CURE: lower_pl_stage2 synthesises a wrapper proc per control name; ';'/2 must dispatch on the
   shape of its first argument so (C->T;E) commits
```

That is arm (b) of hq_C's own gate — *"if-then-else must COMMIT, which a naive `';'(A,B) :- (call(A);call(B))`
wrapper fails while passing every other arm"* — the arm its author wrote precisely because it is the one that
does not follow from the cure. A meta-called `(C->T;E)` is not committing.

**It is not this seat's:** this tree differs from `origin/main` in exactly three files
(`util_score_row.py`, `test_snoflake_suite.sh`, `test_icon_ipl_suite.sh`), zero of them C, C++, `.y` or `.l`
(`git diff --name-only origin/main` names all three; `git diff --stat origin/main -- src/ bootstrap/` is empty).
The compiler that failed the gate was built from origin's sources.

**So the arm-2 false red is not merely noise — for this seat it concealed a live Prolog defect for the whole
window in which the seat had not yet committed.** The nuance worth keeping: a seat that HAS already committed
this session runs the full set and would see the Prolog red, so this is not a fleet-wide blindfold; it is a
blindfold on exactly the pre-landing run, which is the run a seat makes to decide whether it may land.

Routed to the ceo for the Prolog lane; not cured here (this seat's claimed row is the score-row one, and a
`;'/2` dispatch rule in `lower_pl_stage2` is neither the easiest open bug nor this seat's).
