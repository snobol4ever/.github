# FINDING 2026-09-06 — seat05 — twelve strengthened witnesses reconfirmed clean; rung26 pow cure verified real and its vacuous-pass risk closed; one correction to my own prior finding

Context: FLEET-12, seat05, hq_B lane, row `icon-ladder-every-feature-in-isolation-with-variations`.
Brief: hq_B mail `both-your-new-defects-are-cured-and-pushed-the-hang-first-as-you-ranked-them` (2026-09-06
08:25) asked "any of your twelve strengthened witnesses changes disposition on the current tree ... if
one goes GREEN that was green before, since that is the vacuous shape you were hunting" — re-testing the
Class A recipe witnesses from `FINDING-2026-09-05-seat05-icon-witness-audit-passes-for-the-wrong-reason.md`
now that hq_B's coercion cure (SCRIP prior push) and hang/runerr cure (SCRIP `1b749a480`) are both in.
Fresh `git pull --rebase` (SCRIP `68eae925e`, corpus `18301c1b3` at measurement) + full rebuild first
(stale-binary discipline) before measuring anything.

## 1. The twelve, reconfirmed

`ladder_rung06_cset_scan_refuse_{any,many,upto}`, `ladder_rung08_strbuiltins_scan_refuse_{find,match,
move,tab}`, `ladder_rung14_limit_limit_refuse_{neg,type}`, `ladder_rung36_sets_refusal`,
`ladder_rung37_bal_{refusal,scan_refuse}`: all twelve PASS both modes, unchanged disposition
(`test_icon_ladder.sh --only 6/8/14/36/37`: 16/16, 24/24, 16/16, 10/10, 10/10). None reverted to a
vacuous green. Delta: **none** — hq_B's cures did not touch any codepath these twelve exercise.

## 2. rung26 pow: cure verified genuinely correct, then its own forward-risk closed

The full-ladder re-run (unrelated to the twelve above) showed rung26 now 14/14 PASS where it was
previously the routed shared-node defect (FINDING-2026-09-05-seat01-icon-limit-and-power-operators...).
This row is the one my own audit flagged: "the instant hq_B's cure lands, THIS SAME witness shape
(`ref="before"` only) will pass **vacuously**." hq_B's `audit-accepted` reply said the recipe would be
written into the cure itself. **It was not** — `ALL.icn` still held the original two-line `write("before");
...; write("after");` bodies (verified by reading the source directly, not inferred from the board turning
green), so the pass, as landed, could not be distinguished from "the cure made this abort for some other
reason."

Rather than take the board's green on faith, ran a direct minimal repro (no harness) against both SCRIP and
the real oracle (`icont`/`iconx`, absolute path) for `(-2.0)^0.5` and `0^(-1)`:
```
oracle: num=206 text=negative first argument to real exponentiation   |  num=204 text=real overflow, underflow, or division by zero
SCRIP m3/m4: byte-identical to both lines above
```
**The cure is real** — SCRIP raises the exact oracle error codes/text, not a coincidental abort. Having
confirmed that, applied my own audit's strengthening recipe to close the forward-risk rather than leave it
open for the next person: `&error := 1; write(EXPR); write("num=", &errornumber, " text=", &errortext);`,
ref cut from icont/iconx (never SCRIP), the two `ALL.wantrc` overrides removed (new want rc=0, the
default). Corrupted-ref proven individually (deliberately corrupted both new ref lines, confirmed FAIL
2/2, restored, `sha256sum -c` confirmed byte-identical to the pre-corruption file), then reconfirmed PASS
(`test_icon_ladder.sh --only 26`: 14/14, both before and after the corruption round-trip). LADDER.tsv
rung26 NOTE appended (not overwritten) with the full verification + strengthening account.
`corpus/tests/icon/{ALL.icn,ALL.ref,ALL.wantrc,config/LADDER.tsv}` this commit.

This is the same class my own audit named (CLASS A, passes-for-the-wrong-reason) closing a second time on
the same row: first the witness was vacuous *while red* (any abort reads as "before" only), and it would
have stayed vacuous *while green* had the recipe not actually been applied. Fixing a faulty test is named
explicitly as mine in hq_B's own instruction ("fixing a faulty test is yours, not mine") — done here rather
than just reporting that hq_B's stated plan hadn't landed yet.

## 3. Correction to my own prior finding: `ladder_rung41_rt_system_exit_stop` was never a valid "positive
pattern" example

While investigating why rung41 showed FAIL(rc=1) want-rc=42 for this witness on the current tree (initially
looked like a possible new regression from today's cure), read the witness source directly:
`write(system("true")); exit(42);`. Ran a minimal repro: real Icon (`iconx`) executes `system("true")`
successfully (prints `0`) and reaches `exit(42)` (rc=42, confirmed). **SCRIP raises `ERROR 022 --
Undefined function called` on `system("true")` itself** — identical to the already-filed rung41 defect
(`system` is one of the eight functions FINDING-2026-09-05-seat05-icon-rung41... names as "entirely
unimplemented"), so `exit(42)` is never reached and the witness fails with rc=1, not 42.

This is **not a new regression** — `system()` was already filed as unimplemented the same day I wrote the
positive-pattern citation, and a fatal untrapped runtime error cannot skip past to a later statement in
either Icon or SCRIP. My original finding's Positive Patterns §1 citing this witness as a legitimate,
non-vacuous, already-passing example was **wrong when written** (whatever tree I measured it against that
day, it was not exercising `system()` the way the current, pushed source does — I did not keep a byte-cut
repro of it at the time to check against, which is exactly the discipline the rest of that finding used
elsewhere and I should have applied here too). Correcting the record rather than leaving a false "this one's
fine" citation standing: the arbitrary-return-value discriminator technique (§1 of the positive-patterns
section) is still sound in general, but this specific witness is not a demonstration of it — it is simply
another instance of the already-known, already-routed `system`-unimplemented class, correctly red for that
reason, and belongs with its seven siblings, not in the positive-patterns list. No corpus change needed
(the witness's rc=42 expectation is already correct given real Icon's behavior; it's blocked on the same
unimplemented-builtin gap as `flush chdir delay getch getche kbhit loadfunc`, not a defect of its own).

## Net

Twelve-witness ask: answered, no delta. Bonus: rung26's cure independently verified correct (not just
"board went green") and its own flagged vacuous-pass risk closed same session. One self-correction on
record. Full ladder + forms-check numbers in the task file LEDGER/NEXT.
