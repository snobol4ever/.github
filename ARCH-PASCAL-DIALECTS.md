# ARCH-PASCAL-DIALECTS.md — one Pascal front end, four dialects, one switch

**Minted 2026-10-10 13:4x CDT by the ceo on Lon's word (in-chat to the ceo, verbatim: *"We do want to support the full variations of Pascal dialects, FPC in ISO mode, FPC with objects, and Delphi mode that FPC offers. For the parser_pascal.sc these dialects can be switches via a global variable that is set and tested via \*IDENT(global_switch) in the PATTERN."*; CEO-1614). The sentence is also Lon's GRANT of the one global the Snocone parser needs (RULES.md § FACT RULES: no new global without Lon's in-chat grant that session — this is it, for `parser_pascal.sc`'s dialect switch).**

## 1. The dialects and their oracles

| dialect | `{$mode}` | what it adds over the one before | oracle (ONE ORACLE PER DIALECT, CEO-1588's any-fpc-mode contract) |
|---|---|---|---|
| **ISO 7185** | `iso` (or no directive and no dialect construct) | the base: SCRIP's Pascal today, PAT 427/427, the strictness the PAT rejection tests require (for-variable, goto into an else, complete variant parts) | `fpc -Miso` |
| **FPC** (Turbo-compatible) | `fpc` (fpc's own default when no directive), `tp` | units and `uses`, `{$ifdef}` conditional compilation, `case … else`, short strings with `+`/`s[0]`, `assign`/`paramstr`/`fillchar`/`move`, typed constants, `@`, `inc`/`dec`/`exit`/`break`/`continue`, `shl`/`shr`/`xor`, `Result`, hex and `#n` literals, `+=` | `fpc` (default mode) |
| **ObjFPC** | `objfpc` | classes with inheritance, virtual and abstract methods, constructors and destructors, `self`, properties, `is`/`as`, exceptions (`try`/`except`/`finally`/`raise`), dynamic and open arrays with `SetLength`/`High`/`Low`, overloading, default parameters, `AnsiString`, `for … in` | `fpc -Mobjfpc` |
| **Delphi** | `delphi` | ObjFPC's set under Delphi's rules: `string` is `AnsiString`, `Result`, no `@` needed for procedure variables, `Exit(v)`, class helpers, interfaces, generics and anonymous methods as fpc's Delphi mode accepts them | `fpc -Mdelphi` |

A program's dialect DECIDES ITS ORACLE, never the reverse: PasRosetta already cut 203 refs under `iso`, 92 under `fpc`, 23 under `objfpc`, 1 under `delphi` (`ALL.dialect`), and a program compiles under no mode stays debt.

## 2. The switch — one per program, set early, tested everywhere

**What decides the dialect:** (1) a `{$mode X}` directive, read by the LEXER as fpc reads it (directives are not ignored any more: `{$mode}`, `{$ifdef}`/`{$ifndef}`/`{$else}`/`{$endif}`/`{$define}`, `{$I-}`/`{$I+}`, `{$H+}`; the rest stay ignored as fpc ignores unknown ones) — it comes first in the file and sets the switch before the parse; (2) absent a directive, ISO, until the FIRST DIALECT CONSTRUCT appears (`uses`, `unit`, `{$ifdef}`, `case … else`, a `string[n]`, `assign(`, `class`, `object`, `try`), which flips the switch to the smallest dialect that owns the construct — hq_pascal's contextual-keyword grammar for units is the first instance (`uses`, `unit`, `interface` stay identifiers in ISO's `pat0001`); the harness's dialect contract records the same decision as the mode that cuts the ref. One switch, one decision per program, recorded on the entry's attribute row; NO `--compat` command-line switch (RULES.md ONE ORACLE, ONE FEATURE SET — the program carries its dialect, the user never names it).

**In the C parser (`src/parsers/pascal/`):** the switch is a field of the parser's state struct (Lon's globals rule: one struct per stage, never a bare global), set by the lexer on `{$mode}` and by the parser on the first dialect construct, and tested in the grammar actions and the lexer's keyword table (a Delphi-mode `string` is `AnsiString`; `operator` is a reserved word only in FPC/ObjFPC/Delphi; `otherwise` only in ISO's successor). The tree is the PRUNED PARSE TREE regardless of dialect: a dialect-only construct is one node per rule that fires, and the LOWERER places its semantics (a class is a record plus a method table placed by the lowerer; a dynamic array a heap block with a length; an exception a `bb_catch`-shaped box, the one new box of the Prolog rebuild reused).

**In `bootstrap/parser_pascal.sc` (Lon's design, verbatim above):** the dialect is a GLOBAL VARIABLE of the Snocone parser — `dialect` holding `'iso'`, `'fpc'`, `'objfpc'` or `'delphi'` — SET when the `{$mode}` directive is recognized (or when the first dialect construct fires) and TESTED IN THE PATTERNS through an unevaluated expression: `*IDENT(dialect, 'objfpc')` (and `*DIFFER`) guards the alternative a dialect owns, so one pattern grammar carries all four dialects and the match itself selects the arm at match time. This is the one global Lon grants to `parser_pascal.sc`; the pruned-parse-tree law holds — the guard chooses which rule fires, never the shape the rule builds.

## 3. The order of work

Each dialect is LARGE CHUNKS: the switch and the lexer's directive reading first with the PAT suite as the control arm (ISO must not move); then FPC mode (units CEO-1611; the two CEO-1612 rows; TPLY the demo); then ObjFPC (classes, exceptions, dynamic arrays — Rosetta's 23 objfpc solutions and the FPC test programs that carry `{$mode objfpc}` the smoke); then Delphi (Rosetta's Delphi solutions, the pascal-lisp Scheme demo in its own dialect instead of a port). The Snocone `parser_pascal.sc` follows the C parser dialect by dialect under CEO-1562 order (3), its tree gate `test_gate_snocone_parsers_match_the_c_parsers_tree_for_tree.sh` the closure for each.

## 4. Rows (CEO-1614)

- `pascal-dialects-one-switch-set-by-the-mode-directive-or-the-first-dialect-construct-iso-fpc-objfpc-delphi-each-graded-against-its-fpc-mode-ceo-1614` — hq_pascal, rank 1, the mechanism and the lexer's directives; CEO-1611 (units) and the two CEO-1612 rows are its FPC chunks.
- `pascal-objfpc-and-delphi-classes-exceptions-dynamic-arrays-properties-and-overloading-graded-against-fpc-mobjfpc-and-fpc-mdelphi-ceo-1614` — hq_pascal, rank 2, after FPC mode.
- `snocone-parser-pascal-sc-carries-the-four-dialects-through-one-global-switch-tested-by-ident-in-the-patterns-lons-grant-ceo-1614` — hq_snocone, rank 3 (order (3) of CEO-1562), when hq_snocone is seated.
