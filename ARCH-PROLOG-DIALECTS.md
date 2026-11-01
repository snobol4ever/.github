# ARCH-PROLOG-DIALECTS.md — one Prolog front end, two dialects, one record

**Minted 2026-10-10 by hq_prolog on the cto's ruling CEO-1632** (approving the design asked under row
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
The principle is the cto's (CEO-1632), the same as Pascal's dialect switch (CEO-1624). MEASURED by the cto on gprolog 1.6.0 and
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
   08:3x CDT). MEASURED on swipl 9.0.4 against SCRIP 51d399df7 in the SWI dialect: `functor([a],N,A)` gives `'[|]'/2` (SCRIP `'.'/2`); `[a|b] =.. L`
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

**§ 6 STEP (1) AS BUILT (hq_icon, SCRIP 8cbf19b8f and 5c435f745, corpus 2bd8e5850, 2026-10-25 00:4x; recorded by the cto 08:3x CDT):** one `pl_dialect` field (ISO/SWI/GNU/XSB) with about sixteen reads, the XSB markers outranking SWI's, `'$dialect'` xsb, `--dialect=xsb`, the package prelude's one marker; a markerless program prints `[97,98]` as XSB does. 5c435f745 withdrew `:- export P.` and `:- index/1` from the marker set because swipl accepts both: the markers are what BOTH other oracles refuse (import-from, compiler_options, hilog, ti), by § 2's measurement; family_prolog.pl's main graph tripling and returning between 01964419b and 5c435f745 in the coo's ZSM census was that flip. ONE CONTRACT FINDING: the vendoring's driver passed `""` where XSB reads codes, so it now passes atoms at its 1,034 sites. TWO SWITCHES RECORDED, SWI's value given to XSB and accepted until a measured difference says otherwise: (a) a program's own definition of a NON-ISO builtin wins (`pl_swi_user_redefines`: table_tests_abol_test defines `print/2`, a name XSB does not have, so no builtin is lost); (b) a program's own definition of a library leaf wins. Every other SWI-keyed switch gives XSB the ISO/GNU arm. Next in the page's order: the float writer.

### 6.1 XSB MODULES: a module name is a ground term and a key; the file is a load site, never part of the name; a module-tagged structure symbol is a module-qualified ATOM, not a cell bit and not a side table (the cto, 2026-10-31 09:30 CDT; hq_packages' ask of 2026-10-30 under its XsbTests row, routed by the cto 2026-10-31 09:4x; CEO-1926, CEO-2067)

**THE ORACLE'S DEFINITION (XSB 5.0.0, `docs/userman/module_system.tex`, read whole):** a module name is a GROUND TERM `M(m_1, ..., m_n)`, the main symbol the base module (its file `M.P` by default), the arguments the actual modules that replace the formals of `:- module_parameters(f_1, ..., f_n)`; there is no limit on nesting. `Name>>File` names the file the module's code is loaded from on demand, in an import and in a qualified goal alike (`Mod = moda>>moda_file, Mod:p(X,Y)`), and EVERY reference to such a module must carry the same file. `usermod(File)` and `usermod>>File` are PSEUDO-MODULE references: File is not a module, its predicates load into usermod on the first call of the imported predicate; `usermod(load_dyn(File))` and `usermod(consult:load_dync(File,a))` name the loading predicate. `:- import P/N from Mod as Q/N` renames at the importer. A STRUCTURE SYMBOL is (module, name, arity): every predicate symbol of a module file is in that module, every non-predicate structure is in usermod unless imported or `:- local`; `term_new_mod/3` coerces a term's symbol into any module; `functor(Term, Module, Name, Arity)` reads it, and the parametrised module prints as its ground term (functor4_tests t57: `t57(g(A,B,C),newmod(newmod2,newmod3),g,3)`), while `write` of the term prints the bare name (t36: `g(A,B,C)`); two tagged terms of one module unify (t35, t56).

**THE RULINGS.**

- **R1 THE KEY.** A module's identity is the canonical text of its ground module term with every `>>File` STRIPPED (`parent(mother_us,father)`, `newmod(newmod2,newmod3)`, `usermod`), and a predicate's key is `<module>:<name>/<arity>` exactly as § 20 and ARCH-PROLOG-DATABASE § 2 already key a library's private predicates (`dcg_basics:digit/3`). The file names a LOAD SITE: the loader's module registry maps a module key to its file and its state (unloaded, loading, loaded); stripping loses nothing because XSB requires every reference to carry the same file. `usermod` is `user` through the alias table of § 6 (5). Answer to (b): yes, `Name>>File` in a goal means load File as module Name on first touch, then call the goal there; the parameters of a parametrised module live in the instantiated KEY, never in a tag.
- **R2 THE ONE RESOLVE ROAD.** `Mod:Goal` with Mod bound at RUN time (a variable, a `>>` term, a parametrised term) and `:- import P/N from Mod [as Q/N]` both reach ONE runtime leaf, `'$mod_resolve'(Mod, Name/Arity, Key)`, written in the prelude's Prolog over the registry (no C decides a module): it normalises Mod to its key and records each `>>File` against the module it names (the base module's and every parameter's), LOADS the base module's file on first touch through the consult road of § 20 (the file: the explicit `>>File`, else `<base>.P` then `<base>.pl` on the library and program directories; an absolute path from `expand_filename/2` as is; a relative path against the program's directory), INSTANTIATES a parametrised module ONCE PER DISTINCT ACTUAL TUPLE by loading its file under the instantiated key with each formal of `module_parameters` bound to the actual module term wherever the file's `import ... from <formal>` and `<formal>:G` name it (`parent(mother_us,father)` and `parent(mother_pap,father)` are two loaded modules, as XSB keys them), loads an ACTUAL parameter module on the first call of one of its predicates (XSB's on-demand order), and returns the key the call then goes through. A static `:- import P/N from Mod as Q/N` lowers to a stub under `Q/N` in the importing module whose body is `'$mod_resolve'` then the call; a pseudo-module `usermod(File)` / `usermod>>File` / `usermod(Loader(File, ...))` is the same stub whose load step is the named loader (`consult` by default, `load_dyn`, `consult:load_dync/2`, `proc_files:load_csv/2`) into usermod. The compile-time arm hq_packages landed (a CONSTANT module atom in `M:Goal`, lower_prolog.c's qualified-goal arm) stays as the fast path of the same key. This road is DIALECT-BLIND after lower: SWI's `M:G` with M bound at run time takes it too, which is a shared gain, not an XSB arm.
- **R3 THE TAGGED SYMBOL IS AN ATOM.** Answer to (a): neither a bit in the term cell nor a side table keyed by address. SCRIP's functor is an atom, so the module of a structure symbol is a property of the ATOM ENTRY: the atom table (`src/runtime/rt/prolog_atom.c`) gains one word per entry, the module key (a sentinel for usermod), and is interned on (module, name), so `f` in usermod and `f` in `newmod` are two entries with the same PRINT NAME. `term_new_mod(Mod, T, NT)` interns the symbol of T under Mod's key and builds NT with that functor atom and T's arguments (an atomic T under usermod is returned as is, t39 and t40; under any OTHER module XSB builds a ZERO-ARITY STRUCTURE: `term_new_mod(m1, hello, T)` gives T printing as `hello()` and `functor(T, M, N, A)` answers m1, hello, 0 -- measured by hq_packages 2026-10-31 on XSB 5.0.0, CORRECTING the page; the landing 48b7cb4c3 returns the plain atom there, and table_tests_not_exists_test reaches the case through a qualified `M:Goal` with an atom Goal, so hq_packages cures it when that program measures red for it); `write`, `writeq`, `print`, `numbervars` and `format` print the name and know nothing of the module; unification is functor identity, so two tagged symbols of one module unify and a tagged symbol never unifies with the untagged one, as XSB's symbol table decides it. `functor(Term, Module, Name, Arity)` (`:- import functor/4 from standard`, § 6 (5)'s alias to `xsb_builtins`): a compound answers its functor atom's module as the TERM parsed back from the key text (t57, t58) and Name as the print name; an atomic Term answers usermod and itself (t14 to t34); with Term unbound it builds under the Mod-tagged atom when Mod is bound and under usermod when not (t5, t6, t46 `functor(T,f(a),pp,6)`); its errors and its quiet failures (t41 to t55) are the ref's lines, cut from XSB, and hq_packages measures each against the oracle before writing its arm. COST: one word per atom entry, no new global (the table exists), no new collector visitor (the atom table is a root today), no change to the DESCR.
- **R4 WHERE IT LIVES.** Answer to (c): `>>`, `module_parameters/1`, `import ... as`, the pseudo-modules, `functor/4` and `term_new_mod/3` are XSB's and live in `xsb_builtins.pl` and the XSB arm of the reader (the operators of § 6 (1): `>>` is `yfx 200` as XSB reads it, measured before the landing); the key, the registry and the resolve road are shared machinery.

**BUILDER AND ORDER (hq_packages, one program at a time, CEO-1926; the Prolog smoke before each push, CEO-1928; refs are the package's XSB refs):** (1) functor4_tests (R3 whole: the atom word, `term_new_mod/3`, `functor/4`); (2) mod_file_tests_test_mod_file (R2 with constant `>>` modules: `modp>>modp_file`, an absolute and a relative file, `do_all`); (3) mod_dyn_tests_test_dynmod (a run-time bound Mod under `findall`); (4) parmod_tests_test_parmod (parametrised modules, `import ... as`, the `usermod(...)` pseudo-modules with `pm_subdir` and `load_dyn`, the quoted module names); each `_im` twin after its base; test_modules' isolation half last. What this section forbids: a module identity in the DESCR tag or in a side table; a per-call `strcmp` on a module name (the key is interned once); a C function that loads or resolves a module (the resolve road is prelude Prolog over the consult road); a fourth dialect switch.
