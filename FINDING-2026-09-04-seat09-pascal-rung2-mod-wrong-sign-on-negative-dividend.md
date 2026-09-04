# FINDING: Pascal `mod` uses C-style sign-follows-dividend convention instead of ISO 7185's required non-negative result

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16), row `pascal-ladder-every-feature-in-isolation-with-variations`, rung2 FORMS mint (`ladder__rung02_arithmetic_mod_neg`).

## What the rung2 FORMS walk found

ISO 7185 §6.7.2.2 gives `div`/`mod` a precise mathematical definition, not "whatever the host CPU's instruction does": *"A term of the form i div j shall be an error if j is zero; otherwise... `abs(i) - abs(j) < abs((i div j) * j) <= abs(i)`... the sign of the value shall be positive if i and j have the same sign and negative if i and j have different signs"* (truncating division, toward zero) and *"A term of the form i mod j shall be an error if j is zero or negative; otherwise, the value of i mod j shall be that value of (i-(k*j)) for integral k such that `0 <= i mod j < j`"* — i.e. for a positive `j`, `mod`'s result is **always non-negative**, regardless of `i`'s sign. This is the classic point on which C-derived `%`/`mod` implementations (sign follows the dividend, can be negative) diverge from ISO Pascal.

Existing `ladder__rung02_arithmetic` only exercises `div`/`mod` on two positive operands (`6 div 4 = 1`, `6 mod 4 = 2`), which cannot distinguish the two conventions — exactly the "witness whose expected answers are all the easy case" trap THE LADDER RECIPE point 2 warns about. Testing a negative dividend separates them. Minted as two SEPARATE witnesses (not one), because they disagree — `div` is fine, `mod` is not:

```pascal
program m1;
var
  i: integer;
begin
  i := -7;
  writeln(i div 2)   { -3, correct in both  }
end.
```
```pascal
program m2;
var
  i: integer;
begin
  i := -7;
  writeln(i mod 2)   { the divergent one }
end.
```

| | m3 | m4 | `fpc -Miso` oracle |
|---|---|---|---|
| `-7 div 2` | `-3` | `-3` | `-3` — **matches** |
| `-7 mod 2` | `-1` | `-1` | `1` — **defect** |

`div`'s truncating-toward-zero behavior is already correct. `mod` returns `-1` (the C `%` answer: `-7 = (-3)*2 + (-1)`) where ISO requires the non-negative representative in `[0, 2)`, which is `1` (`-7 = (-4)*2 + 1`). Both SCRIP modes agree with each other and disagree with the oracle identically — a shared arithmetic-lowering defect, not a per-mode emission divergence.

## Not cured by me

Construct-level arithmetic semantics defect — outside "fixture, xfail, or instrument" scope for a walker seat. Likely shares a code path with `div` (same operator family) but is NOT the same bug as the sibling `/`-truncation finding from this same rung (`FINDING-2026-09-04-seat09-pascal-rung2-real-division-truncates-like-integer-division.md`) — `div` itself is correct here, only `mod`'s sign handling is wrong. No `src/` investigation done past this characterization.

## Disposition

`ladder__rung02_arithmetic_mod_neg` (rank 176) added to the master **RED on both modes** — THERE IS NO XFAIL; `ladder__rung02_arithmetic_div_neg` (rank 175, the correct sibling) is green and stays in the master as a positive regression witness for `div`'s truncation behavior specifically, so a future change to `mod` cannot accidentally break `div`'s already-correct handling without being caught. `LADDER.tsv` rung2's FORMS/STATUS reflect both. `ask`ed to hq_P. Continuing the FORMS walk on rung3 while this cures behind me.
