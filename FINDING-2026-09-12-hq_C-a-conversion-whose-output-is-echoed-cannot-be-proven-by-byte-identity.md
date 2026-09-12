# FINDING — a conversion whose output is ECHOED cannot be proven by byte-identity, and the obvious cure is the one that breaks it

**Seat:** hq_C · **Date:** 2026-09-12 · **Row:** `snobol4-twelve-spitbol-tests-hold-code-inside-evaluated-string-literals` (CEO-571)
**Trees:** SCRIP `602e51f7a` · corpus `5b6dd7ab2` · oracle `/home/resources/x64/bin/sbl`
**Instrument:** `SCRIP/scripts/test_gate_spitbol_x64_case_conversion_is_oracle_equivalent.sh` — `PASS=36 FAIL=0 of 36`, 3s, no build.

## The row as briefed, and the half of it that was wrong

CEO-571 converted 24 of 36 `spitbol_x64_tests` to upper-case builtins and left twelve, with the reason
measured: nine math tests assert with `chks('sqrt(2.63e-308)', ...)`, so **the builtin name lives inside a
string that is `EVAL`'d**. Under folding it resolves `sqrt`→`SQRT`; under `-bf` it is undefined and all 616
lines become `Obs[undefined function called]`. The brief's implied cure was to uppercase inside the literal
once a seat decided which strings are code.

⛔ **That cure is provably wrong, and the proof is the same instrument that grades the row.** `chks` **echoes
the expression string** into every result line it prints. Uppercasing `sqrt(` to `SQRT(` changes 616 lines of
*output*, so the converted file no longer agrees with upstream's folding run — the conversion fails the very
equivalence it exists to preserve.

✅ **The cure is `OPSYN('sqrt','SQRT')`**, one line per file: the lower-case name becomes a real name, and the
printed text is byte-identical to upstream's. Nine files, nine one-line aliases.

⭐ **THE GENERAL FORM: a source token that is also echoed output has two roles, and a rewrite can only serve
one.** Ask of any mechanical source transform: *does anything print this token back?* If yes, the transform
must go through a **binding** (an alias, a synonym, an indirection) rather than through the **spelling**.
`math_sqrt.sbl` shows both roles in adjacent arguments of one call — `'sqrt(...)'` is code, and the expected
value `'sqrt argument negative'` is genuine `&ERRTEXT` data that must not be touched. No blanket rule over
string literals can separate them, which is exactly why the twelve were left for a seat.

## A missing word in a converter's list reports as "this file needed nothing"

`module.sbl` is one statement, `exit(-3,'module.out')`. `util_uppercase_snobol4_builtins.py` printed **`0`** on
it. **`EXIT` was absent from its builtin list** — so a file it could not convert *at all* produced the exact
report of a file that needed no conversion. The miss surfaces only downstream, as `ERROR 022 -- undefined
function called` under `-bf`.

⭐ **A word-list instrument fails silently on its own gaps, in the direction that looks like success.** The
count it prints answers *how many names I recognised*, read as *how much this file needed*. Same family as
`command -v` answering *is it on PATH* when asked *does it exist*. The verdict must come from the oracle
comparison, never from the converter's own count. `EXIT` added, with the lesson in the docstring.

## One program cannot be made invariant, and it says so itself

`gcbuster.sbl` sets `&DUMP = 1`, so SPITBOL dumps the symbol table and every keyword on exit. Three findings:

1. **User identifiers ARE output here.** The folding arm printed `BASEMEM`, ours printed `basemem`. The
   converter's standing rule — *user identifiers keep their case, case-sensitivity does not disturb them* —
   is **false in any program that dumps, traces, or reflects over its own symbol table**. Uppercased.
2. **`&CASE` is the folding flag the two arms differ in BY CONSTRUCTION** (`1` vs `0`). ⭐ **A program that
   reports its own invocation can never be made invariant under that invocation.** Converting the source
   harder never closes this line; recognising it is the only move.
3. **`BASEMEM`/`TOPMEM` are `HOST(-1,2)`/`HOST(-1,3)` — raw heap addresses.** Measured: three consecutive runs
   of the **unmodified vendored** source under the **same** binary print three different values. ⛔ **The
   original arm is not byte-identical to ITSELF**, so this was never a conversion defect and no `.ref` could
   have pinned it either. Had it been met only as a red diff on the converted file, the obvious reading is
   "my edit broke it" — and every further edit would have been chasing a property of ASLR.

The gate normalizes exactly those two cells, **on both arms, anchored to whole lines, and printed in the
verdict**. Everything else in the dump is compared byte-for-byte — which is what caught (1).

## What the instrument is worth

⛔ **It did not exist.** CEO-571's proof was run by hand and written into a commit message, so nothing on disk
could re-prove it or catch a regression. A proof described in prose is not an instrument: it grades the tree
it was typed about and no other.

⭐ **A gate that only ever went green is not known to discriminate.** This one was watched **both ways**: red
at 24/36 before the cures, green at 36/36 after, and red again under three separate one-character mutations —
including one *inside* gcbuster's dump, which proves the normalization did not blind it. Watching it go both
ways is what separates a gate from a decoration.

⛔ It uses `sbl_correctness_bin()`, not `sbl_clean_bin()`. The clean **bench** binary cannot case-fold at all
(`lib_oracle_flags.sh`, SECOND DIVERGENCE AXIS), so the folding arm would have been a no-op and the entire
comparison silently vacuous — a full, plausible, all-green table proving nothing.

## Housekeeping, recorded because it was invisible

`a.spx`, `module.out` and `save.spx` were tracked in the package. They are what `sv.sbl`, `module.sbl` and
`save.sbl` **write** — swept into the CEO-571 commit by a proof run in a dirty working tree, and never in the
declared population in `_PROVENANCE.md`. Removed. ⭐ **A proof run that writes into the tree it is proving
leaves its droppings looking like fixtures**; the gate now stages every run in its own fresh copy.
