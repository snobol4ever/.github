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
