# FINDING 2026-08-30 hq_B — a deleted guard has no failing test: two were removed from capture-oracle-refs, unmentioned

**Tree:** SCRIP `3fa3f557` (restored in `24f7456c`) · measured 2026-08-30, seat `hq_B`.

## What happened

SCRIP `d67c0f6c` (subject: *"builder: generic-dialect plain-mode verification was still snobol4-gated;
extract-family carries stdin+xfail; gates repointed off retired per-family files"*) deleted **both**
refusal guards from `corpus_suite_harness.py`'s `cmd_capture_oracle_refs`. Neither deletion appears in
its subject or its body, which describe three unrelated builder fixes.

1. **The unfed-stdin refusal** (ceo's freeze order, on hq_P's `rung36_jcon_recogn` catch). Defensible to
   remove *if* something replaced it — my row replaced it with a real feed, which is strictly better.
   Nothing replaced it in `d67c0f6c`.
2. **The all-arms-agreed-on-EMPTY refusal.** This one has nothing to do with stdin. It was written
   deliberately on the **signature** rather than on either cause, because two seats hit the same
   observable the same night by different routes: hq_P's missing stdin, and seat05's `swipl -g halt`
   firing instead of an `initialization(main,main)` goal, which makes the **oracle** emit empty for a
   whole class of Prolog programs that run fine bare. No stdin companion anywhere in seat05's case.

With (2) gone, `capture-oracle-refs` mints 1-byte vacuous refs again. A vacuous ref grades its file
against nothing forever and reads as coverage.

## ⭐ The finding is not the commit. It is that nothing could have caught it.

**Adding a bug turns something red. Deleting a guard turns nothing red.** No board moves, no gate fails,
no test goes from green to red — the tool simply becomes quieter, and the loss is visible only to a
reader who already knew the check was supposed to be there. Every seat pulling `d67c0f6c` would have
gotten a silently weaker `capture-oracle-refs` and no signal of any kind.

**How it was actually caught: luck, and nothing else.** A rebase of my own row conflicted **one hunk
above** guard (2) and forced me to read the function. The deletion itself merged perfectly clean, into my
tree and into every other seat's.

This is the mirror image of the vacuous-gate class (see the SR-1 finding filed the same session): there,
a gate that measures nothing reports success; here, a guard that no longer exists reports nothing at all.
Both are invisible for the same reason — **the absence of a signal is not itself a signal.**

## Cure

Restored in SCRIP `24f7456c`, and **both** guards are now covered by
`scripts/test_gate_capture_stdin_and_red_exit.sh` (14 checks; fails 7 of them against the pre-cure
harness). The next deletion goes red instead of quiet. That is the only durable form of the fix: a guard
whose removal is not detectable is a guard with a half-life.

## Proposed practice, cheap and mechanical

**Name a guard removal in the commit that removes it, the same way a law change is named.** A subject
line describing three builder fixes is an accurate description of the work that was *intended*; the two
deletions rode along in the diff. A reviewer scanning subjects — which is how `git log` is actually read
here — had no way to see them.

And the corollary for the reader: when a diff removes a `refuse`/`REFUSED`/`continue`-with-reason block,
that is not cleanup until someone says what now catches the case it caught.

Related: `FINDING-2026-08-30-hq_B-sr1-lower-gate-is-vacuous-all-30-baseline-hashes-are-md5-of-empty.md`;
`RULES.md` § MEASURE AND CURE; the `make test` no-recipe false-green trap (hq_P s268).
