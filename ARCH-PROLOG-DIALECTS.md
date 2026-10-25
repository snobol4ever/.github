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
| **XSB** (§ 6, 2026-10-24) | its own tree carries an XSB marker (`:- import P from M.`, `:- compiler_options(L).`, `:- index/2-3`, `:- hilog`, `:- ti`), which outranks an SWI marker | XSB 5.0.0 (CEO-1927/1958; `xsb_bin` in `lib_oracle_flags.sh`) |

## 2. The rule and its markers — grown by measurement, never by taste

A program is SWI when its own source tree carries a construct the GNU oracle REFUSES OR DOES NOT READ; otherwise it is GNU/ISO.
The principle is the ceo's (CEO-1632), the same as Pascal's dialect switch (CEO-1624). MEASURED by the ceo on gprolog 1.6.0 and
swipl 9.0.4:

- a `:- module/2` directive: gprolog warns and does not read it, swipl runs the program;
- a `:- use_module/1,2` directive: GNU Prolog has no module system;
- an SSU rule (`Head => Body`): a syntax error for gprolog, runs under swipl.

- a dict literal (`Tag{K:V}`) or a dict dot (`D.key`) -- since SCRIP reads them (SCRIP 77743fbfc), MEASURED by hq_prolog
  2026-10-11: gprolog 1.6.0 stops at `syntax error: . or operator expected after expression`, swipl runs it (the cfo's suggestion).

A quasi-quotation joins the set by the same measurement once SCRIP reads it. A marker counts only in the program's
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
3. **print/1 and print/2** (CEO-1663, row prolog-print-quotes-in-the-swi-dialect-...). MEASURED by hq_prolog 2026-10-11: swipl
   prints `'A b'` and `[a,'B',"s"]` (its print/1 is `write_term(T, [portray(true), numbervars(true), quoted(true)])`), gprolog
   1.6.0 prints `A b` and `[a,B,[115]]` (portray and numbervars, unquoted). With no `portray/1` defined and no program `print/N`,
   the lowerer rewrites a static call to `writeq` in SWI and to `write` in GNU/ISO, so the GNU arm costs nothing over write/1
   (`test_gate_pl_print_1_honours_portray_and_costs_nothing_without_it.sh` arm 1). With a `portray/1` the portray road is
   unchanged in both. `call(print, X)` and `maplist(print, L)` resolve statically and quote too (measured); format's `~p`
   still prints unquoted in SWI (swipl quotes), as does a goal whose name is only known at run time: the dialect is a
   compile-time record, and a run-time `'$dialect'` flag is the cure that would reach those.

4. **THE LIST CONSTRUCTOR** (hq_runtime's ProRosetta catamorphism-6 and hq_snobol4's TreallaTests issues_old_test0046, 2026-10-25; ruled by the cto
   08:4x CDT). MEASURED on swipl 9.0.4 against SCRIP 51d399df7 in the SWI dialect: `functor([a],N,A)` gives `'[|]'/2` (SCRIP `'.'/2`); `[a|b] =.. L`
   gives `['[|]',a,b]`; `T =.. ['[|]',x,[]]` gives `[x]` (SCRIP an ordinary compound `'[|]'(x,[])`); `'[|]'(p,q) = [_|_]` succeeds; `is_list('[|]'(1,[]))`
   succeeds; `compound_name_arity([a],N,A)` gives `'[|]'/2`. GNU, ISO and XSB keep `'.'/2`, as SCRIP does today. THE RULE: the cons cell's REPRESENTATION
   does not change (one list cell type in every dialect, no new descriptor); its NAME is a column of the dialect record, `'[|]'` in SWI and `'.'` elsewhere,
   read through ONE accessor at the three roads that spell a cons by name -- the lowerer reading a source term `Name(H,T)` with the dialect's list name
   builds the cons; `=..`, `functor/3`, `compound_name_arity/3` and `compound_name_arguments/3` build a cons from that name at arity 2 and decompose a cons
   to it; `write`, `print` and `writeq` of a cons keep list syntax. In the SWI dialect `'.'(a,b)` is then an ordinary compound (swipl 7+); in the others
   `'[|]'(a,b)` is. BUILDER: hq_runtime (catamorphism-5 and -6 first, issues_old_test0046 second, both modes against swipl; the SWI core files hq_packages
   grades carry the same red and re-grade with it), the Prolog smoke before the push.

A later conflict between the oracles is one more switch on the same record, ruled the same way.

## 4. The package contract — markerless programs whose refs swipl cut

A package whose refs were cut by swipl but whose programs carry no marker (the 15 ProRosetta programs of
ARCH-PASCAL-PROLOG-PROGRAM-SOURCES.md § 4.3) gets `:- set_prolog_flag(double_quotes, string).` from its suite runner's directive,
as the Logtalk runner sets `iso` (CEO-1272: conflicts go through ISO's own flags, set by the program or by a suite runner). It is
the package's contract with the oracle that cut its refs, one line in the coo's runner.

## 5. Reach at the ruling (files carrying a marker / files shipped)

swi_tests 207/231 · puzzles 406/409 · trealla_tests 135/457 · rosetta-prolog 125/787 · gnu_prolog 1/107 · logtalk_iso 0/20 ·
inriasuite 0/2 · tests/prolog 1/34 · demos: chat80, advent, prolog_recognizer.

## 6. THE XSB DIALECT: the third value of the one record, grown from five measured differences (hq_icon's ask under the XsbTests row, 2026-10-24 22:4x; ruled by the cto 2026-10-24 23:0x CDT under CEO-1964 and CEO-1958)

**MEASURED (XSB 5.0.0 `/home/resources/prologs/xsb/XSB/bin/xsb`, gprolog 1.6.0, swipl 9.0.4, SCRIP 0d3a92f14 in both of its dialects):**

| fact | XSB | GNU | SWI | SCRIP today (SWI arm / GNU arm) |
|---|---|---|---|---|
| `X is 1/3, write(X)` | `0.333333333333333` (15 significant digits) | `0.33333333333333331` (17) | `0.3333333333333333` (shortest round trip) | shortest / shortest |
| `X is 4/2` (two integers, exact) | `2.0` | `2.0` | `2` | `2` / `2` |
| `0.1+0.2`; `1.0e17`; `1.5e-7` | `0.3`; `1.0e+17`; `1.5e-07` | `0.30000000000000004`; `1.0e+17` | `0.30000000000000004`; `1.0e+17` | swipl's / swipl's |
| `current_prolog_flag(max_integer, M)` | `9223372036854775807` (min `-9223372036854775807`, `bounded` true) | `1152921504606846975` | no such flag (unbounded) | fails / `domain_error(prolog_flag, max_integer)` |
| `2 ** 64` | wraps to `-9223372036854775808` | error | bignum | bignum |
| `functor(f(a,b), M, N, A)` | `functor(f(a,b), usermod, f, 2)`, reached only by `:- import functor/4 from standard.` | none | `functor(T, Name, Arity, Type)` | swipl's / none |
| `compile(F)` | compiles, loads nothing | -- | consults (quintus) | consults |
| `double_quotes` default | `codes` | `codes` | `string` | the package prelude forces `string` (CEO-1712, written for swipl's refs) |
| `print/1` | does not exist (`existence_error`) | exists | exists | exists |
| `:- import P from M.` / `:- compiler_options(L).` | read | gprolog refuses (no output) | `Syntax error: Operator expected` / `Unknown procedure: compiler_options/1` | parsed through CEO-1958's operator lines |

Every XsbTests red hq_icon names (float_tests_roots, roots_int_comp, arith_op, n2c, residualAttv, tab_constraint, functor4_tests, test_ascii_*) is one of these rows. The GNU arm carries the same first two divergences against gprolog (a GNU red class of its own, re-graded by the coo when the column lands).

**THE RULE.** XSB is the THIRD VALUE of the ONE dialect record of § 2 -- compile-time `g_stage2`'s dialect (today two booleans, `pl_dialect_gnu` and `pl_dialect_swi`, which become reads of ONE three-valued field; `pl_gnu_dialect()`, `pl_swi_dialect()` and a new `pl_xsb_dialect()` the runtime's reads) and the run-time flag `'$dialect'` the lowerer bakes in (`gnu`, `swi`, now `xsb`; `--dialect=xsb` beside `--dialect=gnu` for a program with no marker). Never a fourth switch, never a per-builtin flag.

1. **THE MARKERS, by § 2's measurement.** A program is XSB when its own clauses carry a construct BOTH other oracles refuse: `:- import P from M.`, `:- compiler_options(L).`, `:- index/2` and `:- index/3`, `:- hilog`, `:- ti` (swipl: a syntax error or an unknown procedure; gprolog: refused). **`:- export P.` and `:- index/1` ARE NOT MARKERS (hq_icon, 2026-10-25, measured):** swipl 9 accepts `:- export(foo/0).` as its own export/1 and `:- index(foo/1).` as a deprecated declaration with no effect, so neither is refused by both; SCRIP's polyglot programs declare their exports with `:- export(name/arity)` (demos/prolog/family_prolog.pl, family_net, tests/prolog/linker/ancestor, swi_tests core test_call.pl), and the first cut (SCRIP 8cbf19b8f) read those as XSB -- the coo's frame census showed it as family_prolog g0 growing 192 to 576 excess; the cure drops both from `pl_xsb_marker`. An XSB marker outranks an SWI marker in the same tree (a tree carrying XSB's directives is XSB whatever else it carries); otherwise the SWI marker decides, otherwise GNU/ISO. The reader's four operators (`import fy 1050`, `export fx 1100`, `from xfx 1040`, `index fy 1100`) stay the package prelude's lines under CEO-1958, because the marker directive must PARSE before the lowerer can read it -- A PARSER MOVES NOTHING. **THE PACKAGE CONTRACT (§ 4):** `xsb_tests/ALL.prelude` drops its two SWI lines (`:- use_module(library(lists)).` and `:- set_prolog_flag(double_quotes, string).`, both written for swipl's refs) and carries ONE marker, `:- compiler_options([]).`, so a program with no import or export line of its own is XSB too; XSB's `double_quotes` default is `codes`, and a program's explicit flag still wins.
2. **THE FLOAT WRITER is a column with three values and ONE writer.** `write`, `print`, `writeq`, `write_canonical` and `format`'s `~w` print a float through one function with a per-dialect precision: SWI shortest round trip (today's), XSB `%.15g`, GNU `%.17g`, each followed by the same rule the three oracles share: a mantissa with no `.` gets `.0` inserted before the exponent or at the end (`2.0`, `1.0e+17`, `1.5e-07`). Three writers, or a per-call test, are refused.
3. **INTEGER DIVISION is a column.** `/` on two integers: SWI the integer when exact (iso false), a float otherwise; XSB and GNU always a float. `//`, `mod`, `rem`, `truncate` agree across the three and stay.
4. **THE FLAG TABLE is per dialect.** `current_prolog_flag/2` answers `max_integer`, `min_integer` and `bounded` from the dialect's row (XSB 9223372036854775807 / -9223372036854775807 / true; GNU 1152921504606846975 / its negative / true; SWI `bounded` false and no `max_integer`); a flag the oracle lacks is a `domain_error` or a failure exactly as that oracle gives it (measure, then write the row). Integer ARITHMETIC stays SCRIP's bignums in every dialect: a program whose answer depends on XSB's 64-bit wraparound is `SCRIP_EXCEEDS_ORACLE` (CEO-1710), never emulated.
5. **THE CONFLICTING BUILTINS live in `xsb_builtins.pl`** (the prelude library that exists, 336a29fcd's `compiler_options/1` is there), reached as XSB reaches them: `:- import functor/4 from standard.` resolves `standard` to `xsb_builtins` through the dialect's MODULE ALIAS TABLE (ARCH-PROLOG-DATABASE.md § 2's rule of CTO-372: `basics` = lists, `usermod` = user, now `standard` = xsb_builtins), and XSB's `functor(Term, Module, Name, Arity)` answers `usermod` for an unqualified term and `M` for `M:T`; `compile/1` checks the file exists and LOADS NOTHING (consult, ensure_loaded and `[F]` load it once); a name both `swi_builtins` and `xsb_builtins` define is picked by the import's module or, for a bare call, by the run-time `'$dialect'` guard the prelude already uses (`listing/1`, `consult/1`, `load/1` are the shape). `print/1` has no XSB arm: a program the oracle refuses on it is `NO_ORACLE_ANSWER` (CEO-1696).

**BUILDER AND ORDER:** hq_icon, inside the XsbTests row, one program at a time (CEO-1926), the Prolog smoke before each push (CEO-1928), in this order: (1) the record's third value, the markers and the package contract (witness: a markerless XsbTests program through the new prelude, its `double_quotes` codes); (2) the float writer column (float_tests_roots, roots_int_comp, n2c); (3) integer division (arith_op's roots); (4) the flag table (arith_op evl3); (5) `functor/4` and `compile/1` in `xsb_builtins.pl` (functor4_tests, test_ascii_*). The GNU values of columns 2-4 land with the columns and the GNU rows are the coo's to re-grade; a GNU witness cut from gplc for each column is the proof that the column's GNU value is gprolog's. No new global: the record's field exists, the tables are static data.

**§ 6 STEP (1) AS BUILT (hq_icon, SCRIP 8cbf19b8f and 5c435f745, corpus 2bd8e5850, 2026-10-25 00:4x; recorded by the cto 08:4x CDT):** one `pl_dialect` field (ISO/SWI/GNU/XSB) with about sixteen reads, the XSB markers outranking SWI's, `'$dialect'` xsb, `--dialect=xsb`, the package prelude's one marker; a markerless program prints `[97,98]` as XSB does. 5c435f745 withdrew `:- export P.` and `:- index/1` from the marker set because swipl accepts both: the markers are what BOTH other oracles refuse (import-from, compiler_options, hilog, ti), by § 2's measurement; family_prolog.pl's main graph tripling and returning between 01964419b and 5c435f745 in the coo's ZSM census was that flip. ONE CONTRACT FINDING: the vendoring's driver passed `""` where XSB reads codes, so it now passes atoms at its 1,034 sites. TWO SWITCHES RECORDED, SWI's value given to XSB and accepted until a measured difference says otherwise: (a) a program's own definition of a NON-ISO builtin wins (`pl_swi_user_redefines`: table_tests_abol_test defines `print/2`, a name XSB does not have, so no builtin is lost); (b) a program's own definition of a library leaf wins. Every other SWI-keyed switch gives XSB the ISO/GNU arm. Next in the page's order: the float writer.
