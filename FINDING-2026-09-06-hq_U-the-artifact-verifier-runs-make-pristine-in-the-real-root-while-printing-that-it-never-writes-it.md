# `util_verify_s_artifacts_owed.sh` runs `make pristine` in the REAL root while printing that it never writes it

**hq_U (HQ-UNIFY), 2026-09-06.** Found by walking into it: it destroyed a Prolog ladder measurement mid-run
and the corrupted reading looked exactly like a catastrophic regression.

## 1. THE DEFECT

`scripts/util_verify_s_artifacts_owed.sh`:

    line 115:  echo "    (scratch clone only — the real corpus and SCRIP checkouts are never written)"
    line 122:  if ! ( cd "$ROOT" && make pristine ) > "$WORK/pristine_build.log" 2>&1; then

Line 122 runs **`make pristine` in `$ROOT`** — the live checkout. `make pristine` wipes the per-checkout objdir
and `out/`, deletes `./scrip`, and rebuilds from scratch. For the ~10–20 minutes that takes, **the root has no
compiler.**

The printed reassurance is true of the *sources* and false of the *build*, and the sentence does not make that
distinction — so a reader is told the opposite of the thing that will bite them. Nobody expects a **verifier**
to be destructive.

## 2. HOW IT PRESENTS — AND WHY IT LOOKS LIKE SOMEONE ELSE'S REGRESSION

Measured here. I launched the verifier and `test_prolog_ladder.sh --to 40` concurrently in the same root:

    LADDER --to 40: graded=568 PASS=218 FAIL=350     <- rungs 0-9 pass, rungs 10-18 ALL PASS=0
    rung 10..18 every witness: m3=FAIL(rc=127) m4=NOBUILD

`rc=127` is *command not found*. The ladder started with a binary, the verifier deleted it around rung 9, and
everything after failed to launch. ⛔ **The shape is the trap:** a clean prefix of passing rungs followed by a
total wipeout reads as a real, severe, systemic regression — and 350 failures against a known 82 is exactly the
kind of number a seat telegraphs to the fleet immediately. I was one message away from reporting a Prolog
collapse on origin HEAD that did not exist.

The clean re-run, ladder alone, same day: **`graded=568 PASS=486 FAIL=82`**, SCRIP `58dd0a7a6`, corpus
`760fe0850` — identical to the pre-existing red. Nothing had regressed.

## 3. WHY IT MATTERS BEYOND ONE WASTED RUN

- ⛔ `util_verify_s_artifacts_owed.sh` is run by **`handoff_status.sh`**, which every seat runs at handoff, and
  which *blocks* on its result. So the most-run instrument in the tree silently deletes the build of the root
  it runs in, at exactly the moment that root is busiest.
- It **contradicts the loosened-pristine ruling** (Lon 2026-09-03: *"It's time to loosen this pristine build
  that keeps preventing forward progress and causes 20 minute wait times"*). Verdicts now run on incremental
  builds — but this verifier still forces a pristine, and it is not one of the sanctioned pristine occasions.
- Under FLEET-12 every root is busy. Any measurement overlapping a handoff in the same root is silently void,
  and **there is no diagnostic** — the victim runner reports its own honest `rc=127` and has no way to know the
  cause was another process in its own root.

## 4. ⭐ THE TRANSFERABLE SHAPE: AN INSTRUMENT THAT INVALIDATES OTHER INSTRUMENTS, WHILE REASSURING YOU

This root's standing lesson is *an instrument that answers a narrower question than you think you asked will
never say so*. This is the mutation of it that is worse: **an instrument whose SIDE EFFECT invalidates every
other instrument in the root, while printing a line that tells you it has no side effects.** The reassurance is
what stops you looking, exactly as an exoneration does.

⭐ And note which discipline actually caught it, because it was not scepticism about the verifier — I had no
reason to suspect it. It was the standing rule to **check the instrument before reporting the number**: `rc=127`
is not a semantic failure, so I ran the binary by hand instead of writing the telegram, and found `./scrip`
missing. *A failure mode that cannot be produced by the thing under test is a fact about the harness.*

## 5. WHAT SHOULD CHANGE (routed to hq_T, instruments)

1. **Fix the false line, or fix the behaviour.** Either build in `$WORK` like the message promises, or change
   line 115 to say plainly that the root's build is destroyed and rebuilt.
2. **Refuse to run while another measurement holds the root**, or at minimum print a loud banner before the
   `make pristine` so a concurrent victim has something to find.
3. **Re-justify the pristine at all** against the loosened-pristine ruling; an incremental build would serve a
   `.s`-currency check and would not cost 20 minutes.

⛔ Not cured here: this is hq_T's instrument lane and the fix is a behavioural choice between the three above,
not a one-liner I should pick unilaterally. The artifact debt it was checking is separately cleared and pushed
(corpus `760fe0850`).
