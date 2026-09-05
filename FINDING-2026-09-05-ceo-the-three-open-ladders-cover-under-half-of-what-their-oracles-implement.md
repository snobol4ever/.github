# FINDING 2026-09-05 (ceo, 2026-09-05 14:33 CDT) — the three open ladders cover under half of what their oracles implement; every gap is now a declared, red rung

**Lon, in-chat to ceo, verbatim:** *"Has the three ladders and rungs for SNOBOL4, Icon, and Prolog been completely flushed out? Are the ladders complete? Are their rungs for every feature? If not ensure that each ladder is full and complete."* · *"I suspect that our master suites and test ladders are SEVERELY lacking since the evidence is we are only 50% passing the industry standard tests."*

## Method — the census comes from the oracle, not from a reading of the manual
A ladder is complete when every feature THE ORACLE IMPLEMENTS is named by a rung's CONSTRUCT, a FORM, or a witness origin. Coverage was measured by name (case-insensitive whole-word match over `config/LADDER.tsv` plus every `ladder__rungNN_*` origin in `ALL.csv`) — an undercount where a witness exercises a feature it does not name, and exactly the right count for a ladder whose FORMS column IS the census.

| language | reference census | how it was cut | implemented by the oracle | named by the ladder before | uncovered |
|---|---|---|---|---|---|
| SNOBOL4 | SPITBOL manual v3.7 Ch19 function headings (131) | one program per name, `X = NAME()` under `&ERRLIMIT`, run through `/home/resources/x64/bin/sbl -bf`; ERR 22 = undefined function | 81 (the 50 undefined are the DOS screen / PEEK / POKE / SOUND set) | 38 | **43** functions + BAL, SUCCEED + the `?` `~` operators and OPSYN extensions |
| SNOBOL4 keywords | the 43 `&NAME`s the manual uses | `X = &NAME` under `&ERRLIMIT`; 251 = not a keyword | 39 (STFCOUNT PARM UPPERS LOWERS raise 251) | rung14 carried ONE witness (&STCOUNT &ANCHOR &ALPHABET) | **36** |
| Icon | `refs/icon-master/src/h/fdefs.h` (150 functions), `kdefs.h` (64 keywords), `odefs.h` (44 operators) — the runtime's own tables | `&features` of iconx v9.5.25a: UNIX, ASCII, co-expressions, dynamic loading, environment variables, external values, keyboard functions, large integers, pipes, system function — **no Graphics**; `WOpen` raises run-time error 106 | 95 non-graphics functions + keyboard | 55 functions, 20 keywords | **40** functions, **44** keywords, co-expression operators |
| Prolog | ISO/IEC 13211-1 §7.8, §8.2–8.17, §9 — 130 features listed by section (the INRIA suite's 64 family files are a subset and read 0 real gaps by name) | section census against the ladder | 130 | 92 | **38** |

## What landed (corpus `6e84528bf` + `6bd5aea03`)
- **SNOBOL4 rungs 24–33 DECLARED (PENDING):** primitive patterns complete · comparison predicates · string functions · real arithmetic and math · unevaluated expressions and program-defined operators · I/O and control statements · system/environment/storage · SORT/RSORT and conversion · error handling and limits · recursive patterns, FULLSCAN, NRETURN. rung14's FORMS extended to the 39 accepted keywords.
- **Icon rungs 38–42 DECLARED (MISSING):** co-expressions · numeric and bit functions · string functions completing the set · files and the run-time system (keyboard functions included) · keywords. **rung43 graphics EXCLUDED by the oracle's own feature list**, recorded as a comment in the file — outside THE ORACLE is outside 100% until Lon says otherwise.
- **Prolog rungs 14–18 DECLARED (RED):** evaluable functors complete (§9) · stream/char/byte I/O complete (§8.11–8.13) · term I/O complete (§8.14) · term_variables, current_predicate, number_chars, halt · ISO error terms (§7.12).
- **The instruments read them:** `test_snobol4_ladder.sh --to 33` REFUSES rc=2 naming rungs 15–33; `util_ladder_forms_check.py` reads snobol4 126 · icon 54 · prolog 42 declared slots without a witness. The ladders are complete by declaration and red by build — which is the instrument, not a defect of it.

## Why the boards read ~50% while the masters read green
The masters and ladders were built by walking what had been written, not by censusing what the oracle implements; a green master over a population that names half the language is the missing-denominator defect at the scale of the whole suite. The package suites (csnobol4 60/119, arizona 43/89, jcon 43/81, INRIA 275/445) are the only boards whose denominator is the standard's, and they read what they read.

## Owed
- seat09 (hq_P) walks SNOBOL4 rungs 24–33 and rung14's keyword forms in order; seat01 (hq_B) walks Icon 38–42; seat05 (hq_C) walks Prolog 14–18 — one rung per claim, refs cut from the oracle, both modes, forms then pairs.
- hq_T (the standard): the oracle-census probe becomes a permanent instrument — `util_ladder_census_vs_oracle.py <lang>` — and a gate arm that reds when the ladder names fewer features than the oracle implements; the ceo's probe recipe above is the seed. The same census is owed for Snocone, Pascal, Raku and Rebus when they open.
