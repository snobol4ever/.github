# FINDING: a ruling's premise expired between the ask and the answer — `trace_driver` was cured by the very dedup that raised the question

**hq_P · 2026-08-29 · row `beauty-suite-ref-provenance` · corpus `d2b423fb0`, SCRIP `5cdcdd13`**

## The claim

Lon ruled three beauty_suite drivers **OUT-OF-DIALECT** (not SNOBOL4-conformance witnesses, because they use
constructs SPITBOL rejects by documented restriction). ⛔ **One of the three — `trace_driver` — was already cured
when the ruling was written, by a commit that landed HOURS EARLIER THE SAME DAY.** It was not marked. Marking it
would have enshrined a false claim in suite metadata and permanently excluded a genuinely conformant witness from
SPITBOL-conformance scoring.

## The measurement

```
OLD  beauty_suite/trace.sno  (T8Trace = '')      ->  trace_driver.sno(59) : ERROR 243 -- function result in nreturn is not name
NEW  corpus/include/trace.inc (T8Trace = .dummy) ->  rc=0, 9/9 PASS, byte-identical to the pinned trace_driver.ref
```

Both arms run against `/home/resources/x64/bin/sbl -bf`, library includes staged identically; the ONLY difference is
which `trace` source resolves. ⭐ **The whole of ERROR 243 was one token.** SPITBOL's NRETURN restriction (manual
v3.7 line 5961) requires the function's result to be a **name**; `''` is a string, `.dummy` is a name.

`corpus 04b403542` (include-dedup, 06:55 the same day) swapped `trace` from its local copy to the library `.inc` —
it is listed in that commit's own message under *"8 swap cleanly"*. **The dedup deleted the defect and nobody
noticed, because the evidence document went on naming a path.**

## ⭐⭐ The shape, which is the transferable part

**EVIDENCE NAMES A FILE, AND A FILE CAN BE DELETED OUT FROM UNDER A CONCLUSION THAT IS STILL TRUE OF IT.**

`REF-PROVENANCE.md` was not wrong. Every sentence in it remained true *of `beauty_suite/trace.sno`* — a file that no
longer existed. The conclusion did not rot; **its subject was removed.** That is why nothing flagged it: a stale
claim usually contradicts something, and this one contradicted nothing at all.

⛔ **This is the SECOND time this same document learned this same lesson.** Its own §1 carries an earlier correction
— *"the provenance was documentation, not history"* — where git archaeology answered a narrower question than the one
asked of it. Both defects are one defect: **a claim whose subject moved while the claim stood still.**

⭐ **Two structural notes, because "be careful" is not a cure:**
1. **The ask and the answer were concurrent.** The dedup and the escalation were the same seat, the same day, hours
   apart, and neither knew about the other. Any escalation with a latency has this exposure — the tree keeps moving
   while the question is in flight.
2. **Re-verify a refusal against the CURRENT tree immediately before acting on it**, however recently measured.
   Three hours was enough here. The re-verification cost one command per driver and caught it.

⚠️ **The same exposure is live on any other in-flight escalation whose evidence names a path.** Not swept — this is a
finding about one row, and the general sweep is somebody's row, not a claim I am making here.

## What was executed (Lon's rulings, in full)

| item | ruling | executed |
|---|---|---|
| pins | OUT-OF-DIALECT, construct + manual line each | `tree_driver` (ERROR 067, manual 11380) and `ReadWrite_driver` (ERROR 116, manual 11434) marked in `KEEP.md`; **`trace_driver` NOT marked** — see above |
| `TDump` | adopt library + re-pin (the one sanctioned re-pin) | local variant deleted, `TDump_driver.ref` re-pinned from the oracle run |
| `tree` | rename distinctly, ref untouched | `tree.inc` → `tree_mini.inc` |

### ⛔ Two things the rulings' wording did not say, found by measuring

1. **"the driver's `-INCLUDE`" is THREE drivers.** `src/driver/scrip.c:1038` adds the source file's own directory
   **before** `SNO_LIB`, so `beauty_suite/tree.inc` shadowed the library file for `tree_driver`,
   `ShiftReduce_driver` **and** `omega_driver`. Renaming while updating only `tree_driver` would have flipped the
   other two onto the 88-line library file — the exact opposite of the ruling's *"zero behavioral churn"*.
   ⭐ **A shadowing file is a shared node: `grep -l` for its name before you rename it.**
2. **The re-pinned `TDump_driver.ref` deliberately contains two `FAIL:` lines.** They are the driver's own prose,
   not a harness verdict, and **SCRIP is byte-identical to `sbl -bf`** — the row is green because the two agree. The
   driver's `'(Name)'` expectations are CSNOBOL4 answers (`NULL *IDENT(n(x))` succeeds under SPITBOL, fails under
   CSNOBOL4); its own lines 7–9 said so all along. Marked out-of-dialect so a later seat does not "cure" it.

## Control arms

- 17/17 beauty drivers PASS against their pinned `.ref` **before and after every step**, checkpointed twice.
- SNOBOL4 blocking set, read from the printed board: **m3 PASS=1299 FAIL=0 · m4 PASS=1299 FAIL=0 SKIP=0 · MISSING=0**, rc=0.
- `test_gate_suite_conversion_complete.sh snobol4`: unchanged at 34 loose-but-undeclared (all `probe/`/`feat/`,
  pre-existing) — negative-tested by stashing these changes and re-running.
- The new scorecard branch negative-tested both arms (fires on `pin-only`; silent when blanked).

## ⚠️ Two digest numbers measured stale in passing (not this row; recorded, not chased)

`CLAUDE.md` says the SNOBOL4 board is **~32 s** and advises `timeout 600s`. Measured here: **298 s** wall, rc=0.
⛔ That puts the advised bound **within ~2x of the real duration** — precisely the flaky-bound class the same digest
warns about two paragraphs earlier ("a bound tuned to a job's measured duration is not tight, it is flaky"). The
denominator is likewise **1299**, not the 365/893 the digest quotes — though the digest correctly says to read the
board rather than remember a total, which is what was done.
