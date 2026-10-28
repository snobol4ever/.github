# ARCH-PASCAL-REDESIGN.md — DRAFT (hq_pascal, 2026-10-23; unfinished, pushed at sprint end per CEO-1934)

**Mandate.** Lon, in-chat to hq_pascal, 2026-10-23 about 14:05 CDT, verbatim: *"You, HQ-PASCAL, are promoted to Opus 5.5 xhigh. Go re-design Pascal and get it to 100%."* and *"Tell CEO."* Ruled CEO-1933 (.github cb1e64232): the design of Pascal's own front end (the parser, `src/lower/lower_pascal_tree.c`, `src/lower/lower_pascal.c`, the prelude units, the Pascal runtime arms) is hq_pascal's. The cto reviews only what reaches a shared node (planner, templates, x86_zop, placement); this page goes to the cto for information.

**Status: DRAFT.** Sections 1-3 are measured. Sections 4-6 are the plan, not yet reviewed against the code line by line.

## 1. Where Pascal stands (measured 2026-10-23)

- Pipeline: `src/parsers/pascal/` (bison/flex) builds the pruned parse tree. `lower_pascal_tree.c` (8,185 lines, 845 static functions) elaborates it into a desugared `tree_t` of generic nodes and `__pas_*` builtin calls. `lower_pascal.c` (1,444 lines) builds the IR from that. Language identity stops there.
- Suites: PasM 100%, PAT 398/400, FPC 94/94. PasRosetta went from 174/319 to 195/319 today, in nine landings (SCRIP 4ab6fd7f3, b034ba0b9, fded1a675, ecc90a17b, 60b544f50, 90acad8b5, 62ce0e57a, bbd09778f; corpus 16c21b8f4).
- The ISO 7185 core is solid. The 124 remaining PasRosetta reds are mostly FPC/ObjFPC/Delphi programs.

## 2. The design defect: the elaborator decides types from names, not from a type model

`lower_pascal_tree.c` is the former `pascal.y` semantic actions moved into LOWER: `v[k]` is yacc's `$k` and the `pas_pend_*` fields are yacc-era pending state. Type knowledge lives in about 60 tables inside `g_lower_pas_sem_t` (`lower_pascal_tree.h`), most of them keyed by variable NAME:

- `pas_arrays[256]`, `pas_arrtypes[64]`, `pas_chararrs[256]`, `pas_strarrs[128]`, `pas_charvars[256]`, `pas_boolvars[512]`, `pas_rectypes[512]`, `pas_recvars[512]`, `pas_arrrecs[128]`, `pas_ptrvars[512]`, `pas_rows`, `pas_scalarvartype`, and others.
- Node marks with fixed caps that drop silently when full: `pas_cvfield_marks[2048]`, `pas_cafield_marks[2048]`, `pas_nafield_marks[2048]`.
- 73 `pas_is_*` predicates guess a property such as "is a char", "is a string" or "is dynamic" from the shape of an already-lowered node plus those tables.

Every cure landed today was this defect wearing a different program:

| Symptom (PasRosetta witness) | Root cause in the type layer |
|---|---|
| `write(P[i,j])` printed codes for `array of array of char` and for `array[a..b,c..d] of char` (draw-a-cuboid) | the char flag was not carried through an alias type, and a two-index char array had no char mark at all |
| A parameter `a` shadowing a global `a` read the global's marks (sorting-algorithms-circle-sort) | array entries looked up by name; parameter entries registered before their scope existed, so they took the outer uid |
| `Map[L,1][p]` indexed past the array (soundex) | a flattened element was re-read as a row by the chained-index rule |
| ISO 6.2.1 fired on FPC programs (aks-test-for-primes, horners-rule) | the dialect is decided by lexer events; flips that need name resolution (undeclared `Result`, a function's own name read as a value) had no home |

The tables also break NO FIXED LIMITS (CEO-1933 b).

## 3. Features that are missing, not mis-typed (PasRosetta reds by class, 2026-10-23)

- Parse errors (22): generics (~10, its own row: `pascal-generics-...-ceo-1930`, ranked last), unit-qualified type names (`Types.TIntegerDynArray`), `procedure of object`, `absolute`, `exports`, `string[expr]`, lvalue casts `Pointer(a[i]) := ...`, `exit(value)`.
- Pointers to existing variables (`p := @a[i]`, `p^`, `inc(p)`, `PChar` arithmetic). There are about 12 programs. The pointer model is a heap-cell index (`pas_heap_ref`), so there is no aliasing of a variable or an element.
- 80-bit `Extended`: about 8 programs differ in the last digits. This needs x87 or soft-float support at the emitter, which is a shared node, so it is out of scope until the cto rules.
- Arrays of small ordinals take one DESCR cell per element (8-16 bytes). fpc uses 1-4 bytes. Sieve programs ask 8-20 GB (fusc-sequence, strong-and-weak-primes, unprimeable-numbers-2). Compact typed element storage is a runtime node (shared).
- Missing library and intrinsics: `val` is not a SCRIP intrinsic (it is a by-name call that loses its var params); `StrLen`, `BsrQWord`/`BsrDWord`, `FillDWord`, `PopCnt`, `Swap`, `BinStr`/`HexStr`; the `dos`, `gmp`, `regexpr`, `sha1`, `contnrs`, `unix`, `sockets` and `fphttpclient` units. Each unit counts as debt unless an fpc run shows fpc itself fails it (cfo, CEO-1696).
- `for row in A` over a two-index array (soundex) needs a row copy.
- `stdout`, `stderr`, `ErrOutput` as predeclared text files.

## 4. The target design (plan)

Three passes inside LOWER. Only `tree_t` crosses from the parser, as now. Every table is allocated in `ct_arena`, grows, has no fixed cap, and lives in the lowering stage's own struct, never in a new global.

1. **DECLARE.** Walk the pruned tree once, after `pas_flatten_units`. Build scopes and a symbol table: constants with their values, types, variables, parameters (value, var, const, out, open, default), routines with signatures and overloads, record fields and variant parts, enum constants, labels, and class members. Each declaration gets a uid. Lookup follows the scope chain, never a bare name.
2. **TYPE.** Give every expression node of the pruned tree a `PasType *` and, where it is constant, a value. The type kinds are ordinal subrange, char, boolean, enum, real, string (short n or ansi), array (index types, element type, packed, dynamic depth, open), record, set, pointer, file or text, procedural, and class. This pass resolves identifiers (variable, constant, call, field, enum, the function name as its result variable, `Result`) and `with` scopes, and decides the whole-program dialect, so every flip point that needs a resolved name (undeclared `Result`, the function's own name read as a value) is decided here. ISO semantic refusals move here from `pascal_sem_check`.
3. **ELABORATE.** The existing `E_*` code generation stays: it carries the tested choices of builtins, record layout and set representation. It asks the typer instead of the tables. Lowered nodes map to their source node's type through one arena map that `E_expression` and `E_variable` fill on return.

The value representation does not change: DESCR cells, ARBLK arrays, records as slot arrays, heap-cell pointers until section 3's pointer model lands. Pascal's measured placement stays exactly as Lon praised it: no rbp-based operand, locals carved by their first writer, zero pre-allocations.

## 5. Roll-out (LARGE CHUNKS)

1. Build DECLARE and TYPE whole in a new Pascal-only file. Run it in SHADOW mode: the elaborator asks both the typer and the legacy predicate, and a census lists every disagreement over the 1,993-program population (packages, benchmarks, demos and the master). Each disagreement is a bug on one side, cured or recorded.
2. Small roll-out: switch one predicate family (char and string first, the family behind today's cures). The control arm is the Pascal smoke, the PasM, PAT and FPC tables (no row may drop) and the `--dump-ir` differential (only named programs move).
3. Massive roll-out: every predicate family switches, then the legacy tables and `pas_pend_*` state are deleted in one landing.
4. The missing features of section 3 that are Pascal-only (lvalue casts, `procedure of object`, qualified type names, `val`, the units) land on the new layer, each graded against its PasRosetta witnesses. Generics is last (CEO-1930).

## 6. Open questions for the next sitting

- Where `pascal_sem_check` (the ISO refusals) moves: TYPE, or a fourth pass after it.
- Whether the pointer-to-variable model (section 3) is Pascal-only (a new DESCR kind handled in Pascal builtins) or reaches a shared runtime node. If it reaches a shared node, it is an ASK to the cto.
- The order between the typer roll-out and the PasRosetta parse-error families. The typer comes first wherever a family needs resolved names.

## 7. Status at stand-down (2026-10-23, CEO-1935, MODE SOLO)

- **Chunk 1 is built and pushed to its own branch, not main:** `wip/hq_pascal/pascal-typer-shadow` at SCRIP `bc8a69628`, held for Lon and the ceo to test. It adds the new Pascal-only `src/lower/lower_pascal_types.c/.h`: DECLARE and TYPE over the flattened, prepassed tree, run before `E_program`, with an arena hash map from each source and lowered node to its `pty_t`. The legacy predicates `pas_is_charexpr`, `pas_is_stringexpr`, `pas_is_boolexpr` and `pas_is_setexpr` still decide. `scrip --dump-pas-types` prints each disagreement and a `PTY-STATS` tally.
- **Measured before the push:** `--dump-ir` is identical to the parent on all 1,993 programs; the Pascal smoke is 9/9 in both modes; the fixed-caps census rows are unchanged. The branch touches shared files (the driver flag, an int field in `src/lower/g_lower.h`, the Makefile list), so the other seven smokes and the PasM, PAT and FPC tables are owed before it can reach main.
- **The census (`scrip --dump-pas-types --dump-ir`, whole population):**

| Predicate | Asked | Typer answered | Disagreements |
|---|---|---|---|
| char | 40,188 | 37,217 | 16 |
| string | 32,743 | 32,635 | 8 |
| bool | 10,249 | 10,201 | 3 |
| set | 35,942 | 35,853 | 17 |

  The 44 disagreements I read all show legacy errors: name-keyed set flags leaking across scopes (rosetta `set.pas`), a char subrange (`webtbs_tw3324`), `char(x)` casts (`quine-2`), PChar dereferences (`thue-morse`, `amicable-pairs-2`), `Format` results, and record boolean fields (p5 `pcom`). Two typer gaps were found and closed: `bytebool`/`wordbool`/`longbool` are integers at run time, and a bare function-typed variable is a call (`__pas_pcall`).
- **Next step:** section 5.2, switching the char and string family to the typer's answers (typer first, legacy where the typer is silent), with the IR and output differentials, the smoke, and the PasM, PAT and FPC tables.

## 8. DESIGN-PLAN: pascal-front-end -- the plan the HQ steps through (the cto, Fable 5.1, 2026-10-28 12:1x CDT, CEO-1996/1998; the row `design-pascal-front-end-scoped-symbol-table-ceo-1998`)

DESIGN-PLAN: pascal-front-end

Sections 1-7 above are hq_pascal's draft of 2026-10-23 and stand as the measure and the target; this section rules the design, folds hq_pascal's four questions (ShortString, pointers, Extended, generics) and turns it into ten steps with witnesses. The witnesses are `corpus/tests/pascal/front_end/` (STEPS.tsv, KEEP.md, ten programs with refs cut from fpc 3.2.2), the harness is `harness/scripts/test_design_pascal_front_end_steps.sh` (`--list` runs nothing, `--step N` is red before the step lands and green after, `--cut` re-cuts the refs).

### 8.1 The measure (SCRIP 40d6d5c50, fpc 3.2.2, 2026-10-28 12:1x CDT)

- **PasRosetta reads 205 of 319** (SUITES.tsv at 9934db1be); by results.tsv's latest reading per program 104 FAIL, 4 OOM, 1 HANG, 1 CRASH (hq_pascal hand-cured ten more this sitting, awaiting the coo's re-read). THE 110 REDS BY THEIR FIRST COMPILE-TIME MESSAGE under mode 4: 66 compile and answer wrongly or die at run time (the type-model class, pointers, Extended, missing intrinsics), 22 parse errors (generics 10: `generic`, `specialize`, the dotted unit name `Generics.Collections`; `absolute`; `exports`; `string[2*N]`; `procedure of object`; `cdecl`; `Unit.TType`; `Pointer(a[i]) := ...`; `then exit(False)`; text after the final `end.`), 14 missing units (gmp 4, dos 3, unix, sockets, sha1, regexpr, fphttpclient, contnrs), 7 ISO 6.2.2.1 refusals of a predeclared name (`stdout`, `ioresult`, `faanyfile`, `tstringsplitoptions`, `taleftjustify`, `font8x8` twice) and one 6.6.3.4, and 1 emitter FATAL (permutations-with-some-identical-elements: emit.cpp 1762, a template guard refused -- the cfo's, not this page).
- **The front end:** `pascal.y` 733 and `pascal.l` 508 lines; `lower_pascal_tree.c` 8,261 lines with 42 static `pas_is_*` predicates used at 295 sites; `lower_pascal_tree.h` holds **67 fixed-size name-keyed or node-keyed arrays** in `g_lower_pas_sem_t` (`pas_arrays[256]`, `pas_boolvars[512]`, `pas_recvars[PAS_REC_MAX]`, `pas_cvfield_marks[2048]`, the `pas_pend_*` yacc-era state); `lower_pascal.c` 1,537; `lower_pascal_class.c` 1,023. hq_pascal's chunk 1 of section 7 is on `origin/wip/hq_pascal/pascal-typer-shadow` (bc8a69628: `lower_pascal_types.c/.h`, 693 lines, DECLARE and TYPE before `E_program` in SHADOW mode, `--dump-pas-types` printing `PTY <pred> legacy= typer=` disagreements and `PTY-STATS <family> asked= answered= agreed=`), based on bbd09778f of 10-23 and now seven Pascal landings behind main (647ab4b95 .. 3d31456b5); main answers `--dump-pas-types` with "cannot open".
- **The four questions, measured against fpc:** (1) SHORTSTRING: `var s: string[5]; s := 'abcdefgh'` prints `abcde 5` (fpc), SCRIP `abcdefgh 8`; `sizeof(string[5])` 6, `sizeof(array[1..3] of string[2])` 9, `s[0]` the length byte; SCRIP has no `sizeof` and drops the bound (`pas_shortstrings`, lower_pascal_tree.c 7949). (2) POINTERS: `p := @a[2]; inc(p); p^ := 77` writes `a[3]` in fpc; SCRIP dies "ISO 6.5.4 the pointer-variable denotes no variable" because a pointer is a heap-cell index (`pas_heap_ref`) that only `new` creates; `PChar(s)`, `p[1]`, `(p + 4)^` are parse errors. (3) EXTENDED: fpc prints `writeln(1/3)` as ` 3.33333333333333333342E-0001` for extended (20 digits, a four-digit exponent), ` 3.3333333333333331E-001` for double, ` 3.333333433E-01` for single; SCRIP prints the double form for all three. (4) GENERICS: the eleven programs use `specialize` (6), `generic` (2), `TList<T>` (2), `TDictionary<K,V>` (1), `TQueue<T>` (1), `THashSet<T>` (3), `TPair<K,V>` (2), `TFPGList` (1), `TComparer<T>` with Generics.Defaults (1), `TArray<T>` (2); SCRIP's parse error is the dotted unit name on the `uses` line for five of them.
- **A witness RED today for the type-model class** (pf02_scopes): a global `ok: boolean` and a procedure-local `ok: string` of the same name -- the legacy string mark leaks out of the procedure and `if ok then` dies "error 102 numeric expected, offending value str"; a 600-variable program (pf03_caps) dies "6.5.3.2 index value" because the 257th array's marks were dropped by a full table: NO FIXED LIMITS (CEO-1210) is violated today.
- **Out of this plan, named:** the four OOM sieves (fusc-sequence, stern-brocot-sequence, strong-and-weak-primes, unprimeable-numbers-2: one DESCR cell per small ordinal where fpc uses 1-4 bytes -- compact typed element storage is a runtime design of its own, written so that a pointer's INDEX stays an element index); the two timeouts (evolutionary-algorithm, hamming-numbers-1); the five environment programs (hostname, sockets-1, http-1, unix-ls, walk-a-directory-non-recursively: NEEDS_NETWORK or the file system, EXCLUDED as the Prolog package names its kind); the five random-or-time programs (loops-nested, magic-squares-of-odd-order-2, monty-hall-problem, one-of-n-lines-in-a-file-1, pick-random-element: NONDETERMINISTIC); the four gmp programs (a `gmp` prelude unit over SCRIP's bignums: its own row); sha1 and regexpr (pure-Pascal fpc package units, vendored after the finish); the emitter FATAL (the cfo). Lon's cloud session rewrites Pascal for speed (CEO-1993): every landing of this plan rebases over it and re-proves; the plan changes no placement (section 4's last paragraph stands: no rbp operand, locals carved by their first writer, zero pre-allocations).

### 8.2 The law

1. **ONE TYPE MODEL, BUILT BY LOWER, KEYED BY SYMBOL, NEVER BY NAME.** DECLARE builds scopes and symbols with uids, TYPE gives every expression a type descriptor, ELABORATE asks the typer; a name is resolved through the scope chain once, in TYPE. No table of the front end is keyed by a bare name or capped at a constant (CEO-1210); every table lives in the lowering stage's own struct in `ct_arena` and grows (no new global: the stage struct is the grant).
2. **THE VALUE REPRESENTATION STAYS; THE PLACEMENT STAYS.** DESCR cells, ARBLK arrays, records as slot arrays; Pascal's spine placement as Lon praised it. What this page adds to the runtime is two DESCR kinds (a pointer with an index, a boxed extended) and the builtins that read them; each is a typed heap visitor the cfo reviews (THE COLLECTOR GUESSES NOTHING).
3. **THE ORACLE IS fpc 3.2.2 IN THE PROGRAM'S OWN MODE**, and a form fpc accepts is debt until a ref proves otherwise (CEO-1696); what fpc prints -- the truncated string, the 20-digit extended, the store order -- is what SCRIP prints.

### 8.3 The rulings

- **R1 THE TYPER LANDS FIRST, IN SHADOW.** hq_pascal's chunk 1 (bc8a69628) rebases onto main and lands as is: no behaviour change, proven as hq_pascal proves a Pascal-only landing (its own `--dump-ir` A/B over the 1,993-program population, then the Pascal smoke; the coo's identity proof is for emitter moves). `--dump-pas-types` is the shadow census; the plan's probe is `PTY-STATS` with answered = agreed on the witnesses, and each of the 44 disagreements it listed (section 7) is cured in step 2 as the typer takes its family.
- **R2 THE TYPER DECIDES.** `pas_is_charexpr`, `pas_is_stringexpr`, `pas_is_boolexpr`, `pas_is_setexpr` read the typer first and the legacy table only where the typer is silent, for one landing; the ISO refusals of `pascal_sem_check` move into TYPE (section 6's first question: TYPE, not a fourth pass), where the name is resolved. A name mark cannot leak across scopes because a symbol is a uid.
- **R3 THE TABLES GO.** Every `pas_is_*` predicate reads the typer or is deleted; the 67 arrays of `g_lower_pas_sem_t` and the `pas_pend_*` state are deleted in ONE landing (LARGE CHUNKS); `grep -o 'pas_[a-z_]*\[[0-9A-Z_]*\]' lower_pascal_tree.h | sort -u | wc -l` reads 0 and the fixed-caps census loses its lower_pascal rows; the 600-variable witness runs.
- **R4 SHORTSTRING.** The string KIND is part of the type: `ShortString(N)` with N at most 255 (`string` is `ShortString(255)` in the fpc, tp and objfpc modes without `{$H+}`; `AnsiString` under `{$H+}` and in delphi mode; a `string[N]` type is `ShortString(N)`); a STORE into a `ShortString(N)` location -- an assignment, a var-parameter write-back, a read, a field or element store -- truncates the value to N (`__pas_sstr_fit(v, N)`, emitted by ELABORATE wherever the typer cannot prove the source within N); `sizeof` is N+1 (and `sizeof` of every type is the typer's size: ordinals by their fpc widths, records by their fields, arrays by element count times element size); `s[0]` reads and writes the length byte; a concatenation is a value of at most 255 characters when its target is a ShortString. The representation stays `DT_S`.
- **R5 POINTERS: A POINTER VALUE IS (BASE CELL, ELEMENT INDEX).** One DESCR kind: the value word holds the address of the BASE CELL (a heap block's element 0, a record's slot 0, or a variable's own cell on the spine or the standing frame) and the length field holds the ELEMENT INDEX. `@a[i]` is (block(a), i); `@a` is (block(a), 0); `@r.f` is (block(r), the field's slot); `@x` of a scalar is (cell(x), 0); `p^` is the cell at base + 16 * index; `inc(p, k)` and `p[i]` move the INDEX (typed by the typer: the pointee's element count, never a byte offset, so compact element storage later changes nothing here); `p = q` compares both words; `nil` is (0, 0); `new` and `dispose` keep the heap-cell road as (cell, 0). `PChar` over a char array is the same shape; `PChar(s)` over a STRING VALUE is (the cell holding the string, the byte index) and its deref reads byte[index] because the typer marks the pointee as char-of-string. THE COLLECTOR sees a base-cell pointer only: the kind's typed visitor follows the value word when it lies in the arena and ignores it otherwise; relocation rewrites the base, the index is untouched; an INTERIOR POINTER never exists. A pointer to a spine or frame cell is valid while its construct lives (Pascal's own rule, as fpc). The readers are `__pas_deref`, `__pas_deref_set`, `__pas_addr`, `__pas_ptr_inc` and the PChar arms, no other. The cfo reviews the kind and its visitor.
- **R6 EXTENDED IS 80 BITS.** `extended` is its own real kind: a boxed `long double` in a 16-byte LEAF heap block (one DESCR kind whose value word points at it; the visitor is a leaf), arithmetic in the runtime's `long double` (`__pas_xr_add` and its family, called when the typer says extended), conversions to and from double at assignment by the typer's kinds, printing in fpc's extended format (`writeln(e)`: 20 significant digits and a four-digit exponent `E-0001`; double keeps 16 and `E-001`; single 9 and `E-01`; `e:0:18` fixed as fpc). One allocation per operation is accepted (eight programs); a register-resident form is a speed row after CEO-1914. x87 in the emitter is refused (a shared node for eight programs). The cfo reviews the leaf kind.
- **R7 PREDECLARED NAMES AND UNITS.** `stdout`, `stderr`, `ErrOutput` (and `Input`, `Output`) are predeclared text files of the System scope; `IOResult` reads and clears the last I/O error under `{$I-}`; `low`, `high`, `length` of a string constant (fpc: low 0, high len-1, [0] the length byte) and of an open array; array bounds that are constant EXPRESSIONS are folded by DECLARE; `val` becomes an intrinsic with var parameters; SysUtils grows `TStringSplitOptions`, `faAnyFile`, `FindFirst`/`FindNext`/`FindClose` and `TSearchRec`; Classes grows `TAlignment`; the `dos` and `contnrs` units are vendored as prelude units written in Pascal covering what the programs use, each routine checked against fpc. A unit that needs the network or the file system of the box stays an EXCLUDED environment class.
- **R8 SYNTAX FAMILIES.** `absolute` (the symbol is an alias of the other variable's cell: no copy); `exports` (ignored in a program); `string[expr]` (DECLARE's constant folding); `procedure of object` (a method pointer value: the object and the method, called through it); `cdecl` and the calling modifiers (accepted, ignored); a unit-qualified type name (DECLARE resolves it through the unit's scope); an lvalue cast `Pointer(a[i]) := v` (the cast names the same cell; the store is the cell's); `exit(value)` after `then`; text after the program's final `end.` is ignored as fpc ignores it. Each is a grammar production plus a DECLARE or TYPE rule; none adds a table.
- **R9 GENERICS.** A generic declaration (`generic T<P1..Pn> = <type>`, `generic procedure|function F<P>(...)`, delphi's `T<P> = ...`) is a TEMPLATE TREE DECLARE keeps un-elaborated with its parameter names; `specialize T<Args>` (objfpc) and `T<Args>` (delphi) INSTANTIATE by copying the template with the parameters bound to the argument types, ONCE per distinct argument tuple, as an ordinary declaration named by the tuple, which then goes through DECLARE, TYPE and ELABORATE like any declaration (a method of a generic class is instantiated with its class); `Generics.Collections` (`TList<T>`, `TDictionary<K,V>`, `TQueue<T>`, `THashSet<T>`, `TPair<K,V>`, their `Add`, `Remove`, `Sort` with a comparer, `Keys`/`Values`, the `for in` enumerator), `Generics.Defaults` (`TComparer<T>`) and `fgl` (`TFPGList<T>`) are PRELUDE UNITS written in generic FPC Pascal by hq_pascal covering what the eleven programs use, each method checked against fpc; SysUtils's `TArray<T>` is `array of T`; the lexer and grammar accept `generic`, `specialize`, the angle-bracket argument lists where a type is expected, and a DOTTED UNIT NAME in `uses` (the parse error of five programs). Classes and `for in` are hq_pascal's existing ObjFPC road.
- **R10 THE FINISH.** The tables read 0; every entry the steps name PASS in both modes by the latest readings; PasRosetta at or above 290 of 319 (the 20 programs of 8.1's out-of-plan list are the gap to 319 and are named rows or exclusions, never silent).

### 8.4 The steps (STEPS.tsv; today every step RED on SCRIP 40d6d5c50)

| step | slug | executor | depends | witness | probe | today |
|---|---|---|---|---|---|---|
| 1 | typer-lands-in-shadow | hq_pascal | - | pf01_typer pf02_scopes | shadow=0 | RED: pf02 dies (102 numeric expected); the census flag is unknown to main |
| 2 | typer-decides-char-string-bool-set | hq_pascal | 1 | pf02_scopes | - | RED 0/1 |
| 3 | every-predicate-asks-the-typer-and-the-tables-go | hq_pascal | 2 | pf03_caps | tables=0 | RED: 6.5.3.2 index; tables 67 |
| 4 | shortstring-capacity | hq_pascal | 2 | pf04_shortstring | entries 100-doors-2 | RED 0/1 |
| 5 | pointers-to-variables-and-elements | hq_pascal, the cfo reviews the kind | 2 | pf05_pointers pf05_pchar | entries abelian-sandpile-model, amicable-pairs-2, one-dimensional-cellular-automata, thue-morse | RED 0/4 |
| 6 | extended-80-bit | hq_pascal, the cfo reviews the kind | 2 | pf06_extended | entries the eight extended programs | RED 0/8 |
| 7 | predeclared-names-and-units | hq_pascal | 1 | pf07_names | entries execute-brain-, maximum-triangle-path-sum, align-columns, sort-using-a-custom-comparator, sedols, knuth-shuffle, hash-from-two-arrays, date-format | RED 0/8 |
| 8 | syntax-families | hq_pascal | 1 | pf08_syntax | entries arena-storage-pool-2, create-an-object-at-a-given-address, executable-library-1, factorial-3, fibonacci-word, legendre-prime-counting-function, machine-code, nonoblock | RED 0/8 |
| 9 | generics | hq_pascal | 3, 8 | pf09_generics | entries the eight generic programs | RED 0/8 |
| 10 | the-finish | hq_pascal | 3-9 | - | tables=0, row 290, latest (40 entries) | RED: tables 67, row 205, latest_not_pass 80 |

The smoke probe runs the named rosetta-pascal entries under the feature `writeln`, which every one of them carries, at most eight per step (CEO-1677).

### 8.5 What this page forbids

A name-keyed or capped table anywhere in the front end after step 3; a new global (the stage struct is the grant); a second type model beside the typer (an `pas_is_*` that guesses from a lowered node's shape); an interior pointer in a DESCR; x87 in the emitter; a change to Pascal's placement (rbp operands, pre-allocations); a `--compat` switch; a program excluded for a feature fpc has (debt, CEO-1696, unless the box's environment is the reason).

### 8.6 Order and seating

1 -> 2 -> 3, then 4, 5, 6 (each on the typer), 7 and 8 (on DECLARE), 9 last (on 3 and 8), 10 read by the coo; hq_pascal executes every step (its mandate, CEO-1933) one landing per step with the Pascal smoke before the push and its 1,993-program `--dump-ir` A/B where a step claims no behaviour change; the cfo reviews the two runtime kinds (R5, R6) and takes a step hq_pascal cannot (CEO-1996); the cto reviews each landing by telegram and answers a design question in this section. Generics after the typer: a specialisation needs resolved names (section 6's third question, answered: the typer first).
