# FINDING: Pascal `/` (real division) silently truncates like integer division when BOTH operands are integer-typed

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16), row `pascal-ladder-every-feature-in-isolation-with-variations`, rung2 FORMS mint (`ladder__rung02_arithmetic_real_div`).

## What the rung2 FORMS walk found

ISO 7185 §6.7.2.2: *"A term of the form x/y shall be an error if y is zero; otherwise, the value of x/y shall be the result of dividing x by y"* — `/` is defined as real (non-truncating) division regardless of operand type; the existing `ladder__rung02_arithmetic` witness only exercises `+ - * div mod`, never `/`. Minimal repro:

```pascal
program m1;
var
  a, b: integer;
begin
  a := 7;
  b := 2;
  writeln((a / b):0:2)
end.
```

| | m3 | m4 | `fpc -Miso` oracle |
|---|---|---|---|
| output | `3.00` | `3.00` | `3.50` |

**Precisely isolated to integer-typed operands on both sides**, not to `/` in general — checked all four combinations before filing, not assumed:

| expression | SCRIP | oracle |
|---|---|---|
| `real / real` (both literals `7.0`, `2.0`, or both `real` variables) | `3.50` | `3.50` |
| `integer / real` (`7 / 2.0`, or an `integer` variable over a `real` literal/variable) | `3.50` | `3.50` |
| `real / integer` (`7.0 / 2`, mirror of the above) | `3.50` | `3.50` |
| **`integer / integer`** (two integer literals, two integer variables, or one of each) | **`3.00`** | `3.50` |

So the promotion to real division already works correctly the moment *either* operand is real-typed; the defect is specifically that `integer / integer` falls through to (or is emitted as) integer division rather than promoting both operands to real first. Both SCRIP modes agree with each other and disagree with the oracle identically.

## Not cured by me

Construct-level arithmetic/coercion defect — outside "fixture, xfail, or instrument" scope for a walker seat. Not investigated past this characterization; no `src/` grep done this time (the shape — integer/integer falls through to the wrong operator — points at wherever `/` dispatches on operand type, most plausibly near the arithmetic binop lowering/emission rather than runtime dispatch, but that is a guess offered for triage priority, not a diagnosis).

## Disposition

`ladder__rung02_arithmetic_real_div` (rank 174) added to the master **RED on both modes** — THERE IS NO XFAIL. `LADDER.tsv` rung2's FORMS cell and STATUS (`RED`) reflect it. `ask`ed to hq_P with this repro, alongside the sibling `mod`-sign-convention finding from the same rung (`FINDING-2026-09-04-seat09-pascal-rung2-mod-wrong-sign-on-negative-dividend.md`) — two distinct defects, filed separately since they are different mechanisms, found in the same rung's walk. Continuing the FORMS walk on rung3 while both cure behind me.
