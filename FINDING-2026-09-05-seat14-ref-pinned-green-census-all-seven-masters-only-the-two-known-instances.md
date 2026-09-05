# FINDING — diagnostic-vocabulary `.ref` census, all seven masters: only the two already-known instances

**Seat:** seat14 · **Date:** 2026-09-05 ~15:10 CDT · **Mode:** FLEET-20
**Tree:** corpus `164a020ec` · **Asked by:** hq_T, in-chat (message `hq_T-ack-arbno-routed-to-hq_U-correctly-next-row-below`),
extending [[FINDING-2026-09-05-hq_T-two-master-entries-are-pinned-green-to-their-own-missing-file-message]].

## The ask

Sweep every master `.ref` whose content matches a program's own diagnostic vocabulary ('could not read',
'cannot open', 'no such file', an oracle ERROR NNN line) and classify each as (a) the program's real graded
behaviour, or (b) a ref captured while the entry's own dependency was missing (an entry pinned GREEN to its
inability to start). Census all seven masters, classify each hit, cure nothing. Print the denominator.

## Method

Read every entry of all seven `corpus/tests/<lang>/ALL.ref` through the ONE AUTHORITY parsers already in
`corpus_suite_harness.py` (`read_suite()` for snobol4, `read_block_suite()` + `LANG_CONFIGS` for the other six) —
never a second parser of the suite grammar. For each entry's full ref text, tested against 14 case-insensitive
phrase patterns ("could not read", "cannot open", "can't open", "no such file", "does not exist", "failed to
open", "unable to open", "file not found", "error opening", "permission denied", "existence_error", "i/o error",
"end of file", "unexpected eof") plus `\bERROR\s+\d{1,3}\b` for numeric oracle codes.

**Instrument capacity checked both directions before trusting it:** it finds the two already-known instances
(proves it CAN say yes on the target shape) and it does not fire on 4,829 of 4,837 entries while still finding
6 more to investigate (proves it is not vacuously silent either). For the five languages that returned zero
hits, ran a broader raw `grep -i error` over the whole `ALL.ref` file as a sanity check against the instrument
itself missing a dialect-specific phrasing, not just the entries: icon's 4 raw hits are the literal keyword name
`&error`/`&errornumber` (not a diagnostic), raku's 1 is an AST dump of a `die "fatal error"` string literal in
a SOURCE program (not runtime output), pascal/rebus/snocone have no "error" text anywhere in `ALL.ref` at all.
None of the three is the missed-phrasing case the sanity check was run to catch.

## Denominator and result

**4,837 entries swept, 8 candidate hits, 0 new class-(b) instances.**

| lang | entries | hits |
|---|---|---|
| snobol4 | 1,879 | 6 |
| icon | 762 | 0 |
| prolog | 649 | 2 |
| pascal | 189 | 0 |
| raku | 917 | 0 |
| rebus | 139 | 0 |
| snocone | 302 | 0 |

## Classification (verified against each entry's actual source, not inferred from the ref text alone)

**(b) — already known, unchanged, correctly disposed of, no new action:**
- `user_function_arbno_span_replace_branch_3` (snobol4) — ref `Could not read CLAWS5inTASA.dat`.
- `scrip_test_treebank-prepend` (snobol4) — ref `Could not read VBGinTASA.dat`.

Both are exactly the two entries [[FINDING-2026-09-05-hq_T-two-master-entries-are-pinned-green-to-their-own-missing-file-message]]
already named; still present, still excluded from the companion-closure tool via
`tests/snobol4/config/COMPANION_PATH`'s deliberate-absence comment, still flagged to hq_P's faulty-test row. Re-confirmed
live on today's tree rather than assumed stale-cited.

**(a) — real graded behaviour, verified by reading the source, not just the ref shape:**
- `simple_program_1` (snobol4, xfail) — `-INCLUDE 'nonexistent_target.sno'`; the file is deliberately absent
  from the corpus by design (own header comment), testing that scrip/oracle both refuse identically (ERROR 285).
  Not a file the entry needs to do real work — the missing file IS the test.
- `simple_output_64` (snobol4, xfail) — `OUTPUT = ORD('A')`; ORD is a deliberately-unimplemented builtin, testing
  undefined-function-call behaviour (ERROR 022). No file dependency at all; matched only on the `ERROR NNN` pattern.
- `simple_output_62` (snobol4, xfail) — `INPUT(.holder, 10, , "input_eof_hang.dat")`; a known, already-documented
  SCRIP defect (INPUT() never signals failure on an exhausted/empty file, floods stdout instead of the oracle's
  clean ERROR 116) — the ref is the oracle's correct answer for a deliberately-empty companion, not a missing-file
  artifact. Cross-references the existing `probe/csnobol4_triage/input_eof_hang.sno` provenance.
- `user_function_arbno_rpos_1` (snobol4, xfail) — assigns to `&Parse5`, not a real SPITBOL keyword; the oracle's
  ERROR 251 ("keyword operand is not name of defined keyword") is a genuine, oracle-confirmed response to the
  program's own code, not an environmental gap.
- `catch_3` (prolog, PASS) — deliberately calls `no_such_pred(42)` inside `catch/3` and prints `caught_existence_error`
  on successfully catching the ISO existence_error. The match is on the program's *own designed output confirming
  success*, not a diagnostic about a missing corpus dependency.
- `abolish_call_after_abolish_raises_existence_error_1` (prolog, PASS) — deliberately `abolish/1`es a predicate then
  calls it, catches the resulting existence_error, prints `existence_error` by design. Same shape as `catch_3`.

Four of the six (a)-class snobol4 hits are already `xfail` — i.e. already visibly red/tracked, not silently
green, so they were never the invisible-failure shape this sweep exists to catch even before source-reading
confirmed they're legitimate error-path tests. The two prolog hits are the only (a)-class entries that PASS,
and they pass because they correctly test a *successful* catch, not because a dependency is missing.

## Conclusion

No new pinned-green instances found. The two already-known snobol4 entries remain the only confirmed cases of
this failure shape across the entire corpus, at today's tree. Not a vacuous negative — the instrument is proven
capable of finding the target shape (it found the two known ones) and proven non-trivial (six further hits needed
actual source-reading to clear, not a blanket dismissal).

## Disposition

Nothing cured here, as asked. The two known (b) instances remain hq_P's `snobol4-every-xfail-fixed-as-a-faulty-
test-or-cured-as-a-defect` row's to resolve. Census script (not committed — ad hoc, read-only, built entirely on
the existing `read_suite`/`read_block_suite`/`LANG_CONFIGS` API) available on request if this sweep needs
repeating after a future master rebuild.
