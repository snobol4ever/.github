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
