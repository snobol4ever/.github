# FINDING 2026-08-30 seat14 — `insertion-sort.raku`/`merge-sort.raku` cannot pass DONE-WHEN as currently graded: checked-in `.ref` does not match live `/usr/bin/raku`, and separately SCRIP's `rand`/`srand` is glibc's PRNG, not Raku's — needs a ceo/methodology ruling, not a code fix.

## CONTEXT
Found alongside `FINDING-2026-08-30-seat14-raku-xx-operator-does-not-reevaluate-lhs-per-repetition.md` while working `raku-frontend-real-world-syntax-gaps`. Two independent problems compound here; either one alone would already block this kernel.

## PROBLEM 1 — THE CHECKED-IN `.ref` DOES NOT MATCH THE LIVE ORACLE, MEASURED NOW
`corpus/benchmarks/raku/insertion-sort.raku` (`srand(42)`, sorts a 500-element pseudo-random array, prints `@ints[0]`). Checked-in `insertion-sort.ref` says `0`. Running the exact, unmodified kernel file through `/usr/bin/raku` (v6.d, this box) three times, deterministically: **`1`**, not `0`. (SCRIP itself currently outputs `16` — see Problem 2, a different number again.) I don't know this ref's capture provenance (predates this task's LEDGER, which only goes back to pass 1 of this row and never mentions capturing it) — flagging rather than guessing whether it was ever actually agreement-checked against a live Raku run, or against what process.

## PROBLEM 2 — EVEN A CORRECT REF CANNOT BE MATCHED: SCRIP'S PRNG IS A DIFFERENT ALGORITHM, NOT JUST A DIFFERENT BUG
`src/runtime/by_name_dispatch.c:576`: `.rand` → `(double)rand() / RAND_MAX * to_real(recv)`; `by_name_dispatch.c:3447-3449`: `srand` → glibc `srand((unsigned int)seed)`. This is a thin wrapper over the C standard library's PRNG — structurally unrelated to whatever algorithm Rakudo/MoarVM uses internally. **No seed value can make SCRIP's random sequence match real Raku's** — this is a by-design (if likely unexamined) gap, not a bug fixable by a small patch. Confirmed empirically: seeding both with `srand(42)` and drawing raw values gives SCRIP `16, 164, 345, ...` vs real raku `122, 372, 319, ...` — different from the first draw.

`corpus/benchmarks/raku/merge-sort.raku:34` uses the identical `(SCALE.rand).Int xx SCALE` pattern and inherits the same problem (it's also independently blocked by the declined map/grep native-emitter gate, so this isn't currently its binding constraint, but would become one if that gate is ever cleared).

## WHY THIS ISN'T SOMETHING TO JUST FIX HERE
Fixing `FINDING-...-xx-operator-does-not-reevaluate...` (the other finding) is necessary but not sufficient — even a perfectly-reevaluating `xx` would draw from glibc's PRNG, which will never reproduce Raku's sequence. Making SCRIP's Raku `rand`/`srand` bit-exact with Rakudo/MoarVM's actual PRNG algorithm would be a real, separate, likely nontrivial feature (research the exact algorithm MoarVM uses, reimplement it, verify bit-exactness across seeds) — well outside "frontend syntax gaps" and not something to decide unilaterally mid-row.

## RECOMMENDATION (not decided here — flagging for a ruling, same shape as the standing `point_class_add2` MoarVM-internals exclusion in this row's own DONE-WHEN section)
Options for whoever rules on this — naming them, not choosing:
1. Exclude `insertion-sort`/`merge-sort` from the DONE-WHEN acceptance sweep the same way `point_class_add2` is already excluded (implementation-internals mismatch, not a language-syntax gap), and re-target the row's 16/16 to 14/14 + these 2 explicitly out of scope.
2. Re-capture their `.ref` files against SCRIP's own (bug-fixed) output self-consistently, if this row's methodology ever accepts self-consistent capture for PRNG-dependent kernels specifically (check whether `capture-oracle-refs`, the new consolidation tool, has an existing stance on this).
3. Treat bit-exact Raku-PRNG replication as its own tracked goal/row, decoupled from this one.

## VERIFICATION COMMANDS (for whoever re-checks this)
```
/usr/bin/raku corpus/benchmarks/raku/insertion-sort.raku   # -> 1, three runs, deterministic
./scrip --run corpus/benchmarks/raku/insertion-sort.raku < /dev/null   # -> 16 (pre-xx-fix)
grep -n "\"rand\")\|srand" src/runtime/by_name_dispatch.c
```
