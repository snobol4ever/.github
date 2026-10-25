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
`digit//1` inside `dcg/basics`) keep the library's definition, because the reader's renamed helper is a different key -- swipl's split is the same when a
library exports both names and the user redefines one. The compile-time half already behaves (a plain fact overrides the library). Witnesses: issues_test1142
and the minimal program above, both modes, against swipl.

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

## 5. The clause fragment compiles lazily (hq_zetas' measurement on db/test_abolish, 2026-10-24 19:5x; NOT YET A ROW)

Measured by callgrind: every `assert` compiles its clause fragment at assert time (`pl_db_fragment`, 1.9M Ir each, 78 percent of what test_abolish spends after
the absent stub was made once). Design: a fragment is compiled at the clause's FIRST CALL or RETRY, not at assert, so a program that asserts and never calls
pays nothing and one that asserts a thousand facts and calls once compiles once per clause when the call reaches it. The registry's owners (hq_runtime, the
cfo) take this as a row when the ceo mints it; it needs no new state beyond a per-clause "compiled" mark the clause record already has room to carry (the
record is theirs to lay out).

## 6. Measured, waiting for a ruling with their program

- `db/test_module` (hq_zetas, c91370f86: 5 of 7): `Module:clause(H, _, Ref)` comes back module-qualified; a module-scoped `meta_predicate` `:` argument that is a
  cyclic qualifier raises nothing. The module-context section of this page rules on them when the two programs are brought with their swipl answers.
- `ARCH-PROLOG-TABLING-IDG.md` § 6: the transaction's undo log, a spine local of the `transaction/1` activation under one `'$tx_cur'` root (the cfo's placement).

## 7. The dynamic fact table is indexed on its first argument (hq_runtime's row `prolog-dynamic-fact-table-scales-long-primes-1`, steps 2 and 3; ProRosetta long-primes-1, sieve-of-eratosthenes-10 and the dynamic-fact time-outs)

A call to a dynamic predicate with a bound first argument walks every clause today. RULING: the registry's clause list of a dynamic predicate carries a HASH
INDEX on the first argument's atomic key (small integer, atom, functor id; a variable first argument or a clause whose first argument is a variable goes in an
"any" bucket consulted on every call), built lazily at the first call with a bound first argument and maintained by `assert`/`retract` (an `assertz` appends to
its bucket, a `retract` unlinks from it; the logical update view is the clause list's generation stamps as today, the index only narrows which clauses the
walk visits). It is the WAM's first-argument indexing applied to the dynamic database, the static twin of ARCH-PROLOG-BB-REWRITE § 7.2's SWITCH box; the
index lives in the registry record (hq_runtime's and the cfo's layout), a rooted typed vector on the collected heap (CEO-1210: no fixed limit), and § 5's
lazy fragment compile rides with it (a clause the index never selects is never compiled). Witnesses: long-primes-1 and sieve-of-eratosthenes-10 against
swipl in both modes.

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
