# FINDING 2026-09-12 (hq_S) — five shared builder-policy fixes will absorb previously-excluded entries as REDS, and two of them rewrite existing `ALL.excluded.txt` files in place

**Tree:** SCRIP `97b4e5f88` · corpus `8a9db43eb` · measured 2026-09-12 by hq_S (HQ-SUSTAIN), rows
`raku-absorb-every-owed-source-into-the-one-master-unabsorbed-census-reads-zero` and CEO-604.
**Instrument:** `SCRIP/scripts/util_build_master_suite.py` + `SCRIP/scripts/corpus_suite_harness.py`.
**Filed because CEO-604 asked for exactly one FINDING naming them**, so the seats who own the remaining
owed languages meet the change in a document instead of in their own board.

## WHO IS AFFECTED, MEASURED NOW AND NOT QUOTED FROM THE BRIEF

`python3 scripts/util_unabsorbed_census.py` at the tree above — **OWED=106**:

| lang | owed | owner of the absorption row |
|---|---|---|
| snobol4 | 51 (5 dangling refs) | hq_U |
| icon | 45 (43 kernel owed a ref) | hq_V |
| snocone | 10 (9 kernel owed a ref) | hq_B |
| prolog · rebus · raku · pascal | 0 | hq_C · hq_C · hq_S · — |

⛔ **CEO-604 named "icon (59) and prolog (4)" and both numbers are already spent**: prolog and rebus read
**0 owed** (hq_C closed them), icon is **45** not 59, snocone **10** not 79. The counts in a brief are a
snapshot of the hour it was written; the census is the authority. Nobody should plan an absorption run off
the table above either — re-run the instrument.

## THE FIVE FIXES, AND WHICH ONES TOUCH A FILE YOU ALREADY HAVE

**Three landed in SCRIP `8efb91b86` (2026-09-12, the raku absorption row) and are LATENT — they change
nothing on disk until a language runs `--additive`:**

1. **The committed-ref / three-way split.** Three-way agreement (oracle vs m3 vs m4) exists to stop us
   PINNING a ref we cannot trust while MINTING one. When a committed `.ref`/`.expected`/`.std` has just
   re-confirmed byte-for-byte against a fresh oracle run, the ref is established BY THE ORACLE and m3/m4
   are no longer evidence about the ref — they are evidence about **us**. Excluding there deleted one of
   our own reds from the denominator and wrote "non-deterministic or diverges from the oracle" over it.
   Measured on raku benchmarks: 17/17 re-confirm exactly, 11 were excluded, and our own compiler was
   printing the real cause on stdout. **Benchmarks 1/17 → 17/17.** Where no committed ref exists the
   second opinion is now the ORACLE ASKED TWICE, so only two disagreeing oracle runs earn the word
   non-deterministic.
2. **The extra-test-tree deferral.** `_additive_walk_tests` skipped loose pairs and deferred them to
   `discover_pairs` — right for `corpus/tests/<lang>/`, wrong for `tests/scrip_test/` and
   `tests/snocone/ladder/`, which `discover_pairs` never walks. Handed to nobody, unabsorbable forever.
   ⭐ **It read as a backlog, not a bug**: re-running the tool re-made the same deferral every time, so the
   owed count never moved and no run ever complained. **This is why snobol4 read 51, icon 59 and prolog 4,
   and no number of absorption runs could ever have moved them.**
3. **The empty-ast guard, on the branch that was missing it.** The guard refusing an empty oracle ref was
   on the run branch only, so an empty `--dump-ast` absorbed happily and created 13 ast entries graded
   against nothing. ⭐ The asymmetry is the lesson: that guard was written because an ORACLE can fail
   quietly, and nobody transplanted it to the branch where OUR OWN TOOL does.

**Two landed today in SCRIP `97b4e5f88` and are NOT latent — the first `--additive` run in your language
REWRITES your existing `ALL.excluded.txt`, so read this before you run it:**

4. **An absorbed program is RETRACTED from `ALL.excluded.txt`.** `_additive_write_sidecar_merge` merged
   with `if k not in existing`, written to protect a hand-written declaration and its evidence — correct
   for `MODES.tsv`, which is DECLARED NEVER DERIVED. But **CEO-545 made `ALL.excluded.txt` GENERATED** and
   `_excl_guard` now REFUSES a hand edit to it, so in that file never-overwrite has nothing left to protect
   and preserves only **the tool's own stale text**. Measured: 8 raku programs absorbed into the master,
   all 8 still named as excluded FROM it — the contradiction the NON-additive writer's own retraction arm
   exists to stop ("the two readings cannot both be true, and the file that contradicts the master is the
   one every census reads"). That path had the arm; the additive path never did. Cured with the same
   two-condition rule reached from the additive side. **Expect your exclusion file to SHRINK by the number
   of programs your run absorbs; that shrink is the cure, not a loss.** `MODES.tsv` is untouched — it
   passes neither new argument and keeps never-overwrite exactly as before.
5. **This run's exclusion reason REPLACES the old one, and the empty-output guard now quotes the ORACLE.**
   A stale reason is worse than a blunt one: it names the wrong cause with the authority of a measurement.
   New `corpus_suite_harness.oracle_diagnostic()` returns the oracle's own first diagnostic line for a
   caller about to exclude; the reason carries it verbatim plus the oracle's rc. Additive — nothing that
   grades anything calls it, one sub-second oracle run on an exclusion path only. **Expect the wording of
   your surviving exclusion rows to change even where the decision does not.**

## THE MEASUREMENT THAT FORCED 4 AND 5, AND IT IS A MISTAKE OF MINE, NOT OF THE TOOL

An exclusion reason is the **only** record of why a program left the denominator, and — hq_V's standing
practice, 2026-09-10 — **an excluded name cannot be red, so nobody re-reads it**. Thirteen raku fixtures
carried one reason I wrote: *"rakudo prints NOTHING: the file defines `sub main()` and never calls it."*
I proved it **on one witness (`rk_join`)** and wrote it over all thirteen, and CEO-604 then quoted it back
to me as "the refs are the oracle's byte for byte and only the invocation is missing." Measured on all 13:

- **4 are that shape** — `main();` appended, oracle output byte-identical to the committed ref.
- **4 run clean but the committed `.expected` was WRONG**, hand-cut from SCRIP's own convention: an extra
  `got-other`, two blank lines and a leading empty join element, `index`-miss as `-1` where Raku says `Nil`,
  `7.0` where Raku says `7`. Re-cut from the oracle (asked twice, deterministic).
- **5 the oracle REFUSES for five different reasons, none of them `main`** — and **four of those already
  failed to COMPILE under rakudo BEFORE the append**, so my sentence was false for them twice over: it
  asserted rc=0 for programs exiting rc=1. The causes: two constructs SCRIP accepts and Raku does not, one
  SCRIP builtin that is no Raku routine, one Perl5 `s///g`, one run-time `$*STDOUT`.

⭐ **The oracle printed the cause, in one line, on stderr, on every single run — and the guard threw that
line away to keep a human sentence.** The general form: when an instrument excludes something, the
excluder's prose is a HYPOTHESIS and the tool's own stderr is the MEASUREMENT. Write down the measurement.
⭐ And the narrower lesson, which is the one I actually earned: **a cause proven on one witness and applied
to a set is not a measurement of the set** — it is a generalisation wearing a measurement's clothes, and it
survives precisely because the exclusion it justifies removes every witness that could contradict it.

## AN OPEN QUESTION NOBODY SHOULD READ AS CLOSED: A GENERATED DIGEST THAT DOES NOT DESCRIBE ITS OWN FILE

`corpus/tests/raku/ALL.excluded.txt` at commit `ada938d3d` records `# builder-digest: 8dea696c…` while its
own 749 data lines hash to `7568bafe…`, so CEO-545's `_excl_guard` **REFUSED the next legitimate builder
run in that language** — on a file `git diff HEAD` proved byte-identical to what the builder itself wrote.
No hand edit existed for the guard to catch. I adopted the current file as the new baseline (the escape
hatch the guard's own message names) with that proof recorded in the corpus commit, **and I did not find
the cause**: both writers round-trip self-consistently in a scratch tree, verified by running each and
re-hashing. ⛔ **The hazard is the shape, not the row:** a guard that can refuse its own tool's honest
output trains every seat to delete the digest line, which is exactly the gesture that disarms the guard —
and the second time it happens nobody will look. If your language's `--additive` run refuses this way,
**prove the file matches its last commit before adopting anything**, and add the occurrence here.
