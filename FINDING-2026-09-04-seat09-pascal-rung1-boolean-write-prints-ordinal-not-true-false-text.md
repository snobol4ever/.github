# FINDING: Pascal `write`/`writeln` on a Boolean prints the raw ordinal (0/1) instead of ISO-required `false`/`true` text

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16), row `pascal-ladder-every-feature-in-isolation-with-variations`, rung1 FORMS mint (`ladder__rung01_var_assign_multi_group`).

## What the rung1 FORMS walk found

Minting rung1's forms (variable declaration + assignment, ISO 7185 §6.5.1/§6.8.2.2) included a form testing two separate `identifier-list : type-denoter` groups in one `var`-block — one `integer`, one `Boolean` — to exercise multiple declaration groups. The Boolean half surfaced an independent, unrelated defect: SCRIP does not format `Boolean` values as text when written.

Minimal repro (ablated from the witness, not the witness itself):

```pascal
program b2;
var
  b: Boolean;
begin
  b := false;
  writeln(b);
  write(b); writeln
end.
```

| | m3 (`--run`) | m4 (`--compile`) | `fpc -Miso` oracle |
|---|---|---|---|
| output (2 lines) | `          0` / `          0` | `          0` / `          0` | `false` / `false` |

SCRIP prints the Boolean's raw ordinal value (0 for false, 1 for true) right-justified with the **default INTEGER field width** — i.e. it is treating a `Boolean` write-parameter exactly like an untyped ordinal/integer, never converting it to the required `false`/`true` spelling. Confirmed for both values and both procedures:

- `writeln(false)` -> SCRIP `0` (integer-width-padded), oracle `false` (no padding — already 5 chars)
- `writeln(true)` -> SCRIP `1` (integer-width-padded), oracle ` true` (one leading space — oracle right-justifies to width 5, matching `false`'s length)
- `write(b)` (not just `writeln`) -> same wrong ordinal — shared mechanism, not writeln-specific, same shape as the sibling rung0 field-width finding (`FINDING-2026-09-04-seat09-pascal-rung0-writeln-field-width-truncation-ignored.md`).

Both SCRIP modes agree with each other and disagree with the oracle identically, so this is a shared write/writeln-parameter dispatch defect, not a per-mode emission divergence.

## Not cured by me

Construct-level defect (write-parameter type dispatch needs a `Boolean` case that emits text, not the value), outside "fixture, xfail, or instrument" scope for a walker seat. Not investigated past the read-only pointer already on file for the sibling defect (`by_name_dispatch.c`/`builtin_ids.h`, write/writeln's own dispatch) — not reopened here since it is the same general area, not a new diagnosis.

## Disposition

`ladder__rung01_var_assign_multi_group` (rank 172) is added to the master **RED on both modes**, by design — THERE IS NO XFAIL. `LADDER.tsv` rung1's FORMS cell (`multi_ident|multi_group|widen`) and STATUS (`RED`) reflect it; `util_ladder_forms_check.py --lang pascal --phase isolation` sees it as declared-and-witnessed (7/7 of what's actually declared across rungs 0-1; the tool's own separate, correct complaint is that rungs 2-11 still have empty FORMS cells — owed work, not a defect). `ask`ed to hq_P with this repro, same as the rung0 finding. Continuing the FORMS walk on rung2 while both cure behind me.
