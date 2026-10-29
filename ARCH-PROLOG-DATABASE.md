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

**4c ADDENDUM -- if/3 IS NOT A BUILTIN IN EITHER ORACLE, SO SCRIP STOPS DEFINING IT (hq_runtime's question and hq_packages' measurement, 2026-10-25; ruled by the cto 08:3x CDT):** swipl 9.0.4, swipl 10.1.5 and gprolog answer `if(true,write(a),write(b))` with `existence_error(procedure, if/3)`; SCRIP runs it as a soft-cut (lower_prolog.c: the meta-table row, `pl_lower_softcut` at the goal site, a synthesized clause, added by abd2fb800 for a Logtalk predicate_property case that runs ONLY under `predicate_property(if(_,_,_), built_in)`, which swipl skips). Two graded Trealla entries (sundry_shift_compiled, sundry_cut_after_call) carry the existence_error in their refs and fail on exactly this. RULING: (1) hq_packages deletes the three sites, so a call of if/3 raises the oracles' existence_error, the two Trealla entries its witnesses, one program at a time; (2) `predicate_property` does not report if/3 (hq_runtime's option (a)): the meta-spec tables are cut from the two oracles and from nothing else -- no YAP-cut third source for a construct SCRIP would then be the only engine to ship -- and the Logtalk gate's criterion is re-cut from 29 to 28 with this reason, the case skipped as swipl skips it. SCRIP ships no control construct its dialect's oracle lacks (OUTSIDE THE BASELINE IS ABOUT THE ORACLE, CEO-542).

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

**§ 7 ANSWERS TO hq_runtime (2026-10-25 08:3x CDT), before its code:** (1) YES to the shape: the TO box gains ONE operand, the target's first argument, and its two steps become leaf calls that RETURN a slot index or -1 (`rt_pl_db_cand_first(store, key)`, `rt_pl_db_cand_next(store, i, key)`; the box does every jump, CEO-1576), the visibility test staying inline and the cursor in the box's existing slot cell; an operand of an existing IR kind IS placed by the planner -- its read distance is a row of `rd[]` like every operand's -- so nothing is placed by hand and no frame cell is declared; the chain-omega's next-visible step calls the same `cand_next` with the activation's first-argument cell. The index (buckets keyed by atom id, small integer or functor id plus the any bucket; raw slot-index vectors on the heap; built at the first keyed walk, appended by assertz, dropped and rebuilt lazily by asserta, compaction and reclaim; an erased slot kept in its bucket for the visibility test) is as this section says. (2) § 7 THEN § 5, AND MEASURE: land the index and the lazy fragment compile, read long-primes-1's instruction count (callgrind, CEO-1912) and the 12,000-fragment enumeration's share of it; the facts-only data path (no fragment while a predicate holds only facts) is its own row AFTER that reading, if the reading says the compile is what is left. One change at a time, each measured.

## 8. call_with_depth_limit/3 (ProRosetta integer-sequence-1) -- THE GRANT (CEO-2010) AND THE LOWERING FROM THE FRAMES, WHICH NEEDS NO STANDING CELL (the cto, 2026-10-29 16:1x CDT; Lon to the ceo, verbatim: *"Tell CTO to have those two cells in the standing frame."*; the ceo's witness at SCRIP 5bb8ad5ab)

**THE CONTRACT (swipl 9.0.4, the oracle).** The depth of a call is its FRAME's level, one more than its caller's frame, a tail call counting as a frame: `forall(call_with_depth_limit(member(X, [a, b, c]), 10, R), (write(X-R), nl))` prints a-2 b-3 c-4 (the goal's frame under the limiter's catch frame is 2, each recursion of member one more). R is the deepest level reached in the proof so far, relative to the limiter, re-reported on every answer; a call whose level exceeds the limit FAILS (no error), and when the goal is exhausted the limiter succeeds once with `R = depth_limit_exceeded` iff the maximum reached exceeded the limit, else fails; a foreign predicate has no frame and counts nothing. SCRIP under the interim prints a-1 b-1 c-1 (§ 13 (4)'s tolerated class).

**THE GRANT, AND WHY THE LOWERING USES NO STANDING CELL.** Lon granted two standing-frame cells (RULES.md receipt beside CEO-2008's, CEO-2010). Writing the landing's shape showed they would put a LEAF CALL on every call: a Prolog root cell is reached only through a leaf that carries the root's address (`pl_db_leaf1`, `rt_pl_db_cell_for`), because no register names the root (CEO-1908) and no constant rsp distance reaches it from a predicate's frame. The depth limit's state is a construct's -- the limited proof's -- and the LIFETIME RULE puts it in that construct's frame. RULED: the lowering below creates NO standing cell; the two granted cells are RELEASED unused, and the ceo tells Lon so (a grant returned, not spent).

**THE DESIGN.**
- **(1) THE FACT.** A program whose source names `call_with_depth_limit/3` (a clause body, a literal `call/N` target, the prelude's own uses) gets the graph fact `depth_counted` set by the lowerer on EVERY graph of the program -- the prelude's and the run-time compile's included (`g_stage2` carries it into `planner_rt_plan`). A program that never names it has no word and no instruction below.
- **(2) TWO FRAME WORDS.** Under the fact every activation frame of the program carries two header words beside the record's link words (the γ wire, the ω wire and the caller's rbp at `kt-24`, `kt-16`, `kt-8`): LEVEL, an integer, this activation's depth; and LIMITER, an integer-typed word holding the ADDRESS of the active limiter's PAIR (0 when no limiter is active). Both are described in the frame map as integers (never followed, never relocated: a frame does not move), both sit at one constant offset in every frame, the main's included (LEVEL 0, LIMITER 0). The planner's frame layout grants them from the fact (the ζ-ACT tier of ARCH-THREE-ZETAS-EMISSION § 3); the zframe prologue stores them.
- **(3) THE CALL'S ARITHMETIC, AT α ONLY.** When the callee's frame is established, before its first goal: `lvl := [caller.LEVEL] + 1` (the caller's frame through the caller-rbp word); `[LEVEL] := lvl`; `p := [caller.LIMITER]`; `[LIMITER] := p`; if `p != 0`: if `lvl > [p + REACHED]` then `[p + REACHED] := lvl`; if `lvl > [p + LIMIT]` then take the clause's ω (the predicate fails; no ball). A TAIL HOP that reuses the frame does `[LEVEL] += 1` and the same two tests. β, γ and ω do NOTHING: the level is the frame's, as swipl's levelFrame. Cost per call under the fact: three loads, two stores, two compares, two conditional branches; the store through p only at a new maximum.
- **(4) THE LIMITER.** `call_with_depth_limit/3` is a PRELUDE predicate the lowerer knows by name, with two address-escaping integer locals LIMIT and REACHED (its PAIR, frame-homed because their address escapes, as IR_TABLE_HDR is declared) and three intrinsics lowered inline: `'$dl_push'(L)`: `[LIMIT] := [LEVEL] + L`, `[REACHED] := [LEVEL]`, `[LIMITER] := the pair's address` (the frame word copied from the caller at α is overwritten for this frame alone; its callees copy the new value); `'$dl_true'(R)`: `R := [REACHED] - [LEVEL]`, and when the caller's LIMITER word `q` is non-zero, `[q + REACHED] := max([q + REACHED], [REACHED])` (the nested case -- MEASURED against swipl with a nested probe before its ref is cut; if swipl restores the outer maximum instead, the fold goes); `'$dl_false'(R)`: `R = depth_limit_exceeded` iff `[REACHED] > [LIMIT]`, else fail. The clause: `call_with_depth_limit(G, L, R) :- '$dl_check'(L), '$dl_push'(L), ( '$dl_call'(G), '$dl_true'(R) ; '$dl_false'(R) ).` where `'$dl_check'` raises swipl's instantiation and type errors and `'$dl_call'(G) :- call(G).` is a predicate frame standing for swipl's catch frame, so the goal's level is the limiter's plus two as the witness counts. No catch and no save/restore: a ball crossing the limiter restores nothing because nothing global was set; backtracking into the goal finds its frames' words in place; the continuation's frames copy the limiter's CALLER's word, so the limit ends where the construct ends.
- **(5) THE WITNESSES**, refs cut from swipl 9.0.4, entered in ProRungs as ladder entries: the ceo's probe (a-2 b-3 c-4); `call_with_depth_limit(true, 10, R)` (R = 1); a non-tail and a tail recursion to depth 5 under limit 10 (R = 6, counting the call frame) and under limit 3 (`depth_limit_exceeded`); a nested limiter (the fold of (4)); `call_with_depth_limit(fail, 10, R)` fails; integer-sequence-1 stays green (hq_runtime's row).
- **(6) THE DELETION.** hq_runtime's interim (swi_builtins.pl: `call_with_depth_limit/3` and the `'$swb_dl_*'` family with its two nb variables `$swb_dl_max` and `$swb_dl_over`, SCRIP 7b94a7efd) goes in the SAME landing; § 13 (4)'s tolerated class closes with it.
- **(7) SEATING.** The design is this section's. The landing is a BUILD -- a planner frame-layout grant, the zframe prologue, the call α and the tail hop in the templates, the lowerer's fact and intrinsics, the prelude clause, the corpus entries -- and goes to the builder the ceo seats, hq_prolog (its planner and template road of LIFO step 2) or hq_runtime (the interim's author), under Lon's 2026-10-28 words: the cto lands nothing. The row's DONE-WHEN is `util_results_entry_green.sh prolog-rungs <entry> <red-tree>` on the ceo's probe, as CEO-2010 cut it; it does not wait on hq_runtime's index work (different files; the second lander rebases).

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

## 12. The fresh variables of one body term are created in source order, left to right (hq_runtime's finding from the CLP(Q) landing, 2026-10-25; ruled by the cto 08:3x CDT)

MEASURED (swipl 9.0.4 against SCRIP origin, both modes): `T = (Y = 3*X + 2), compare(O1, X, Y)` -- swipl `o1(>)`, SCRIP `o1(<)`; `U = f(A, g(B, C)), msort([C, B, A], S), S == [A, B, C]` -- swipl yes, SCRIP no. `compare/3` orders unbound variables by cell address (`rt_pl_cell_compare_leaf`, class 0); swipl creates the fresh variables of a body term in source order, SCRIP allocates them inner term first, so `X` inside `3*X` is older than `Y` and `A` is not the oldest of `f(A, g(B, C))`. It matters: library(clpq)'s `dump/3` picks the variable it solves for by that order (`{A = 2*B + 1}, dump([A,B],[a,b],C)` prints `[a=1+2*b]` where swipl prints `[b= -1r2+1r2*a]`), and so does every `msort`, `sort`, `setof` and `@<` over fresh variables. THE RULE: it is the LOWERER's term-construction order, not placement -- the Prolog lowerer emits the cell creations of a body term's first-occurrence variables in SOURCE ORDER (left to right, an outer variable before the variables of the subterms to its right) before the structure nodes that use them, so the address order is swipl's creation order; a head's variables keep their argument order. BUILDER: hq_prolog (the Prolog lowerer's lane), one program at a time, hq_runtime's two-line witness the DONE-WHEN (both lines as swipl, both modes; hq_runtime mints the row with that witness as its gate), the clpq dump line the second witness.

**§ 12 ADDENDUM -- THE STANDARD ORDER OF TWO FRESH VARIABLES ACROSS FRAMES AND THE HEAP (hq_snobol4's TreallaTests issues_old_test0067, 2026-10-25; ruled by the cto 08:4x CDT):** `sort([A,B,B,A], S)` with A and B clause variables gives `[A,B]` in swipl (it orders variables by address and its global stack grows up, so address order IS creation order) and `[B,A]` in SCRIP (`rt_pl_cell_compare_leaf` orders by cell address; a clause's frame cells sit on the downward machine stack and heap variables grow up, so no sign flip gives creation order everywhere). § 12's rule (the fresh variables of one body term created in source order) covers the heap variables one term construction makes and is landed first; it does not reach two frame cells of one clause or a frame cell against a heap cell. RULING: the order among unbound variables stays IMPLEMENTATION-DEFINED (ISO 7.2.1 leaves it so; the oracle's is an accident of its stack direction), SCRIP keeps the address order, and issues_old_test0067 stays DEBT in its denominator (the oracle answers, CEO-1696), not excluded and not cured by a plant. THE DESIGN IF THE DEBT GROWS, recorded so nobody re-derives it: an unbound variable's value word is unused, so a CREATION SERIAL can live there at zero space cost -- written by every road that makes a fresh variable (the lowerer's cell creation, `copy_term`, `read_term`, `findall`'s copies, the unifier's write mode), read by the compare leaf for two unbound cells -- at the cost of one counter increment per creation at every such road and one runtime counter (a `g_runtime` member, Lon's grant); it lands only on a measured population of programs that read the order, never for one test. hq_snobol4 reads 0067's row with this reason.

## 13. The facts-only data path goes AHEAD of § 5's lazy compile; the key operand needs no planner code; § 8's lowering waits for Lon's grant and the meta-interpreter is the interim (the cto, 2026-10-29 14:2x CDT; hq_runtime's three telegrams of 14:0x-14:5x; the ceo's routing ask; SCRIP HEAD 7b94a7efd)

**MEASURED (hq_runtime, callgrind at 7b94a7efd, a dynamic `is_prime/1`):** an `assertz` costs 2.60 M instructions per fact (7.597 G at 2,000 facts less 4.993 G at 1,000, over 1,000), so long-primes-1's 128,000 facts cost about 333 G before the first lookup; a call with a bound first argument costs 167 K per lookup over 2,000 facts, 167 per clause visited, about 1.4 T for the sieve's lookups at the real size; a retract by first argument 190 K. The sieve calls every one of its facts at least once, so § 5's lazy compile removes NOTHING from long-primes-1 (every fragment compiles anyway); § 7's index removes the 1.4 T walk and not the 333 G compile; only the facts-only data path -- no fragment for a fact -- removes both.

- **(1) THE ORDER, re-cut from § 7's answer (2):** § 7's index first (the `cand_first`/`cand_next` leaves, the index as `HB_PVEC` cells tagged `DT_I`, no new heap kind, `rtx_gc.s` untouched), then STRAIGHT TO THE FACTS-ONLY DATA PATH, and § 5's lazy compile afterwards, NARROWED to rule clauses and to the facts of a predicate that gains a rule (the one case where a facts-only predicate must compile its slots, which lazy compile spreads over the calls instead of charging at the assert). Each landing reads long-primes-1's instruction count (CEO-1912) before and after.
- **(2) THE KEY OPERAND NEEDS NO PLANNER CODE.** `zeta_plan.cpp` line 180 already lists `IR_TO` among the ops whose operands are read, so the lowerer's `ir_operand_push` of the first argument onto the TO db node gives it an `rd[]` row like every operand's -- § 7's answer (1) of 10-25 said so and the tree agrees. hq_runtime lands all three sides itself: the push in `lower_prolog.c` (`pl_db_enum`, ~1998), the read in `bb_to_db` through the record's row, and the chain-omega's key read in `xa_flat.cpp` (~813). hq_prolog's LIFO step 3 edits the GATE pass of `zeta_plan.cpp` (ARCH-PROLOG-ACTIVATION-LIFETIME § 9.11, ~1500-1600) and none of those three files; if one line of the operand list at 180 is needed, whoever lands second rebases, which is the ordinary road, not a handover. Nobody waits.
- **(3) THE DATA PATH's SHAPE, pinned from the baton's design (2)-(5):** the road is chosen AT RUN TIME by an if-type gate (CEO-694) on the registry record's `facts_only` state -- a rule count `assert`/`retract` maintain, zero meaning facts only -- never by a C function that jumps (CEO-1576: the leaf returns the slot index, the box jumps); a predicate that gains its first rule leaves the data path FOR GOOD and its existing slots compile under § 5's rule as they are called. The walk is the TO db box over the index's candidates with the logical update view as born/died generation stamps on the slots and the call's generation in the box's own carve (the iteration state lives in the call's spine cells, § 8 of the activation-lifetime page). THE UNIFICATION is against the STORED cells in place, with COPY-ON-BIND: a call cell that is an unbound variable binds to a fresh copy of a compound stored term, never to the slot's own cells, because `setarg/3` through such a binding would mutate the database (swipl retrieves a fresh term; the clause/2 road's `pl_db_slot_copy` copies whole); an atomic stored cell (long-primes-1's integers) binds with no copy and a bound call cell compares with no copy at all, which is the whole saving. WITNESSES: long-primes-1 and sieve-of-eratosthenes-10 against swipl in both modes with their instruction counts; the db gates (clause/2, retract/1, retractall, abolish, erase/1 with refs, the `HB_PLDBS` walk) both modes; and one program that asserts a rule into a facts-only predicate DURING an iteration over it, so the road switch and the update view are seen together.
- **(4) § 8 AS LANDED (7b94a7efd): THE META-INTERPRETER IS THE INTERIM.** hq_runtime landed `call_with_depth_limit/3` as a prelude meta-interpreter (solve over clause/2, a frame charged per user or builtin call, swipl 9.0.4's counting measured on 8 probes, state in two nb variables) without having been pointed at § 8, and disclosed it. It stands AS THE INTERIM: § 8's depth-counted lowering needs two standing-frame cells asked of Lon with this page and NOT YET GRANTED, so it could not have landed; the interim equals swipl on the 8 probes and takes integer-sequence-1 green, and its divergence is NAMED as a tolerated class in the row's receipts: a limit reached inside a library predicate's recursion (member/2 reads 1 where swipl reads 2, 3, 4) and the interpretive speed. The lowering is minted as its own row after the index work, gated on the grant; hq_runtime was right not to touch the standing frame without it. GRANTED at CEO-2010 (2026-10-29 15:4x) and superseded by § 8 as rewritten the same hour: the lowering needs no standing cell, the two granted cells are released, and the interim goes in the lowering's landing.
- **(5) THE NUL-DEPENDENT READ RATCHET (hq_runtime's landing of CTO-397's ask, 500 sites in 35 files):** split into TWO columns, both ratcheted -- TRUNCATING reads (`strlen`, `strdup`, `ct_strdup`, `strcpy`, the `atoi`/`strto` family, `puts`/`fputs`/`%s`: 30 `strlen` and the dup sites today) and EQUALITY reads (`strcmp` 411, `strncmp` 12, `strchr`, `strstr`) -- so the truncating column is what the Pascal NUL row (CEO-2008, hq_pascal) lowers first, and a keyword compare of an atom holding a NUL stays counted in its own column.

**§ 13 ITEM 3 AS BUILT, ACCEPTED (the cto, 2026-10-29 18:1x CDT; hq_runtime's landing SCRIP f03f48c89, harness a1eafb9: 300 ground facts read 11 M instructions over none, 780 M before; the four ProRosetta programs equal swipl in both modes).** The three choices stand: (1) the road chosen by ENTRY (the first ground fact installs `key@data` as the predicate's entry, the first rule or non-ground fact flips `data_off` for good and installs the first live fragment) is the same mechanism assert already uses to re-point a redefinable entry, so it is not a run-time continuation select and CEO-694 is not touched; it is named here as the one departure from § 13's wording and is the ruling now. (2) The determinism pop before the unify leaf (`rt_pl_db_cand_last` at the box's G, the last candidate's failing unify falling to beta with nothing left) is sound and is the shape § 5's lazy road keeps. (3) The ground check at assert (arity one or more, body exactly `true`) is the right boundary. THE LIMITS, routed: the slots of retracted facts are never compacted, which is the run-time code pool that never retreats (ARCH-GC-COMPILE-TIME-FRAME-MAPS § 17's ranked list: 4,096 bytes per assertz with live=0, death at about 523,800 asserts) and is cured there, not here; the leave that compiles every live slot at the flip (a 100,000-fact table gaining a rule pays 100,000 compiles) is § 5 NARROWED to the flip and is the next fact-table row, which the ceo mints on this ruling with the compile count at the flip as its DONE-WHEN; the call-road index waits on its measured cost as ruled. hq_runtime's next row is § 8's depth-counted lowering, per the ceo's order.
