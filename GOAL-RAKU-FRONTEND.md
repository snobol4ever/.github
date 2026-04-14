# GOAL-RAKU-FRONTEND.md — Tiny Raku Frontend for SCRIP

**Repo:** one4all
**Done when:** A `.raku` fenced block in a `.scrip` file compiles to IR and
runs under `--ir-run`. `gather`/`take` maps to BB_PUMP. A smoke test passes.

---

## Motivation

Raku (Perl 6) has two goal-directed constructs that map directly onto the
unified broker:

| Raku construct | Broker mode | SCRIP analogue |
|---------------|-------------|----------------|
| `gather { take $_ for @list }` | BB_PUMP | Icon `every` generator |
| `grammar` / `rule` | BB_ONCE + OR-retry | Prolog clause search |

Adding Raku completes the picture: every major GDE paradigm is represented.
SCRIP already covers SNOBOL4 (BB_SCAN), Icon (BB_PUMP), Prolog (BB_ONCE).
Raku adds a modern language that users actually know.

The acronym situation: SCRIP = SNOBOL4, Snocone, Rebus, Icon, Prolog.
Adding Raku makes it SCRIPR. Or we call it SCRIP and note Raku fits because
it independently discovered the same three broker modes.

---

## Scope — "Tiny Raku"

Not a full Raku implementation. A minimal subset sufficient to demonstrate
`gather`/`take` as BB_PUMP and basic scalar expressions. Grammar rules are
future work (post this goal).

Supported subset (Phase 1):
- Integer and string literals
- Variables (`$x`, `@arr`)
- `gather { ... }` / `take expr`
- `for @list -> $x { ... }`  (basic iteration)
- `say expr` / `print expr`
- Arithmetic: `+ - * /`
- String concatenation: `~`
- `my $x = expr`

Not in scope for Phase 1: grammar/rule, junctions, hyper-operators, OO,
regexes, type system, `use` module imports.

---

## Steps

### Phase 1 — Lexer and parser

- [x] **RK-1** — `src/frontend/raku/raku_lex.c` + `raku_lex.h`.
  Tokens: integer/string literals, `$`-sigil vars, `@`-sigil arrays,
  keywords (`gather`, `take`, `for`, `my`, `say`, `print`, `if`, `while`),
  operators (`+ - * / ~ = := ==`), punctuation `{ } ( ) ; ,`.
  Gate: tokeniser round-trips test snippets correctly.

- [x] **RK-2** — `src/frontend/raku/raku_parse.c` + `raku_parse.h`.
  Recursive descent. Produces a `RakuNode*` AST (same pattern as Icon's
  `IcnNode*`). Parses the supported subset from RK-1.
  Gate: parses `gather { take $_ for 1..5 }` without error.

### Phase 2 — Lowering to IR

- [x] **RK-3** — `src/frontend/raku/raku_lower.c` + `raku_lower.h`.
  `raku_lower_file(RakuNode**, int, int*) → EXPR_t**`.
  Key mappings:
  - `gather { ... }` → `E_ITERATE` wrapping body (mirrors Icon `every`)
  - `take expr`      → `E_SUSPEND` (yield one value, same as Icon suspend)
  - `for @arr -> $x` → `E_TO` / `E_ITERATE` over array elements
  - `say expr`       → `E_FNC("write", [expr])`  (reuse Icon write builtin)
  - `my $x = expr`   → `E_VAR` assignment
  Gate: lowers `gather { take $_ for 1..3 }` to IR that `icn_eval_gen`
  can drive via BB_PUMP.

- [x] **RK-4** — `src/frontend/raku/raku_driver.c` + `raku_driver.h`.
  `raku_compile(src, filename) → Program*`.
  Sets `st->lang = LANG_RAKU` on each STMT_t.
  Gate: `scrip --ir-run file.raku` runs a hello-world snippet.

### Phase 3 — Integration

- [ ] **RK-5** — Add `LANG_RAKU = 3` to `scrip_cc.h`.
  Add `.raku` extension detection in `scrip.c` main.
  Add ` ```Raku ` fence tag to `parse_scrip_polyglot`.
  Add `LANG_RAKU` dispatch in `execute_program` (same as LANG_ICN path —
  `gather` blocks register as generators, `main` called post-loop).
  Gate: `make scrip` clean; smoke PASS non-regressing.

- [ ] **RK-6** — `polyglot_init` support for LANG_RAKU.
  Collect Raku procedure definitions into `icn_proc_table` (reuse Icon's
  table — Raku procs lower to the same E_FNC shape).
  Gate: Raku proc callable from SNOBOL4 via U-22 cross-call hook.

- [ ] **RK-7** — Smoke test: `test/raku_gather.scrip`.
  Raku section: `gather { take $_ for 1..5 }` driven by BB_PUMP.
  SNOBOL4 section: receives each value, prints `RAKU: n`.
  Expected output: `RAKU: 1` through `RAKU: 5`.
  `.ref` generated. Gate: `test_smoke_unified_broker.sh` extended, PASS++.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/raku/raku_lex.c/h` | Lexer |
| `src/frontend/raku/raku_parse.c/h` | Parser → RakuNode* AST |
| `src/frontend/raku/raku_lower.c/h` | Lowering → EXPR_t** IR |
| `src/frontend/raku/raku_driver.c/h` | `raku_compile()` entry point |
| `test/raku_gather.scrip` | Smoke test |
| `test/raku_gather.ref` | Expected output |

---

## Naming

The binary stays `scrip`. The language tag in fenced blocks is ` ```Raku `.
The file extension is `.raku`. LANG_RAKU = 3 in scrip_cc.h.
The acronym question (SCRIPR?) is Lon's call.

---

## Tiny-Raku Agreed Subset

Decided 2026-04-14. Flex + Bison for lexer/parser (raku.l, raku.y).

**In scope — Phase 1:**
- Literals: integer, float, single- and double-quoted strings (flat, no interpolation)
- Variables: `$scalar`, `@array`
- Keywords: `my say print if else while for sub gather take return`
- Arithmetic: `+ - * / %`
- String concat: `~`
- Numeric compare: `== != < > <= >=`
- String compare: `eq ne`
- Assignment: `=`
- Range: `..` (inclusive only)
- Logic: `&&` `||` `!`
- Pointy block: `->`
- Comments: `#` to end of line
- Semicolons required everywhere

**In scope — Phase 2 (after Phase 1 green):**
- `gather { ... }` / `take expr` → BB_PUMP
- `for RANGE -> $var { ... }` / `for @arr -> $var { ... }`
- `$_` implicit topic variable

**Deliberately out of scope (Tiny-Raku forever):**
- String interpolation inside `"..."` (treated as flat literal)
- Raku `grammar`/`rule`/`token` keywords
- Junctions, hyper-operators, OO, types, `use` imports
- `given`/`when`, smart match `~~`
- LTM `|` alternation (only `||` ordered-choice in combinator demo)

**Combinator parser demo (do last):**
A Tiny-Raku program using `gather`/`take` to implement an ordered-choice
PEG combinator parser — demonstrating BB_PUMP is powerful enough to
express a grammar engine without any new syntax.

**Grammar note:**
Raku's `|` in grammars is NOT PEG — it uses Longest Token Matching (LTM),
a non-deterministic NFA over declarative prefixes. `||` is ordered-choice
(PEG-style). This distinction is irrelevant to our frontend (Flex/Bison
handles Raku source) and to our combinator demo (which uses `||` semantics
via sequential `gather` tries).

## Incremental TDD Rungs

- Rung 0: Skeleton — stub driver, `say "hello world"` prints. Build green.
- Rung 1: Flex lexer (raku.l) — all Phase 1 tokens, lex test passes.
- Rung 2: Bison parser (raku.y) — parses `say "hello"`, direct eval.
- Rung 3: Arithmetic + `my $x = expr; say $x;`
- Rung 4: String concat `~`, single-quoted strings.
- Rung 5: Range `..` + `for` loop, direct eval.
- Rung 6: Lower to IR (raku_lower.c) — hello world via --ir-run.
- Rung 7: `gather`/`take` → BB_PUMP, `for 1..5` via generator.
- Rung 8: Full driver, `.raku` extension, LANG_RAKU=3, smoke test.
- Rung 9: Combinator parser demo (do last).

## Current state

## Current state

Session 2026-04-14: RK-1 and RK-2 DONE (Rung 0-5 green, 17/17 PASS).
Flex/Bison frontend complete: raku.l (prefix=raku_yy), raku.y
(api.prefix=raku_yy), raku_ast.h/c, raku_driver.h/c.
Supports: say/print, my $x=expr, arithmetic, string concat ~,
for RANGE->$var {}, if/else, while loop.
Fixed pre-existing U-22 bug: DESCR_t.type -> .v in scrip.c.
HEAD: ecc21def (one4all)
Next: RK-3 (IR lowering — raku_lower.c), then RK-7 (gather/take BB_PUMP).

Session 2026-04-14 (continued): RK-3 and RK-4 DONE.

RK-3 (raku_lower.c): 28/28 PASS. HEAD 77ef905d
  - raku_lower.h / raku_lower.c: full AST→IR lowering pass
  - All key mappings: literals, vars, arithmetic, strcat, comparisons,
    logic, assignment, say→E_FNC("write"), take→E_SUSPEND,
    gather→E_ITERATE, for RANGE→E_SEQ_EXPR(init,E_WHILE) [explicit loop],
    if/while/block/sub/call lowered correctly
  - E_FNC call layout: children[0]=E_VAR(name), children[1..]=args
    (matches icn_interp_eval expectation)
  - raku_lower_file: subs first, top-level stmts in synthetic "main" E_FNC
    with icon_lower layout (ival=nparams=0, children[0]=name-node)

RK-4 (raku_compile, --ir-run): DONE. HEAD e43b8dcc
  - raku_compile(src,filename)→Program* added to raku_driver.c/h
  - scrip.c: .raku files now use raku_compile() → full --ir-run path
  - LANG_RAKU shares icn_proc_table with LANG_ICN (same E_FNC shape)
  - polyglot_init, execute loop, post-loop dispatch all handle LANG_RAKU
  - Gates: hello world, arithmetic, concat, for 1..5 -> $i, if, while
  - Smoke: PASS=2 FAIL=0; lower gate: 28/28 PASS

Next: RK-5 (LANG_RAKU in scrip_cc.h confirmed=3, .raku extension confirmed,
      add ```Raku fence tag to parse_scrip_polyglot, LANG_RAKU dispatch
      in execute_program; smoke non-regressing)
