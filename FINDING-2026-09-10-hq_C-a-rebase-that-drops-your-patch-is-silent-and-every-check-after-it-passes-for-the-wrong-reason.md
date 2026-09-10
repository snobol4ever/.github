# FINDING 2026-09-10 hq_C — a rebase that drops your patch is silent, and every check you run afterwards passes for the wrong reason

**Seat** hq_C (HQ-CORRECTNESS) · **Mode** NONET · **Row**
`icon-jcon-errors-red-both-modes-diagnosed-to-its-first-divergence-and-cured` · **Trees** SCRIP `3e68226ea` →
`5097b54f2`, corpus `3f0b910e4`

## What happened, in the order it happened

1. Measured jcon/arizona `errors.icn` on SCRIP `3e68226ea`. Diagnosed line 180: error 206 (negative first
   argument to real exponentiation) is raised **value-less** by Arizona, so `&errorvalue` must FAIL after it and
   the fatal report must print no `offending value:` line. `src/runtime/arithmetic.c` passed the left operand.
2. Cut the one-line cure (`core_icn_error(206, FAILDESCR)`), wrote a gate, watched it go both ways (6/14 red on a
   reverted rebuilt control, 14/14 cured), ran the control arms, committed.
3. `git pull --rebase` before push. **Clean. No conflict. No warning.** Rebuilt, re-proved the gate — PASS.
   Re-ran `make preflight` — 33 arms, 0 red. Pushed. Telegrammed the FLIP.
4. `git show <sha> --stat` on the pushed commit: **Makefile + the gate. Two files. No source change.**

The cure had landed twenty minutes earlier as another seat's `118fe2e4a`, carrying the identical line. Git
recognised my hunk as already applied and dropped it.

## The defect in the procedure, which is not the duplicate

Two seats converging on one line in a class we were explicitly told to co-sign is a scheduling cost, and it is
recoverable. The unrecoverable part is that **nothing told me, and everything I did next looked like
confirmation.**

> A rebase that DROPS your patch is byte-identical, from the outside, to one that KEEPS it: no conflict, no
> warning, exit 0, a green build — and every arm you re-measure afterwards is TRUE, because the other seat's
> identical cure is holding them up.

I did re-prove the gate after the rebase. That is the rule, I followed it, and it could not have failed. I ran
preflight. It could not have failed. Both instruments measure **the tree**, and after the rebase the tree was
correct. The question was about **the commit**.

⭐ **The only instrument that separates *my change did this* from *my change is gone* is `git show <sha> --stat`
on the PUSHED commit, read AFTER the push.** It is the one step that feels redundant, because you just wrote the
thing and you can see the diff in your own editor. Re-running the tests is what diligence *feels* like here, and
it is precisely the wrong instrument.

This is the REBASE-BASELINE COROLLARY (CLAUDE.md; RULES.md) in a sharper form than the one usually quoted. The
corollary is normally cited for A/B **numbers** — a pull between the arms voids the earlier arm. It binds a
**commit's own claim of authorship** just as hard, and there the failure is silent rather than merely stale.

## The second failure: I over-corrected, and destroyed a real finding

Correcting the record, I retracted **two** things. One retraction was right (the cure was not mine). The other
was wrong. I had reported an m4-only crossing at `errors.icn`'s last line — the digits of `180` split around
`stop(&output,'testing stop')`'s output — and I wrote it off as an artifact of a mis-linked witness.

It was real. The run that first showed it linked with an **absolute** `-L` against this tree's `out/`; the defect
was genuinely present on `3e68226ea`; `e7e916e14` cured it (stop() honours a leading file argument and flushes
before exit), confirmed independently by the seat that landed it. A **later, separate** run of mine *was*
mis-linked with a relative `-L`. Two independent facts, one of them real, and I used the second to explain away
the first.

⭐ **Once you have caught yourself in one instrument error, the cheapest story for every other surprise in the
sitting is that same error — and it is wrong exactly as often as it is right.** It is cheap because it is already
proven, it requires no new work, and it arrives wearing the costume of rigour: retracting your own finding feels
like the conservative move.

It is not conservative. It destroys a real observation, and it destroys **the one that was hardest to get** — a
defect nobody else has reported is exactly the one with no second witness to rescue it. **A retraction needs its
own evidence. "I was sloppy over there" is not evidence about over here.** Attribute each observation to the run
that produced it, and re-read *that run's* actual command before you retract it. One scroll back; it cost nothing.

## What did survive, stated without flattery

Three commits by two seats took `errors.icn` to **0 differing lines against its `.std` in both copies and both
modes** (533 lines, byte-identical): `118fe2e4a`, `e7e916e14`, and a gate. **None of the three cures is mine.**

What is this seat's:

- `scripts/test_gate_icn_errorvalue_is_absent_when_the_error_carries_none.sh`, wired into `make test` — 5
  recorded shapes + 2 fatal reports × 2 modes against a **freshly built** icont/iconx. `118fe2e4a` shipped its
  cure with no gate, and **a cured behaviour with no gate is one refactor from being un-cured.**
- The class **bounded from the oracle's own source rather than from the witness**. `runerr(N)` with no second
  argument in `icon-master/src/runtime/*.r` is Arizona stating that a raise carries no value. Twelve numbers are
  value-less at **every** Arizona site (141 143 146 201 203 204 206 208 216 305 306 402) while **101, 103 and 205
  appear both ways** — so the property is per-**SITE**, never per-**NUMBER**, and a cure keyed on the number
  would have been wrong for exactly the numbers it most wanted to cover.
- The 203 hand-off: `core_icn_error(203, a)` in `arithmetic.c`'s `BINOP_POW` `rt_big_*` arm was the second and
  last deviating site. It is the large-integer lane and I had no witness for it on this tree, so it was **named,
  not cut** — and the owning seat took it within the hour.

## The arm that cannot be skipped, for anyone gating an error keyword

`&errorvalue` **holds its last value**. So "this error carried no value" and "this error carried the PREVIOUS
error's value" render **identically** wherever a value-bearing error ran first — and in a 500-line program like
`errors.icn`, one always has. A build that simply never cleared the keyword goes green on any witness whose first
error is the value-less one.

The discriminator is the gate's `STALE` arm: raise 102 (which *does* carry `"q"`), **then** 206, then demand the
read FAIL. It is the only arm that can tell a build that **CLEARS** from one that merely never **SET**. This row
had already paid for the identical instrument defect on `&errornumber` earlier the same day — same shape, one
keyword over.
