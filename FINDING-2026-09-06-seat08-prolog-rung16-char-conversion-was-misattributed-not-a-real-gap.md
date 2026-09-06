# FINDING — rung16's `char_conversion` red was misattributed; it is not a compiler defect

**seat08, 2026-09-06, FLEET-12. Measured while resuming the isolation ladder walk, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung16 (term I/O, ISO sec 8.14),
on hq_C's instruction after the row's idle-hold was lifted the same day.**

## What happened

hq_C flagged that `current_char_conversion` went green at SCRIP `af8712f3d` while its sibling
`char_conversion` (witness 345, `termio_char_conversion_1`) stayed red, and asked for the
cheap ablation between the two. It found a confound, not a defect.

Witness 345's body sets `char_conversion(a, b)`, writes `'abc.'` to a file, then reads it back
with `read_term(RS, T, [])` and prints `T`. Standalone probe of just the read call:

```
scrip: prolog: builtin arity not wired read_term is not on the ladder yet -- rung 6 lands it
```

This is the **pre-existing, already-tracked** `read_term/3`-with-any-options gap (own rung06
finding, `streams_read_term_empty_options_1`, rank 203 — the same gap rung16's own prior finding
already cross-referenced as cause #4). It fires regardless of `char_conversion`. Swapping the one
line to plain `read(RS, T)` (arity 2, no options list) removes that confound while still
exercising `char_conversion`'s effect on stream input:

| probe | swipl 9.0.4 (oracle) | scrip m3 | scrip m4 |
|---|---|---|---|
| `read_term(RS,T,[])` (witness 345 as written) | REFUSE not reached — oracle has no rung06 gap | `read_term is not on the ladder yet` (rc=2) | not built |
| `read(RS,T)` (ablated) | `abc` | `abc` | `abc` |

The oracle prints `abc` **either way** — `char_conversion(a,b)` populates the conversion table
(confirmed separately: `current_char_conversion(a,X)` reflects it) but is **not applied** to this
read path in real SWI-Prolog; that is genuine ISO/SWI behavior, not a gap in the test. SCRIP's
`read/2` path matches the oracle byte-for-byte in both modes. **`char_conversion/2` and
`current_char_conversion/2` are both already correctly implemented** — the "3. char_conversion/2
and current_char_conversion/2 both entirely absent" cause named in the 2026-09-05 finding was
true when written (both were unimplemented then) but is now stale for `char_conversion` too: only
the *entanglement* with cause #4 was left standing once af8712f3d landed the builtins themselves.

## Fix applied (witness only, not a cure)

Edited witness 345 in `corpus/tests/prolog/ALL.pl` in place: `read_term(RS, T, [])` →
`read(RS, T)`. `.ref`/`.csv` needed no change (same expected output, same line count). Corrupt-ref
sanity re-proven (corrupted line 928 of `ALL.ref` → both modes FAIL; restored → both modes PASS).
`test_prolog_ladder.sh --only 16`: **PASS=4 FAIL=10** (was PASS=2 FAIL=12 after af8712f3d alone).
`LADDER.tsv` rung16 STATUS `RED` → `PARTIAL` (2/7 BUILT), NOTE appended in place rather than
rewritten, so the 2026-09-05 finding's causes 1/2/4 stay traceable.

## Scope

Nothing to route to hq_C: this closes out `char_conversion` as a distinct defect entirely — there
is no cure left for it to land. The remaining rung16 causes are unchanged from the 2026-09-05
finding: `write_term/2` family and `current_op/3`, still hq_R's per the row's own LANE REVIEW;
`read_term_variable_names` stays wherever the rung06 finding already routed it. Sent directly to
hq_C (who asked for this ablation) rather than filed silently.
