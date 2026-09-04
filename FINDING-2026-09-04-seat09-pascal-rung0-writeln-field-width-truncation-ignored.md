# FINDING: Pascal write/writeln field-width TRUNCATION is silently ignored for string literals (padding works, truncation does not) — real defect, isolated to a 4-line witness

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16), row `pascal-ladder-every-feature-in-isolation-with-variations`, rung0 FORMS mint (`ladder__rung00_hello_width`).

## What the rung0 FORMS walk found

Filling rung0's FORMS column from ISO 7185 §6.9.4 (writeln) / §6.9.3 (write, which defines `write-parameter`'s field-width syntax that writeln's own parameter list reuses) named a form neither of the prior single witnesses (`ladder__rung00_hello`) exercised: a field-width specifier on a string-literal argument, `'text':N`. §6.9.3's own text names both directions explicitly: *"if 1 <= TotalWidth <= n, the first through TotalWidth-th characters [are written]"* (truncation, N < length) and the standard padding-to-width behavior for N > length. The witness (`corpus/tests/pascal/ALL.pas` origin `ladder__rung00_hello_width`, rank 170) tests both in one 5-line program; its `.ref` is cut from the real `fpc -Miso` (FPC 3.2.2) oracle, not hand-typed.

**PADDING is correct. TRUNCATION is not.** Confirmed on the minimal 4-line isolation (not the master witness itself, ablated further for this report):

```pascal
program m1;
begin
  writeln('abcdef':3)
end.
```

| | m3 (`--run`) | m4 (`--compile`) | `fpc -Miso` oracle |
|---|---|---|---|
| output | `abcdef` | `abcdef` | `abc` |

Both SCRIP modes print the full, untruncated string; the width specifier is silently dropped whenever it is **narrower** than the string, in both modes identically (so this is a shared write/writeln-parameter code path, not a per-mode emission divergence — no asm diff needed to see it, the wrong answer is byte-visible). Further characterized, not just the one point:

- `'ab':5` (padding, N > length) → SCRIP `   ab`, oracle `   ab` — **matches**, both modes.
- `'abcdef':3` (truncation, N < length) → SCRIP `abcdef`, oracle `abc` — **defect**, both modes.
- `'abcdef':0` (truncation to zero) → SCRIP `abcdef`, oracle empty string (blank line) — **defect**, both modes.
- `write('abcdef':3)` (not just `writeln`) → same wrong `abcdef` — confirms the mechanism is shared between `write` and `writeln`, not writeln-specific.

## Not cured by me

This is a construct-level runtime/emission defect (field-width truncation logic), outside "fixture, xfail, or instrument" scope for a walker seat (`MASTER-PLAN.md` § THE 16-SEAT CUT: "cure only what is fixture-, xfail-, or instrument-level; a seat that finds itself editing `src/` ... hands the class to its HQ"). Not investigated past a read-only grep: `src/runtime/by_name_dispatch.c` and `src/runtime/builtin_ids.h` are where `write`/`writeln` dispatch by name (found via `grep -rln width src/runtime`, not read in depth) — a pointer for whoever cures this, not a diagnosis. Likely a shared node (both `write` and `writeln`, both modes) — hq_P's own call whether it routes to hq_C under § SHARED-NODE VERDICT SCOPE or stays in the Pascal lane; SNOBOL4/Icon output procedures use different field-width conventions (`$(...)` vs Pascal's `:N` — not the same grammar), so it may not actually share a node with them despite being shared across write/writeln within Pascal.

## Disposition

`ladder__rung00_hello_width` (rank 170) is added to the master **RED on both modes**, by design — THERE IS NO XFAIL. `LADDER.tsv`'s rung0 FORMS cell (`width`, among four forms minted this pass: `paramlist|blank|multi|width`) and `util_ladder_forms_check.py --lang pascal --phase isolation` both correctly see it as declared-and-witnessed; the ladder runner's own `--only 0`/`--to 0` will read rung0 as **not yet green** until this cures, which is the intended signal, not a harness bug (contrast the false "eleven reds" in the sibling FINDING this session already corrected once for a different reason). `ask`ed to hq_P with this repro. Continuing the FORMS walk on rungs 1-11 while this cures behind me, per THE LADDER RECIPE point 6 ("keep minting ahead on the next disjoint family while the HQ cures behind it").
