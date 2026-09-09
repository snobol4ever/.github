# &FILE / &LINE across -INCLUDE is ONE class behind two Budne reds and my own diagnostics row

**Seat:** hq_S (HQ-SUSTAIN) · **Date:** 2026-09-09 · **Mode:** NONET
**Oracle:** `/home/resources/x64/bin/sbl -bf`, swap stamp `20260909T033439Z` · **Kind:** live oracle
**Status:** MEASURED, NOT CURED — it crosses into the lexer (hq_P's lane). Routed to the ceo.

## Why this is worth one class rather than three rows

Three open items are the same defect seen from three sides:

- csnobol4 **`include`** (red, my Budne A–P slice)
- csnobol4 **`line`** (red, same slice)
- **`snobol4-runtime-errors-do-not-name-the-source-file-or-line`** — the rank-1 row hq_P minted me,
  whose own note says *"the error comes from an -INCLUDE'd file, so the report must name the
  INCLUDED file and ITS line, not the driver's"*.

All three need one thing: **`&FILE` and `&LINE` must track the file and line actually being
compiled, across include boundaries.** Cure that and the diagnostics row gets its data for free,
because the error reporter has nothing better to print today than what these keywords hold.

## Measured semantics — four separate differences

Every line below is a measured `sbl -bf` vs `scrip` pair, not a reading of the manual.

**1. `&FILE` / `&LINE` do not follow the include.** In `include.sno`, inside `line2.sno`, SPITBOL
reports `line2.sno:2`; we report `_inc.sno:4` — the outer file, and the *spliced* line number.
`lineno` in `snobol4.l` is a single counter that is never reset on entering an include, and there
is no per-include file name at all.

**2. `&FILE` / `&LINE` are not restored the way one would guess, and this is the part worth
copying down rather than re-deriving.** After the include ends, SPITBOL keeps reporting
`line2.sno` for statements back in the OUTER file (`line2.sno:3`, then `line2.sno:5`), and reverts
to `_inc.sno:7` only later. Any cure that "saves and restores on pop" will produce a clean,
plausible answer that still disagrees with the oracle. Grade against `sbl`, not against intuition.

**3. `-LINE nnnn "name"` is not implemented.** `snobol4.l:140` is a catch-all
`"-"[^\n]*\n { lineno++; }` that silently discards every control line it does not name — `-LINE`
among them. SPITBOL honours it: after `-LINE 1234 "foo"` it reports `foo:1234`, and after
`-LINE 2000 "foo"` it reports `foo:2000`. We report the physical line of the outer file. This is
the same catch-all that silently discards `-CASE` (see below).

**4. INCLUDE-ONCE IS KEYED DIFFERENTLY, and this one is isolated to a three-line witness.**

```
	OUTPUT = "a"
-INCLUDE "i1.sno"
	OUTPUT = "b"
-INCLUDE "i1.sno "      ← same file, one trailing space
	OUTPUT = "c"
-INCLUDE "i1.sno"
	OUTPUT = "d"
END
```

`sbl  -> a, in-inc, b, in-inc, c, d`  (the padded spelling is a DISTINCT key, so it includes again)
`scrip -> a, in-inc, b,          c, d`  (we trim trailing blanks, then key on the RESOLVED PATH)

⛔ **The two keys are not interchangeable and the difference cuts both ways.** SPITBOL's raw-string
key includes the same file twice under two spellings. Our resolved-path key would refuse to include
a file reached as `x.sno` and as `dir/x.sno`, where SPITBOL would include it twice. Anyone changing
this must measure the second direction too — it is the one no current test exercises.

## Why I did not cure it

`&FILE`/`&LINE` are keywords and mine, but the mechanism is entirely in `src/parsers/snobol4/snobol4.l`
— the include stack, `lineno`, and the control-line rules — which is hq_P's lane by
`CLAUDE.md`'s own boundary. Two further constraints:

- Per-include file tracking wants a name alongside `incl_start_stack`, and **a new global needs
  Lon's explicit word**, which I do not have.
- Changing the include-once key changes the behaviour of every program that uses `-INCLUDE`,
  including SPITCORE. That is not a local cure at this hour and before an announcement.

## Adjacent, same catch-all, separately routed

`case1` (also my slice) is the control line `-CASE 1`, discarded by that same `snobol4.l:140`
catch-all. SPITBOL folds names read AFTER it: `-CASE 1` then `output = .bb` prints `BB`. We leave
folding off. Curing it means compile-time case folding SCRIP has never had — it is documented as
case-sensitive by design — so it is a design question, not a defect to patch quietly.

Measured: only the UPPERCASE `-CASE` with argument `1` turns folding on. `-case 1`, `-CASE 0`,
`-case 0` and a bare `-case` all leave it off, and we agree with the oracle on all four. So the
gap is exactly one spelling, and a cure must not "fix" the other three.
