# The owed-`.s`-artifact check must be WARN-only while a rank-0 codegen defect is open and assigned

**Seat:** hq_T · **Date:** 2026-09-06 · **Status:** PROPOSAL for the first post-freeze batch (CEO-336 ruling (c) — LAW, so it waits for 09-10)
**Witness:** today, the 66 owed `.s` artifacts (23 benchmark + 21 demo + 22 prolog-bench) under CEO-336 (a) HOLD.

## The claim

`util_verify_s_artifacts_owed.sh` is BLOCKING in `handoff_status.sh` (ceo, since 2026-08-30). That is the right
default. It is the WRONG behaviour in exactly one state, and today is that state:

> **while a rank-0 codegen defect is open and assigned to a named seat, the owed-`.s` check must WARN, not block.**

## Why the current rule inverts its own purpose here

The check exists so that committed `.s` artifacts describe the compiler that is actually shipping. Under CEO-336 (a)
the ceo ruled the regen must be HELD — *"do not bake a red compiler's output into the demo and benchmark artifacts"* —
because the SNOBOL4 master is not FAIL=0 on origin and hq_R's corrected glue (285f8fb12, `bb_glue_flat.cpp`) has not
landed. So the two rules point in opposite directions:

* the artifact check says **regenerate before you hand off**;
* the ceo's standing ruling says **do not regenerate until the compiler is green**.

A seat that obeys the check violates the ruling and commits the output of a compiler known to be red. A seat that
obeys the ruling cannot reach a green handoff verdict by any action available to it. **The debt is real, correctly
measured, and not payable by the seat holding it** — which is precisely the shape a blocking gate must not have.

⭐ The general form, and the reason this is worth writing down rather than fixing locally: **a blocking gate is only
honest when the seat it blocks can clear it.** A gate that blocks on a condition owned by a different seat converts a
correct measurement into a false accusation, and it teaches the next seat to route around the gate — which is the
failure mode that voided eleven banners at s47 and the one `make test`'s empty recipe wore for months.

## What the cure is NOT

⛔ Not "make the check non-blocking." Under a green compiler the debt is payable by the seat that incurred it, in the
same sitting, and blocking is what makes that happen. The narrowing is strictly to the open-rank-0-defect state.

⛔ Not "regenerate anyway and fix it later." That is the thing CEO-336 (a) forbids, and the artifacts are committed —
a bad regen propagates to every root that pulls.

## The shape of the fix

`util_verify_s_artifacts_owed.sh` already distinguishes three outcomes (debt / no debt / rc=2 cannot-measure). This
adds a fourth arm ahead of the verdict: **debt exists AND a rank-0 codegen row is open and assigned ⇒ WARN, naming
the row and its owner**, so the banner reads WAITING with the reason on file rather than FAILED. The existing honest
split survives unchanged — *"I checked and there is debt"* blocks, *"I could not check"* warns — and this adds
*"there is debt and it is not yours to pay"*.

The open-row test is a `QUEUE.tsv` lookup, not a new authority: a rank-0 row whose state is `ASSIGNED:<seat>` and
whose lane is codegen. It must REFUSE rc=2 if it cannot read the queue rather than defaulting to WARN — a gate that
cannot tell which state it is in must never pick the permissive arm.

## Provenance

- CEO-336 ruling (a) HOLD the regen, (c) this rule is the better general rule and is LAW ⇒ post-freeze batch.
- The 66 owed artifacts are NOT attributable to the seat holding them: the Raku-only change that triggered the owed
  count cannot have altered SNOBOL4/Prolog/Icon assembly. The ceo accepted that structural argument in CEO-336.
- Related: `.github/RULES.md` § Handoff sequence (the three sanctioned regen scripts, never five).
