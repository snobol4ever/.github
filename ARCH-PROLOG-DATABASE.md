# ARCH-PROLOG-DATABASE — THE CLAUSE DATABASE, THE LINKED LIBRARIES AND THE STREAMS: THE RULINGS OF RECORD (the cto, Fable 5.1, from 2026-10-24 21:4x CDT, CEO-1964)

**Status: the page where a database, library or stream ruling lands so it is not chat alone.** CEO-1964 gives the cto design authority over every Prolog
feature; the builders ask, the answer is written here with its date and the row it serves, and the builder builds one program at a time (CEO-1926), the
Prolog smoke before every push (CEO-1928). The registry (`pl_db_reg_t`, `src/runtime/unification.c`) is hq_runtime's and the cfo's to touch; a ruling here
names what changes, never how many bytes.

## 1. readutil is a base-prelude rule, not C (hq_runtime's question 1, 2026-10-24 21:0x; built 534a3e421)

The vendored `readutil.pl` stays verbatim and its `link_foreign` takes the FOREIGN branch: `use_foreign_library(foreign(readutil))` succeeds quietly and the
base prelude DEFINES the four predicates the foreign library would have supplied -- `read_stream_to_codes/2,3`, `read_line_to_codes/2,3` -- over `get_byte`
when `stream_property(S, type(binary))` holds and over `get_code` otherwise, byte for byte as swipl's C: a line ends at 10; swipl 9.0.4 DROPS the CR of a CR LF
line end in `read_line_to_codes/2` and KEEPS it in `/3` (measured by hq_runtime, which overrides the first draft of this ruling); end of file gives -1 for the
line form. No new C leaf, no new builtin name (CEO-985: logic lives in boxes).

## 2. The prelude is autoload: a user definition wins whenever it arrives (hq_snobol4's question, 2026-10-24 21:4x; TreallaTests issues_test1142)

Measured: `term_expansion(mk, digit(1,a,b)). mk. main :- digit(X,Y,Z), ...` -- the loader asserts the user's `digit/3` at load time (a clause after a
`term_expansion` definition is deferred to `'$load_item'`), but `main` referenced `digit/3` at compile time with no definition, so the prelude linked
`dcg/basics`, whose `digit//1` is registered STATIC, and the assert raises `permission_error(modify, static_procedure, digit/3)` (`pl_db_static_ball`,
`rt_proc_is_registered`). swipl: autoload resolves only an undefined predicate at call time, so the user's definition wins.

THE RULE, in the registry: (1) a predicate linked from the prelude because the program REFERENCED it without defining it is registered with the kind
LIBRARY, never static (a predicate the program defines keeps static: swipl refuses to assert into a static user predicate too); (2) the first load-time clause
for a key of kind LIBRARY DROPS the library definition and defines the predicate as the program's own, dynamic, re-pointing the key as an abolished key is
re-pointed to its stub (`pl_runtime_install_packet_entry`, hq_zetas 3ccfcecdc), so every call site that resolved the key at compile time reaches the user's
clauses; no warning, as swipl prints none when a local definition shadows an autoload; (3) the prelude's own calls to that predicate (`digits//1` calling
`digit//1` inside `dcg/basics`) keep the library's definition. The compile-time half already behaves (a plain fact overrides the library). Witnesses: issues_test1142
and the minimal program above, both modes, against swipl.

**(3) AS FIRST WRITTEN WAS WRONG AND IS RE-CUT (hq_snobol4's measurement, 2026-10-24 22:0x, with (1) and (2) built; the cto's ruling 2026-10-25 00:5x CDT):**
the reader renames nothing; a library's calls to its own exports go through the SAME key, so with (1) and (2) alone the user's `digit//1` (asserted after a
`term_expansion`) is what library `digits//1` calls -- witness lib2.pl: swipl prints `123-` then `120`, the patch printed `-123`, the parent refused the assert.
THE RULING is swipl's module rule, at compile time only: every predicate a spliced library defines is registered under a PRIVATE KEY, its module-qualified name
(`dcg_basics:digit/3`: the library's file stem as swipl names the module), and the exported key `digit/3` is installed as the LIBRARY-kind entry of (1)
sharing that same code. Every call site INSIDE a spliced library's clauses to an export of a spliced library -- its own, or another library's it imports -- is
lowered against the DEFINING library's private key; only user code reaches the exported key; (2)'s re-pointing moves the exported key alone. So the user's
definition is reached by every user call site and by no library call site, as swipl resolves a library body in its own module and the user's definition in
`user`. A library's call to a name it does NOT export -- a hook the user is meant to define (`portray/1`, `message_hook/3`, `term_expansion/2`, any multifile
predicate) -- keeps the shared key. REFUSED, hq_snobol4's (b): re-pointing at assert time registering an alias and re-targeting the library's call sites walks
the registry at run time on every first assert and misses a library spliced after the assert. COST: none at run time; one more registry entry per library
predicate. `clause/2`, `listing/1` and `current_predicate/1` name exported keys and the user's only; the private key is unreachable from source. WITNESSES:
lib2.pl (the own-export arm) first; then a program that redefines a `lists` export (`member/2` or `append/3`) and calls a spliced library predicate whose body
uses it (the cross-library arm); both modes against swipl. BUILDER: hq_snobol4 under CEO-1964, one program at a time (CEO-1926), the Prolog smoke before the push.

**THE SAME RULE COVERS THE BASE PRELUDE AND A MODULE-QUALIFIED LIBRARY CALL (hq_icon's ask, 2026-10-24 21:4x, XsbTests ai_tests cs_o/cs_r/kalah/pg/plan and
call_tests; the cto 2026-10-25 02:1x CDT):** measured, SCRIP's own library code calls `member/2` by name from the base prelude (`memberchk/2`, `environ/2`,
`file_property/2`, the debug topic check, `trie_gen/3`, `subtract/3`, `intersection/3`, `union/3`, `locale_property/2`, the load_files pickers), from
`prelude/tabling.pl` (`tbl_rhas/2`, `incr_guard`), `xsb_tables.pl`, `lists.pl`, `aggregate.pl`, `nb_set.pl`, `rbtrees.pl`, `clpfd.pl`, and a program that defines
its own `member/2` captures every one of them (ai_tests_cs_o misses 18 of 51 answer lines; renaming the program's member/2 alone cures it); a per-site private
helper flips nothing (hq_icon tried five sites) and is REFUSED as the meanwhile: it is whack-a-mole. THE RULE IS ONE MECHANISM: the base prelude is a library
(module `system`) like the vendored ones, so EVERY call site inside library code (base or vendored) to a predicate that LIBRARY CODE defines is lowered against
the defining library's private key, and only the program's own clauses reach the exported key, whether the program defines the name at compile time (today's
`pl_user_file_defines` road, § 3) or asserts it at load time (the LIBRARY-kind re-point above). A module-qualified call `M:G` with M a LIBRARY MODULE resolves to
that library's private key (§ 6 rule 2), and a DIALECT MODULE ALIAS is a static table cut from the oracle, never typed by hand: XSB's `basics` (member/2,
append/3, select/3, ...) is `lists`, `usermod` is `user`, so `call(basics:select, X, L, R)` reaches the library's select/3 while the program's own select/3 stays
in user, as XSB keeps them apart. BUILDERS: hq_snobol4 builds the mechanism (the private keys, the library-internal lowering for the base and the vendored
libraries) under its TreallaTests row; hq_icon brings the alias table and the XSB witnesses (cs_o first) one program at a time, both modes against XSB.

## 3. Redefining a builtin in the SWI dialect (hq_runtime's question 2; ProRosetta associative-array-iteration-1)

swipl's own rule: a user clause for a predicate swipl marks `iso` (`predicate_property(P, iso)`: the ISO core, `length/2` among them) is
`permission_error(modify, static_procedure, PI)` at load, as today; a user clause for any OTHER builtin DEFINES that predicate in user, every call in user code
resolves to the user's definition (the lowerer does this for the library leaves through `pl_user_file_defines`; widen that test to every non-iso builtin name
instead of listing names), and `clause/2` then reads the user's clauses. The iso set is a static table in the lowerer cut once from swipl with
`findall(P, predicate_property(system:P, iso), L)`, never typed by hand.

## 4. listing/1 lists what swipl lists (hq_runtime's question 3; ProRosetta quine-1)

Every user predicate, static or dynamic: the static seeding (`pl_static_seed_pred`) seeds the clauses of every user predicate a `listing/1` or
`portray_clause/1` target can name, single-clause predicates included (the `TT_CHOICE` test is the defect), printed through the portray_clause road the dynamic
ones use, so a quine prints itself as swipl does.

## 4b. portray_clause and listing print swipl's layout in the SWI dialect: library(listing) vendored (hq_runtime's question 4, 2026-10-24 21:5x)

Measured: swipl 9.0.4's `library/listing.pl` is 1,246 lines of plain Prolog with no system-internal call (zero names of the `$` form), no `print_message`,
eleven `setting/2` reads (`listing:line_width`, `tab_distance`, `cut_at`, `comment_ansi_attributes`, ...) over `library(settings)` (752 lines, plain Prolog),
and autoloads of `apply`, `error`, `lists`, `option`, `ansi_term`, `debug`, `prolog_clause` (`clause_info/5`), `prolog_code` (`most_general_goal/2`);
`portray_clause/1,2,3` are its lines 650-658. RULING: vendor `listing.pl` verbatim under CEO-1473 for the SWI dialect, parsed only for a program naming
`listing`, `portray_clause` or their options; its settings answered by vendoring `settings.pl`, or, if that library drags more than the cost gate allows, by a
base-prelude rule answering exactly the listing settings with swipl's defaults cut from swipl; `clause_info/5` and `most_general_goal/2` only when a program
reaches `listing/1`'s source-layout road. The GNU dialect keeps `gnu_builtins.pl`'s `portray_clause` (gprolog's layout, graded by gplc); the dialect picks the
library as it picks the builtins file. Hand-written layout rules are refused: they drift on the next shape the corpus prints. Witnesses: ProRosetta quine-1, then
a clause with an if-then-else and a disjunction body, both modes against swipl.

**4b ADDENDUM (hq_runtime's measurement, 22:3x; my "zero dollar names" reading was wrong and is withdrawn):** vendored verbatim, `listing.pl` meets two
directive kinds the reader lacks (`:- setting/4`, five of them, which become base `setting/2` facts at swipl's measured defaults 4, 0, false, 78, [fg(green)];
`:- thread_local`, whose single-threaded meaning is `dynamic`, a reader rule) and, because an injected library is COMPILED WHOLE, the dead `listing/1` road's
names refuse at compile time (`current_predicate/2`, `use_module/2` as a goal, `'$find_library'/5`, `'$define_predicate'/1`, `@/2`, `clause_property/2`).
RULING: option (a), THE INJECTOR COMPILES THE CLOSURE, NOT THE FILE -- a vendored library's clauses are selected per predicate by reachability from the names
the program references (the body walk the prelude already does across libraries, applied inside one, meta-arguments through the `meta_predicate` specs), so a
predicate no program road reaches is never compiled; this is the general road for every vendored library (clpfd is 7,903 lines compiled whole today) and lands
first, its witness a clpfd program's compile time before and after beside quine-1; then `current_predicate/2` as a base builtin (SWI has it, SCRIP lacks it);
then `listing.pl` under the closure. Option (c), hand-written layout, stays refused.

**4b THE INJECTOR'S ROOTS INCLUDE EVERY PREDICATE THE LOWERER OR A PARSER REWRITE CAN NAME (hq_zetas, 2026-10-25 02:xx: bc63b803b's closure rooted the program's clauses, the base prelude's bodies and the refkeys, so `'$tbl_icall'`, `'$tbl_kcall'`, `'$tbl_mcall'`, `'$tbl_dcall'`, `'$tbl_dchange'` -- named by emitted code and the parser's rewrites, by no clause -- were dropped and every kinded or hooked tabling program died on existence_error; cured 6efe5b2eb by rooting those six keys when their name is referenced):** THE RULE: a predicate introduced by the lowerer, a template, a runtime road or a parser rewrite (the `'$tbl_*'` family, `'$mq_arg'`, `'$clause_unmangle'`, `'$lfx_*'`, every `'$'` name a C or `.cpp` file spells) is a ROOT of the closure whenever its name is in the referenced set, and the rooting list in prolog_parse.c beside the `tbl_call` root is the one place it is declared; a landing that teaches the lowerer a new `'$'` name adds it there in the same landing, or the injector drops it on the next program. A coo reading between bc63b803b and 6efe5b2eb on a tabling program is this, not a regression of the file.

## 4c. predicate_property(H, meta_predicate(Spec)) is ONE record column, read at run time in both dialects (hq_runtime's open item under § 4b, 2026-10-24 22:1x; the cto's ruling 22:2x CDT under CEO-1964/1971)

Measured (SCRIP b962f0c92, mode 3, SWI dialect, against swipl 9.0.4): with the head's functor known at compile time SCRIP answers `findall(?,0,?)` where swipl
answers `findall(?,0,-)`; with the head bound at run time (`G = findall(_,_,_), predicate_property(G, meta_predicate(M))`, which is how `listing.pl`'s
`portray_body` asks for every body goal it lays out) SCRIP answers NOTHING for forall, catch, setof, phrase, maplist, assertz, `\+` and a user
`:- meta_predicate solve(2,-)`, where swipl answers `forall(0,0)`, `catch(0,?,0)`, `setof(?,^,-)`, `phrase(//,?)`, `maplist(2,?,?)`, `assertz(:)`, `\+0`,
`solve(2,-)`. swipl holds 147 `system:` meta predicates; its library ones (maplist, foldl, include, aggregate_all, limit, freeze, ...) come from the libraries'
own `:- meta_predicate` directives. THE CAUSE is three deciders of one fact: the lowerer's hand-typed `pl_meta_template` (29 rows, swipl's vocabulary
misspelled, `?` where swipl says `-`), the runtime's `pl_gnu_meta_spec` string (gprolog's rows, read only under `pl_gnu_dialect()` by `pl_pp_prop` and
`pl_pp_nth`), and the compile-time `g_stage2.pl_decl_meta` vector (the program's own directives, unreachable once the head is a run-time value). RULING, four
rules, one mechanism:

1. THE SPEC IS A COLUMN OF THE PREDICATE'S RECORD. Every predicate's meta spec lives on its registry record (the record `rt_pl_db_key_kind` finds by key), as
   its `dynamic` and `multifile` facts do; `pl_pp_prop`'s `meta_predicate` arm reads that column in BOTH dialects for a head bound at any time, and `pl_pp_nth`
   builds the compound from the column. The GNU-only branch of `pl_pp_prop` goes.
2. TWO SOURCES WRITE THE COLUMN, NEITHER TYPED BY HAND. (a) A `:- meta_predicate` directive -- the program's, or a prelude library's (`apply.pl` line 80
   declares maplist's) -- writes the column at lowering, for the program's and the closure's predicates alike (the closure's declarations ride the injector,
   § 4b). (b) A builtin with no Prolog source (the C and asm builtins and the control constructs: findall/3,4, catch/3, forall/2, setof/3, bagof/3, `\+`/1,
   call/1..8, once/1, ignore/1, not/1, assertz/1, retract/1, the `,` `;` `->` `*->` controls, ...) takes its spec from ONE STATIC TABLE PER DIALECT in the
   runtime's record layout (ARCH-PROLOG-C-OUT-OF-THE-BOX.md § 15's compiled tables), GENERATED into an `.inc` by a harness script that runs the oracle -- swipl
   `findall(P, predicate_property(system:P, meta_predicate(_)), L)` with each spec, 147 rows; gprolog `predicate_property(P, meta_predicate(M))` over its
   builtins -- and gated current the way `box_cell_shapes.inc` is (`test_gate_box_cell_shapes_inc_is_current.sh`'s shape). The dialect picks the table as it
   picks the builtins file. `pl_meta_template`, `pl_gnu_meta_spec` and `pl_gnu_meta_term`'s private vocabulary are DELETED in the landing that lands the table;
   the lowerer's compile-time fold of `predicate_property` for a known head (lower_prolog.c 3253, 3268, 5207) stays only as a reader of the same table, never a
   second list.
3. THE VOCABULARY IS EACH ORACLE'S, VERBATIM. swipl's `0..9 : ^ // ? + - *` and gprolog's `0..9 : ? + -` print as the oracle prints them (`setof(?,^,-)`,
   `phrase(//,?)`, `format(+,:)`); a spec SCRIP cannot answer as its oracle does is a red row against the generated table, never an edited row.
4. LISTING NEEDS ONLY RULE 1. `listing.pl`'s layout asks at run time with a bound functor; the compile-time fold never serves it. The meta-argument
   qualification masks of `'$mq_arg'` (`pl_mq_specs`, lower_prolog.c 4690) keep reading the program's directive tree: compile-time by nature, already one reader.

WITNESSES: the probe above as a corpus program (eleven heads, the user `solve(2,-)` among them, every answer swipl's, both modes), then ProRosetta quine-1 and
a clause whose body carries findall, catch and forall under `listing/1` (§ 4b's witness). Builder: hq_runtime mints and builds it as its own row, as it
proposed, one program at a time (CEO-1926), the Prolog smoke before the push (CEO-1928), the generated table's gate adopted into the wiring floor in the same
landing; no new global (the table is static data, the column a field of a record that exists).

**4c ADDENDUM -- if/3 IS NOT A BUILTIN IN EITHER ORACLE, SO SCRIP STOPS DEFINING IT (hq_runtime's question and hq_packages' measurement, 2026-10-25; ruled by the cto 08:4x CDT):** swipl 9.0.4, swipl 10.1.5 and gprolog answer `if(true,write(a),write(b))` with `existence_error(procedure, if/3)`; SCRIP runs it as a soft-cut (lower_prolog.c: the meta-table row, `pl_lower_softcut` at the goal site, a synthesized clause, added by abd2fb800 for a Logtalk predicate_property case that runs ONLY under `predicate_property(if(_,_,_), built_in)`, which swipl skips). Two graded Trealla entries (sundry_shift_compiled, sundry_cut_after_call) carry the existence_error in their refs and fail on exactly this. RULING: (1) hq_packages deletes the three sites, so a call of if/3 raises the oracles' existence_error, the two Trealla entries its witnesses, one program at a time; (2) `predicate_property` does not report if/3 (hq_runtime's option (a)): the meta-spec tables are cut from the two oracles and from nothing else -- no YAP-cut third source for a construct SCRIP would then be the only engine to ship -- and the Logtalk gate's criterion is re-cut from 29 to 28 with this reason, the case skipped as swipl skips it. SCRIP ships no control construct its dialect's oracle lacks (OUTSIDE THE BASELINE IS ABOUT THE ORACLE, CEO-542).

## 5. The clause fragment compiles lazily (hq_zetas' measurement on db/test_abolish, 2026-10-24 19:5x; NOT YET A ROW)

Measured by callgrind: every `assert` compiles its clause fragment at assert time (`pl_db_fragment`, 1.9M Ir each, 78 percent of what test_abolish spends after
the absent stub was made once). Design: a fragment is compiled at the clause's FIRST CALL or RETRY, not at assert, so a program that asserts and never calls
pays nothing and one that asserts a thousand facts and calls once compiles once per clause when the call reaches it. The registry's owners (hq_runtime, the
cfo) take this as a row when the ceo mints it; it needs no new state beyond a per-clause "compiled" mark the clause record already has room to carry (the
record is theirs to lay out).

## 6. THE MODULE CONTEXT: the surface is swipl's compound, the mangled key is the registry's alone (hq_zetas's witness `mq1-module-context-witness.pl` with swipl 9.0.4's answers, 2026-10-24 23:xx; the cto's ruling 2026-10-25 01:5x CDT under CEO-1964/1971)

Measured: module `mq1`, `solve(Pred, R)` declared `meta_predicate solve(2, -)`, called `solve(t, R)`: swipl `qualified(mq1)`, SCRIP `bare('mq1:t')` (the closure
arrives as the mangled atom); `test_module_2:clause(H, _, Ref)` on a clause asserted as `test_module_2:term`: swipl `term`, SCRIP `test_module_2:term` (db/test_module
clause#2); `clause(H, _, Ref)` from mq1: both `test_module_2:term`; `clause(test_module_2:H, _, Ref)`: both `term`; `meta_predicate mqual(:)` called with `T = a:T`:
swipl `type_error(acyclic_term, _)`, SCRIP no error (mqual#2). SWI tabling/test_monotonic_lazy lazy_15 fails on the first: its `Pred = M:t` never matches, so its
`abolish_table_subgoals` is skipped and the stale plain table disagrees. One representation question, four rules:

1. THE REPRESENTATION. The parser's module flatten mangles a non-user module's predicate NAME into the registry key `'mod:name'`, and that atom is the registry's
   alone. A module-qualified term at the SURFACE (a meta argument the context qualifies, a closure, a goal handed to call/N, a head clause/3 returns, anything a
   program can unify or print) is swipl's compound `':'(Module, Term)`, with Module the CONTEXT MODULE of the call site (the module whose clause holds the call:
   `mq1`, never a fixed `user`, which is what `'$mq_arg'` writes today), and the plain term when the context is `user`.
2. RESOLUTION. call/N, the closure-extending library roads (maplist and its kin) and every database road take `M:G` as DATA (bc63b803b's rule), strip the
   qualifiers to the innermost module M and goal G, and form the registry key at the moment of the call: `'M:name'`/N for a non-user M, `name`/N for `user`; one
   key build per call, nothing stored mangled inside a term.
3. THE CONTEXT OF A MODULE-TRANSPARENT BUILTIN. A module-qualified call `M:clause(...)`, and likewise `M:assert`, `M:retract`, `M:current_predicate`,
   `M:predicate_property`, `M:abolish`, runs with the context module M. clause/2,3 (through `'$clause_unmangle'`, which already has the test) return the head
   BARE when the clause's module is the context module or the argument names the module itself (`clause(M:H, ...)`), and `Mod:Head` otherwise: so
   `test_module_2:clause(H, _, Ref)` answers `term` and the same call from mq1 answers `test_module_2:term`.
4. THE CYCLIC QUALIFIER. Stripping a `:` chain (`strip_module/3` and every meta-argument qualification) walks `M:T` while T is `_:_` under ONE cycle check on
   the qualifier spine (`acyclic_term/1` of the chain, never a depth bound) and raises `type_error(acyclic_term, T)` as swipl does.

Builder: hq_zetas (db/test_module clause#2 and mqual#2, then lazy_15), one program at a time (CEO-1926), the witness file's five swipl answers the test, the Prolog
smoke before the push; no new global. Still open here: `ARCH-PROLOG-TABLING-IDG.md` § 6, the transaction's undo log (the cfo's placement).

## 7. The dynamic fact table is indexed on its first argument (hq_runtime's row `prolog-dynamic-fact-table-scales-long-primes-1`, steps 2 and 3; ProRosetta long-primes-1, sieve-of-eratosthenes-10 and the dynamic-fact time-outs)

A call to a dynamic predicate with a bound first argument walks every clause today. RULING: the registry's clause list of a dynamic predicate carries a HASH
INDEX on the first argument's atomic key (small integer, atom, functor id; a variable first argument or a clause whose first argument is a variable goes in an
"any" bucket consulted on every call), built lazily at the first call with a bound first argument and maintained by `assert`/`retract` (an `assertz` appends to
its bucket, a `retract` unlinks from it; the logical update view is the clause list's generation stamps as today, the index only narrows which clauses the
walk visits). It is the WAM's first-argument indexing applied to the dynamic database, the static twin of ARCH-PROLOG-BB-REWRITE § 7.2's SWITCH box; the
index lives in the registry record (hq_runtime's and the cfo's layout), a rooted typed vector on the collected heap (CEO-1210: no fixed limit), and § 5's
lazy fragment compile rides with it (a clause the index never selects is never compiled). Witnesses: long-primes-1 and sieve-of-eratosthenes-10 against
swipl in both modes.

**§ 7 ANSWERS TO hq_runtime (2026-10-25 08:5x CDT), before its code:** (1) YES to the shape: the TO box gains ONE operand, the target's first argument, and its two steps become leaf calls that RETURN a slot index or -1 (`rt_pl_db_cand_first(store, key)`, `rt_pl_db_cand_next(store, i, key)`; the box does every jump, CEO-1576), the visibility test staying inline and the cursor in the box's existing slot cell; an operand of an existing IR kind IS placed by the planner -- its read distance is a row of `rd[]` like every operand's -- so nothing is placed by hand and no frame cell is declared; the chain-omega's next-visible step calls the same `cand_next` with the activation's first-argument cell. The index (buckets keyed by atom id, small integer or functor id plus the any bucket; raw slot-index vectors on the heap; built at the first keyed walk, appended by assertz, dropped and rebuilt lazily by asserta, compaction and reclaim; an erased slot kept in its bucket for the visibility test) is as this section says. (2) § 7 THEN § 5, AND MEASURE: land the index and the lazy fragment compile, read long-primes-1's instruction count (callgrind, CEO-1912) and the 12,000-fragment enumeration's share of it; the facts-only data path (no fragment while a predicate holds only facts) is its own row AFTER that reading, if the reading says the compile is what is left. One change at a time, each measured.

## 8. call_with_depth_limit/3 (ProRosetta integer-sequence-1)

The depth is the number of predicate activations between the limited goal's entry and the current call. RULING: a program that REFERENCES
`call_with_depth_limit/3` is lowered DEPTH-COUNTED (a graph fact the lowerer sets for every predicate of that program, LANGUAGE IDENTITY STOPS AT LOWER): the
emitted call box increments a depth word in the standing frame at entry and decrements it at the γ/ω landings, two instructions each, and compares it against
a limit word beside it, raising `depth_limit_exceeded` as the result when exceeded; `call_with_depth_limit(G, L, R)` saves and sets the two words around
`call(G)` and reports the maximum reached in `R`, swipl's contract. A program that never names the predicate pays nothing (the fact is unset, the box is
the plain one). The two words are two more cells of the standing frame (a single current-X cell each, CEO-1542), asked of Lon with this page.

## 9. Streams: the column counter is the stream record's (ProRosetta arithmetic-integer-1)

`format/2`'s column stops (`~t~20|`) and `line_position/2` read the stream's column, which swipl keeps per stream and SHARES between `user_input` and
`user_output` when both are the terminal or a pipe pair (`set_stream(S, tty(true))`'s shared position). RULING: every SCRIP stream record carries line and
column counters advanced by every write and read through it (the writer's one road, `core_lib`'s stream layer, a value service), and the three standard
streams share one position record when they are the same device, as swipl measures it; `line_count/2`, `line_position/2`, `character_count/2` and the
column-stop arms of `format/2` read that record. No new state outside the stream record.

## 10. The ProRosetta mechanisms, ordered (hq_runtime's list, 2026-10-24 22:4x)

1. `library(plunit)` inside a user program (catamorphism-6, json-pointer-1, sort-disjoint-sublist-3, test-a-function): the shim `corpus/tests/prolog/plunit.pl`
   the SWI runner already feeds becomes a vendored prelude library `plunit`, selected when a program names `begin_tests/1`, `run_tests/0,1` or `test/1,2`, under
   CEO-1473 (the shim is SCRIP's own text, so "verbatim" is its own copy; swipl's plunit.pl stays the oracle of its output format).
2. `library(ctypes)` (rot-13-1 `is_endfile/1`, count-how-many-vowels `is_alpha/1`): the parked vendored copy lands.
3. `lazy_findall/3` (deceptive-numbers): swipl's `library(lazy_lists)` vendored over `freeze/2` (ARCH-PROLOG-CLPFD § 4's attributed variable), no new mechanism.
4. The fact table index, § 7 (long-primes-1, sieve-of-eratosthenes-10, the time-outs).
5. `call_with_depth_limit/3`, § 8 (integer-sequence-1).
6. The stream column, § 9 (arithmetic-integer-1).
7. The listing layout, § 4b with its addendum (quine-1).
8. `sha_hash/3` (sha-1-1): swipl's `library(sha)` is C; SHA-1 and SHA-256 over a code list are a text VALUE SERVICE in C (ARCH-PROLOG-BB-REWRITE § 2's rule), the
   smallest of the list.
9. Dicts and their functional notation (fractran): a page of their own, not before the above.
OUT OF THIS PAGE: a last call after a cut that does not release its frame (hamming-numbers-1, lunar-arithmetic, reverse-the-order-of-lines overflow at any
`-s`) is the activation's lifetime, the cfo's design authority (CEO-1960), telegrammed to the cfo with the three programs; universal-lambda-machine is a harness
staging red (the coo's); CHR and the CLP family are ARCH-PROLOG-CONSTRAINTS.md.

## 11. read_term/2 `subterm_positions` and `comments` (hq_packages, SWI core/test_read.pl: 19 subterm_positions cases, position#1, pos_block; CEO-1677 road (1))

RULING, the ceo's road made concrete: the byte extent of every term is a FIELD OF EVERY `tree_t` NODE (CEO-1715: a field every node uses is a node field, never
a side table), two 32-bit offsets `start`/`end` in the two padding holes `tree_t` has today (after `t`, after `n`), so `sizeof(tree_t)` does not move; the lexer's
token carries its start and end offsets (`Lexer.pos`), and the reduce that builds a node stamps it from its first token's start and its last child's end
(the `pt_stamp` sites), BUILT ONCE, read by no second pass; `read_term/2` with `subterm_positions(P)` builds the position term by one walk over the tree beside
`pl_tree_cell` (`From-To`, `string_position` for the four `double_quotes` forms, `brace_term_position`, `list_position`, `term_position`; a negative number is one
token), subtracting the 7 bytes of the reader's `'$rd'((...))` wrapper; `comments(C)` collects the lexer's skipped comment tokens with their positions the same
way. The tree-for-tree gate prints no position, so `parser_prolog.sc` stays green and stamps when it replaces the C parser (a declared debt in its row).
`dict_position`, `key_value_position` and `a()` zero-arity compounds are separate rows. `tree_t` is shared by every parser, so the landing owes the eight smokes
and the reachable cores (CEO-1928). hq_packages builds it one case at a time.

## 12. The fresh variables of one body term are created in source order, left to right (hq_runtime's finding from the CLP(Q) landing, 2026-10-25; ruled by the cto 08:5x CDT)

MEASURED (swipl 9.0.4 against SCRIP origin, both modes): `T = (Y = 3*X + 2), compare(O1, X, Y)` -- swipl `o1(>)`, SCRIP `o1(<)`; `U = f(A, g(B, C)), msort([C, B, A], S), S == [A, B, C]` -- swipl yes, SCRIP no. `compare/3` orders unbound variables by cell address (`rt_pl_cell_compare_leaf`, class 0); swipl creates the fresh variables of a body term in source order, SCRIP allocates them inner term first, so `X` inside `3*X` is older than `Y` and `A` is not the oldest of `f(A, g(B, C))`. It matters: library(clpq)'s `dump/3` picks the variable it solves for by that order (`{A = 2*B + 1}, dump([A,B],[a,b],C)` prints `[a=1+2*b]` where swipl prints `[b= -1r2+1r2*a]`), and so does every `msort`, `sort`, `setof` and `@<` over fresh variables. THE RULE: it is the LOWERER's term-construction order, not placement -- the Prolog lowerer emits the cell creations of a body term's first-occurrence variables in SOURCE ORDER (left to right, an outer variable before the variables of the subterms to its right) before the structure nodes that use them, so the address order is swipl's creation order; a head's variables keep their argument order. BUILDER: hq_prolog (the Prolog lowerer's lane), one program at a time, hq_runtime's two-line witness the DONE-WHEN (both lines as swipl, both modes; hq_runtime mints the row with that witness as its gate), the clpq dump line the second witness.

**§ 12 ADDENDUM -- THE STANDARD ORDER OF TWO FRESH VARIABLES ACROSS FRAMES AND THE HEAP (hq_snobol4's TreallaTests issues_old_test0067, 2026-10-25; ruled by the cto 09:3x CDT):** `sort([A,B,B,A], S)` with A and B clause variables gives `[A,B]` in swipl (it orders variables by address and its global stack grows up, so address order IS creation order) and `[B,A]` in SCRIP (`rt_pl_cell_compare_leaf` orders by cell address; a clause's frame cells sit on the downward machine stack and heap variables grow up, so no sign flip gives creation order everywhere). § 12's rule (the fresh variables of one body term created in source order) covers the heap variables one term construction makes and is landed first; it does not reach two frame cells of one clause or a frame cell against a heap cell. RULING: the order among unbound variables stays IMPLEMENTATION-DEFINED (ISO 7.2.1 leaves it so; the oracle's is an accident of its stack direction), SCRIP keeps the address order, and issues_old_test0067 stays DEBT in its denominator (the oracle answers, CEO-1696), not excluded and not cured by a plant. THE DESIGN IF THE DEBT GROWS, recorded so nobody re-derives it: an unbound variable's value word is unused, so a CREATION SERIAL can live there at zero space cost -- written by every road that makes a fresh variable (the lowerer's cell creation, `copy_term`, `read_term`, `findall`'s copies, the unifier's write mode), read by the compare leaf for two unbound cells -- at the cost of one counter increment per creation at every such road and one runtime counter (a `g_runtime` member, Lon's grant); it lands only on a measured population of programs that read the order, never for one test. hq_snobol4 reads 0067's row with this reason.
