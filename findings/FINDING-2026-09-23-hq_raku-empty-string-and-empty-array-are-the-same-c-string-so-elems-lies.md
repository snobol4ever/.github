# FINDING 2026-09-23 hq_raku: an empty string and a 1-element array holding "" are the SAME internal C string, so `.elems`/`push` lie on that shape

## What was measured

Oracle-verified against `/home/resources/rakudo-local/bin/raku` directly (real Rakudo 2022.12), both minimal
and in a real corpus witness:

```
my @vals = '';
say(@vals.elems);   # real Raku: 1   -- SCRIP: 0
say(@vals);         # both:      []  -- an array holding one EMPTY STRING prints identically to an empty array
```

`corpus/tests/scrip_test/raku/rk_given18.raku` (master entry `scrip_test_rk_given18`, rank 881) hits this for
real: `my @vals = ''; push(@vals,1..4);` should be a 5-element array (`'', 1, 2, 3, 4`) and print 5 `got-*`
lines under the `given`/`for` loop; SCRIP's `@vals` starts at 0 elements (the leading `''` is invisible) and
prints only 4. `--trace` confirms SCRIP's own event stream sees ONE `VALUE @vals = ''` store, so the value
computed is right -- only the COUNT read back off it afterwards is wrong.

## Root cause, read off `by_name_dispatch.c`'s own `elems` method (line ~738) and the SOH-joined array
convention used throughout the file (`lines`, `split`, `comb`, `words`, ...):

SCRIP represents a Raku array/list as ONE C string, elements joined by `SOH` (0x01). Element count is
derived structurally: `n==0 -> 0 elems`, else `1 + count(SOH bytes)`. This conflates two states that are
distinct in real Raku: "the array is empty" and "the array holds exactly one empty-string element" --
both are the C string `""`. Every reader of this representation (`elems`, `push` growing it, `for` iterating
it, array-to-string join) inherits the same ambiguity; it is not a one-function bug, it is a representation
gap in the shared array encoding.

## Why this was NOT cured in this landing

This is exactly the "class, not a program" shape the pace rules ask an HQ to name rather than patch in place:
curing it means changing what "empty" means for every reader of the SOH-joined array string across the whole
runtime (shared by every language box that touches a Raku/Icon-shaped list), not one function in one file.
A local patch to `elems` alone would still leave `push`/`for`/interpolation disagreeing with it. The correct
fix is a representation change (e.g. a distinguishable one-empty-element encoding, or a length-prefixed
array box) that needs its own design pass and a full-suite regression sweep across every consumer, not a
same-sitting flip.

## Also measured: the sync-step monitor's wire protocol cannot see this class today

`monitor_wire.h`'s value-type enum (`raku_oracle_bridge.py`: `MWT_NULL/STRING/INTEGER/REAL`) has no Array/Hash
carrier -- a VALUE event for an array store is wildcarded by the controller the same way an `UNKNOWN` type is
(cfo's own named gap for Rats applies identically to Arrays/Hashes). Lock-step AGREE on this witness would
not have caught the defect; it was found by direct oracle-output diff (`@vals.elems` on both sides), the same
method that found the `say "$k => %h{$k}"` and `1/4 -> Rat` gaps before it. Anyone reaching for the monitor to
grade an array/hash-VALUE-bearing witness should know it is currently a pass-through, not a check.

## Population, so a future cure can be sized

`grep -rn "SOH" src/runtime/by_name_dispatch.c | wc -l` names every reader of this convention; `elems`,
`split`, `comb`, `words`, `lines`(the method, not the fixed builtin), array literal construction, and `push`'s
growth path are the ones read this session. Not censused exhaustively -- that census is the first step of
whichever seat/officer takes this on.

⟨measured 2026-09-23 · SCRIP 19b2517d0 (pre-`lines()`-fix) · hq_raku, via direct oracle diff against
/home/resources/rakudo-local/bin/raku⟩
