# FINDING — s140 trio literal-arg baseline + treebank defer-structure experiment

**Date:** 2026-07-24  **Session:** s140  **Author:** Claude Sonnet 4.6

## Directed change (Lon): literalize all pattern primitive arguments in trio -match programs

claws5-match.sno: `ANY(&UCASE)` → `ANY('ABCDEFGHIJKLMNOPQRSTUVWXYZ')`, `SPAN('0123456789' &UCASE)` → `SPAN('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')` — eliminates keyword-variable runtime fetch inside cset_fold path.
json-match.sno: `ANY(hex)` ×4, `SPAN(dig)` ×3, `ANY('\"/bfnrt' bslash)` and `BREAK('\"' bslash ...)` all replaced by fully-literal string args — eliminates variable-variable concatenation at pattern construction; `bslash`/`hex`/`dig` helper vars kept as dead code to avoid structural change.
treebank-match.sno: NO CHANGE — all primitive args were already literals.

## Baseline of record (honest, compliant sources, rep100 ×7 interleaved medians, RT_OPT=-O0)

| prog (rep100) | sbl (ms) | m3 (ms) | m4 (ms) | m4 vs sbl |
|---|---|---|---|---|
| json | 173 | 170 | 141 | SCRIP **1.23× win** |
| treebank | 77 | 82 | 81 | SPITBOL 1.05× ahead |
| claws5 | 24 | 19 | 19 | SCRIP **1.26× win** |

## Experiment: treebank structural inlining (NOT committed to corpus)

As a separate measurement (later reverted), `delim`/`word` were inlined at every use and `ARBNO(*group)` → `ARBNO(group)` — same language recognized, reduced indirection depth. Results (rep100 ×7 medians, same container):

| prog | sbl | m3 | m4 |
|---|---|---|---|
| treebank-inlined | 68 | 57 | 57 |

SCRIP m4 improvement: 81→57ms (−30%). SPITBOL improvement: 77→68ms (−12%).  
**Interpretation:** SCRIP pays ~24ms for the defer+variable-indirection machinery that sbl pays ~9ms for — a 2.7× ratio isolated to the `*group`/`*delim` wiring. This is the quantified prize for the patchable-γ/ω + ARBNO-fill engine rungs directed by Lon.

## bbprof profile (treebank rep100 m3, 19 samples)

58% IR_MATCH_ARBNO (inner `ARBNO(SPAN (*group|word))` iteration) · 10% IR_MATCH_DEFER · 10% IR_MATCH_BREAK · 10% IR_MATCH_SEQUENCE · 5% SPAN · 5% ALTERNATE.

Primary target: ARBNO β-arm 21-quad zero-fill per iteration (same rep-stosb disease as s139 NOFILL, different site) + defer return-glue double-hop L(4)/L(5).

## callgrind status

SIGSEGV under valgrind both m3 and m4 at HEAD in this container — a regression since s135 where callgrind worked. Confirmed with both `SCRIP_NO_SEGV_HANDLER=1` and `SCRIP_BBPROF_US` variants. Not investigated further; native bbprof delivered sufficient signal.

## SCRIP_BBPROF_MAP

New env gate in bbprof.c (SCRIP `7d950fbd`): `SCRIP_BBPROF_MAP=1` dumps `[BBMAP] lo hi IR_KIND nid uid` lines to stderr at report time — allows joining box address ranges with callgrind cost-line output for per-instruction attribution when callgrind is functional.
