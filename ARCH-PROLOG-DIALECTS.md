# ARCH-PROLOG-DIALECTS.md — one Prolog front end, two dialects, one record

**Minted 2026-10-10 by hq_prolog on the ceo's ruling CEO-1632** (approving the design asked under row
`prolog-a-swi-dialect-program-reads-a-double-quoted-text-as-a-string-object-as-swipl-does-the-gnu-dialect-as-codes-ceo-1599`;
CEO-1605 for display/1). SCRIP's Prolog is the ISO superset (CEO-391): ISO is the core, every non-conflicting GNU and SWI builtin
is added, and where the two oracles CONFLICT the program's own dialect decides. There is no command-line switch, ever (RULES.md
ONE ORACLE, ONE FEATURE SET).

## 1. The dialects and their oracles

| dialect | what makes a program this dialect | oracle |
|---|---|---|
| **GNU / ISO** (the default) | no SWI marker in its tree | GNU Prolog 1.6.0 (`scripts/oracle_gprolog.sh`, `oracle_gplc.sh`) |
| **SWI** | its own tree carries an SWI marker (§ 2) | SWI-Prolog 9.0.4 |

## 2. The rule and its markers — grown by measurement, never by taste

A program is SWI when its own source tree carries a construct the GNU oracle REFUSES OR DOES NOT READ; otherwise it is GNU/ISO.
The principle is the ceo's (CEO-1632), the same as Pascal's dialect switch (CEO-1624). MEASURED by the ceo on gprolog 1.6.0 and
swipl 9.0.4:

- a `:- module/2` directive: gprolog warns and does not read it, swipl runs the program;
- a `:- use_module/1,2` directive: GNU Prolog has no module system;
- an SSU rule (`Head => Body`): a syntax error for gprolog, runs under swipl.

A dict or a quasi-quotation joins the set by the same measurement once SCRIP reads them. A marker counts only in the program's
own clauses (`PlClause.lineno` non-zero): the prelude and the vendored libraries never decide a program's dialect. Once one file
of a program is SWI the program is (the record is ORed across the files the driver lowers).

**Where it is decided:** the lowerer, from the tree, in prolog_lower.c's first pass over the clauses (`pl_dq_lower_program`, the
pass that already reads the double_quotes directives) — A PARSER MOVES NOTHING. **Where it lives:** `g_stage2.pl_dialect_swi`,
beside `g_stage2.pl_dq_mode` (one struct per stage, never a bare global).

## 3. The switches on the record

1. **The double_quotes default.** SWI: `"abc"` is a string object (string/1 true, string_concat/3 and format's `~s` take it, as
   swipl does). GNU/ISO: a code list. An explicit `:- set_prolog_flag(double_quotes, X)` in the program wins in either dialect.
2. **display/1** (CEO-1605). SWI: library(edinburgh)'s — `write_term(T, [quoted(true), ignore_ops(true)])`, through the prelude's
   `'$display_swi'/1`, to which the lowerer rewrites a static `display/1` call. GNU/ISO: the builtin, operators ignored and atoms
   not quoted.

A later conflict between the oracles is one more switch on the same record, ruled the same way.

## 4. The package contract — markerless programs whose refs swipl cut

A package whose refs were cut by swipl but whose programs carry no marker (the 15 ProRosetta programs of
ARCH-PASCAL-PROLOG-PROGRAM-SOURCES.md § 4.3) gets `:- set_prolog_flag(double_quotes, string).` from its suite runner's directive,
as the Logtalk runner sets `iso` (CEO-1272: conflicts go through ISO's own flags, set by the program or by a suite runner). It is
the package's contract with the oracle that cut its refs, one line in the coo's runner.

## 5. Reach at the ruling (files carrying a marker / files shipped)

swi_tests 207/231 · puzzles 406/409 · trealla_tests 135/457 · rosetta-prolog 125/787 · gnu_prolog 1/107 · logtalk_iso 0/20 ·
inriasuite 0/2 · tests/prolog 1/34 · demos: chat80, advent, prolog_recognizer.
