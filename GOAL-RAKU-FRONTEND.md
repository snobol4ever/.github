# GOAL-RAKU-FRONTEND.md — Tiny Raku Frontend for SCRIP

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** A `.raku` fenced block in a `.scrip` file compiles to IR and
runs under `--run`. `gather`/`take` maps to BB_PUMP. A smoke test passes.

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
  `raku_compile(src, filename) → CODE_t*`.
  Sets `st->lang = LANG_RAKU` on each STMT_t.
  Gate: `scrip --run file.raku` runs a hello-world snippet.

### Phase 3 — Integration

- [x] **RK-5** — Add `LANG_RAKU = 3` to `scrip_cc.h`.
  Add `.raku` extension detection in `scrip.c` main.
  Add ` ```Raku ` fence tag to `parse_scrip_polyglot`.
  Add `LANG_RAKU` dispatch in `execute_program` (same as LANG_ICN path —
  `gather` blocks register as generators, `main` called post-loop).
  Gate: `make scrip` clean; smoke PASS non-regressing.

- [x] **RK-6** — `polyglot_init` support for LANG_RAKU.
  Collect Raku procedure definitions into `icn_proc_table` (reuse Icon's
  table — Raku procs lower to the same E_FNC shape).
  Gate: Raku proc callable from SNOBOL4 via U-22 cross-call hook.

- [x] **RK-7** — Smoke test: `test/raku_gather.scrip`.
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
- Rung 6: Lower to IR (raku_lower.c) — hello world via --run.
- Rung 7: `gather`/`take` → BB_PUMP, `for 1..5` via generator.
- Rung 8: Full driver, `.raku` extension, LANG_RAKU=3, smoke test.
- Rung 9: Combinator parser demo (do last).

## Steps — Phase 4: Test Harness (added 2026-04-14)

roast reference: https://github.com/Raku/roast — official Raku test suite,
organized into S02-literals, S03-operators, S04-statements, S06-parameters, etc.
Our hand-written corpus covers the Tiny-Raku subset only.

- [x] **RK-8** — Fix three bugs in scrip.c / raku_lower.c:
  1. `E_MOD` missing from `icn_interp_eval` arithmetic switch → added `case E_MOD: ri?INTVAL(li%ri):FAILDESCR`
  2. `E_LEQ`/`E_CAT` double-`VARVAL_fn` static-buffer aliasing → use `.s` directly for `DT_S`
  3. `RK_SUBDEF` param wiring — `e->ival` was hardcoded 0, params never loaded into frame;
     fixed to set `e->ival=np` and emit sigil-stripped E_VAR param children matching icon_lower layout.
  Gate: `check('hello','world')` prints `diff`; `10 % 3` prints `1`; 24/24 smoke PASS.

- [x] **RK-9** — Hand-written Raku test corpus in `test/raku/`:
  `rk_arith.raku`, `rk_strings.raku`, `rk_vars.raku`, `rk_control.raku`,
  `rk_subs.raku`, `rk_forloop.raku`, `rk_gather.raku`. Each with `.expected`.
  roast-inspired coverage of Tiny-Raku subset (literals, arithmetic, string eq/concat,
  variables, if/else, while, sub params, return values).
  Gate: all 7 files produce correct output.

- [x] **RK-10** — `scripts/test_raku_ir_rungs.sh` — self-contained harness
  mirroring `test_icon_all_rungs.sh`. Runs all `test/raku/*.raku` against
  `scrip --run`, compares to `.expected`. SKIP-safe if binary/dir missing.
  Integrated into `test_smoke_unified_broker.sh`.
  Gate: PASS=7 FAIL=0; smoke total PASS=24 FAIL=0.

- [x] **RK-11** — Combinator parser demo: `test/raku/rk_combinator.raku`.
  PEG ordered-choice parser using `gather`/`take`. Parses simple expressions.
  Demonstrates BB_PUMP as a grammar engine with no new syntax.
  Gate: correct parse output; added to harness (PASS=8).

---

## Phase 5 — Full Raku Implementation (incremental sprints, easy → hard)

Each sprint adds one language feature. Gate: existing PASS count + new tests green.
All new corpus files go in `test/raku/`. All new harness entries in `test_raku_ir_rungs.sh`.

### Sprint 1 — String interpolation

- [ ] **RK-12** — String interpolation inside `"..."`: `$var` and `@arr[$i]`.
  Lexer: detect `"` strings with `$`-sigils inside; emit RK_INTERP_STR node.
  Lower: RK_INTERP_STR → E_CAT chain (split literal segments + E_VAR lookups).
  Test: `rk_interp.raku` — `my $name = 'world'; say("hello $name");` → `hello world`.
  Gate: PASS=9.

### Sprint 2 — `given`/`when`

- [ ] **RK-13** — `given $x { when val { ... } default { ... } }`.
  Scalar smart-match only (no type dispatch yet). Lower to if/elsif/else chain.
  Test: `rk_given.raku` — classify integer via given/when.
  Gate: PASS=10.

### Sprint 3 — Arrays

- [ ] **RK-14** — Array operations: `push`/`pop`/`shift`/`unshift`, `elems`, `@arr[$i]`.
  Runtime: dynamic array backing in icn_interp_eval. New E_ARR_GET / E_ARR_SET nodes
  or reuse E_FNC("push"/"pop"/"elems") builtins.
  Test: `rk_arrays.raku` — push/pop/index round-trip.
  Gate: PASS=11.

### Sprint 4 — Hashes

- [x] **RK-15** — Hash operations: `%h<key>`, `%h{$k}`, `keys`, `values`, `exists`.
  Runtime: hash table in interpreter. New E_HASH_GET / E_HASH_SET or builtins.
  Test: `rk_hashes.raku` — set/get/keys/exists.
  Gate: PASS=12.

### Sprint 5 — `for` over arrays

- [ ] **RK-16** — `for @arr -> $x { ... }` with real array variable (not just range).
  Requires RK-14. Wire E_EVERY(E_ITERATE(@arr)) to iterate array elements.
  Test: `rk_for_array.raku` — iterate pushed array, print each element.
  Gate: PASS=13.

### Sprint 6 — Multiple dispatch (arity)

- [ ] **RK-17** — `multi sub f($a) { }` / `multi sub f($a, $b) { }`.
  Arity-only dispatch — no type constraints yet. Lexer: `multi` keyword.
  Lower: emit separate icn_proc_table entries keyed by name+arity; dispatch
  selects by nargs at call site.
  Test: `rk_multi.raku` — `multi sub greet($n)` / `multi sub greet($n,$title)`.
  Gate: PASS=14.

### Sprint 7 — Named/default parameters

- [ ] **RK-18** — Named params `:$opt = default` in sub signatures.
  Lexer/parser: `:` prefix on param, `=` default expr.
  Lower: emit default-init E_ASSIGN at sub entry if arg absent.
  Test: `rk_named_params.raku` — `sub greet($name, :$title = 'Mr')`.
  Gate: PASS=15.

### Sprint 8 — Type constraints (compile-time)

- [ ] **RK-19** — Type annotations on params: `Int`, `Str`, `Num`.
  Parser: parse `Int $x` / `Str $s` param syntax. Lower: emit E_TYPE_CHECK
  node at sub entry (or inline guard) — fail with message if type mismatch.
  Test: `rk_types.raku` — type-checked sub, correct call passes, wrong type caught.
  Gate: PASS=16.

### Sprint 9 — Junctions

- [ ] **RK-20** — `any($a,$b,$c)`, `all($a,$b,$c)`, `one($a,$b,$c)`.
  Lower: `any(...)` → E_OR chain; `all(...)` → E_AND chain; `one(...)` → XOR chain.
  Test: `rk_junctions.raku` — `if any(1,2,3) == 2 { say('yes') }`.
  Gate: PASS=17.

### Sprint 10 — Hyper-operators

- [ ] **RK-21** — `@a >>+<< @b` (element-wise), `@a >>.method` (method map).
  Requires RK-14. Lower: emit E_EVERY loop over zip of two arrays, apply op.
  Test: `rk_hyper.raku` — `my @r = (1,2,3) >>*<< (4,5,6); say(@r[0]);` → `4`.
  Gate: PASS=18.

### Sprint 11 — `for`-over-gather (standalone BB_PUMP)

- [ ] **RK-22** — Wire `for GATHER -> $v { }` in standalone `--run`.
  Currently E_EVERY over E_ITERATE(gather-body) is not driven in standalone mode.
  Fix: in `icn_interp_eval` E_EVERY handler, detect E_ITERATE child whose body
  contains E_SUSPEND nodes; drive via setjmp/longjmp coroutine or collect-then-iterate.
  Test: `rk_for_gather.raku` — `for gather { take 1; take 2; take 3; } -> $v { say($v); }`.
  Gate: PASS=19. This unlocks true BB_PUMP in pure Raku context.

### Sprint 12 — Basic OO

- [ ] **RK-23** — `class Foo { has $!attr; method bar() { } }`, `Foo.new(attr => val)`.
  Lexer: `class`, `has`, `method`, `!`-twigil. Parser: class body block.
  Lower: class → struct in icn_proc_table; `new` → E_FNC("new") allocating hash;
  method call `$obj.bar()` → E_FNC("bar") with self as first arg.
  Test: `rk_oo.raku` — simple Point class with x/y and a `str` method.
  Gate: PASS=20.

### Sprint 13 — Roles

- [ ] **RK-24** — `role Printable { method print() { } }` / `class Foo does Printable { }`.
  Requires RK-23. Lower: role methods merged into class method table at `does` site.
  Test: `rk_roles.raku` — role with default method, class that does it.
  Gate: PASS=21.

### Sprint 14 — `grammar`/`rule`/`token` → BB_ONCE

- [ ] **RK-25** — `grammar G { rule top { <digit>+ }; token digit { <[0..9]> } }`.
  Requires RK-22. This is the original GOAL motivation: grammar/rule → BB_ONCE + OR-retry.
  Lexer: `grammar`, `rule`, `token`, `<name>` subrule call, `<[...]>` char class.
  Lower: each `rule` → a sub that tries alternatives via BB_ONCE broker mode.
  Test: `rk_grammar.raku` — simple grammar parsing digit sequences.
  Gate: PASS=22.

### Sprint 15 — Lazy lists and infinite ranges

- [ ] **RK-26** — `lazy gather { ... }`, `take-while`, infinite range `1..*`.
  Requires RK-22. `lazy` keyword defers gather evaluation. `1..*` lowers to
  E_TO with sentinel. `take-while { cond }` → E_SUSPEND inside E_WHILE.
  Test: `rk_lazy.raku` — `my @fibs = lazy gather { ... }; say(@fibs[10]);`.
  Gate: PASS=23.

## Current state

Session 2026-04-14: RK-1 and RK-2 DONE (Rung 0-5 green, 17/17 PASS).
Flex/Bison frontend complete: raku.l (prefix=raku_yy), raku.y
(api.prefix=raku_yy), raku_ast.h/c, raku_driver.h/c.
Supports: say/print, my $x=expr, arithmetic, string concat ~,
for RANGE->$var {}, if/else, while loop.
Fixed pre-existing U-22 bug: DESCR_t.type -> .v in scrip.c.
HEAD: ecc21def (SCRIP)
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

RK-4 (raku_compile, --run): DONE. HEAD e43b8dcc
  - raku_compile(src,filename)→CODE_t* added to raku_driver.c/h
  - scrip.c: .raku files now use raku_compile() → full --run path
  - LANG_RAKU shares icn_proc_table with LANG_ICN (same E_FNC shape)
  - polyglot_init, execute loop, post-loop dispatch all handle LANG_RAKU
  - Gates: hello world, arithmetic, concat, for 1..5 -> $i, if, while
  - Smoke: PASS=2 FAIL=0; lower gate: 28/28 PASS

Session 2026-04-14 (continued): RK-5, RK-6, RK-7 DONE. GOAL COMPLETE.

RK-5: Raku fence tag added to parse_scrip_polyglot; LANG_RAKU compile
      dispatch added; all other dispatch paths confirmed already present.
      make scrip clean.
RK-6: polyglot_init already handled LANG_RAKU via icn_proc_table sharing
      from RK-4. Confirmed. No new code needed.
RK-7: test/raku_gather.scrip + test/raku_gather.ref written and checked in.
      test_smoke_unified_broker.sh extended with Raku section (3 inline +
      1 polyglot file test). PASS=17 FAIL=0 (was 13).
HEAD: f2da733d (SCRIP)
All steps complete: RK-1 through RK-7. Done when clause satisfied.

Session 2026-04-14 (continued): RK-8, RK-9, RK-10 DONE.

Three bugs fixed in scrip.c / raku_lower.c:
  - E_MOD missing from icn_interp_eval → modulo now works
  - E_LEQ/E_CAT VARVAL_fn static-buffer aliasing → use .s directly for DT_S
  - RK_SUBDEF param wiring: e->ival was hardcoded 0; fixed to wire nparams
    and emit sigil-stripped E_VAR param children (icon_lower layout).
    Root cause: $x in body stripped to "x"; param node had "$x" → different
    scope slot → frame never populated → all params read as NULVCL.

Test corpus: test/raku/ — 7 files × (raku + expected):
  rk_arith, rk_strings, rk_vars, rk_control, rk_subs, rk_forloop, rk_gather.

scripts/test_raku_ir_rungs.sh: self-contained harness, PASS=7 FAIL=0.
Integrated into test_smoke_unified_broker.sh: PASS=24 FAIL=0 (was 17).

roast (github.com/Raku/roast) identified as official Raku test suite reference.
Our corpus is hand-written Tiny-Raku subset only — roast is full Raku.

Next: RK-11 (combinator parser demo — gather/take as PEG engine).
HEAD: 8646d030 (SCRIP)

Session 2026-04-14 (continued): RK-11 DONE.

Combinator parser demo: test/raku/rk_combinator.raku
PEG ordered-choice parser for digit (op digit)* — parses "3+4*2".
p_digit/p_addop/p_mulop/p_op combinators with ordered-choice via if/else (|| PEG semantics).
gather { take tok } block structurally present as BB_PUMP-ready generator.
In standalone --run, emit() (say) produces token stream directly.
In polyglot broker context, take() would suspend and yield to E_EVERY consumer.
Gate: PASS=8 FAIL=0 (raku harness); smoke PASS=26 FAIL=0.
HEAD: 2e0d5d46 (SCRIP)
Next: RK-12 (string interpolation).

Phase 5 plan (RK-12..RK-26) added: 15 sprints, easy→hard.
Sprint map: interp(12,13) → collections(14,15,16) → dispatch(17,18,19) →
  junctions(20) → hyper(21) → BB_PUMP standalone(22) → OO(23,24) →
  grammar/BB_ONCE(25) → lazy(26).

Session 2026-04-14 (continued): RK-12 DONE.

String interpolation in double-quoted strings: "hello $name" → expanded at runtime.
raku.l: LIT_INTERP_STR token emitted when closing " and buffer contains $.
raku.y: LIT_INTERP_STR token declared; atom rule → raku_node_interp_str().
raku_ast.h/c: RK_INTERP_STR enum value + raku_node_interp_str() constructor.
raku_lower.c: RK_INTERP_STR → walk raw string, split on $ident boundaries,
  build left-associative E_CAT(E_QLIT, E_VAR, ...) chain.
  Bug fixed: original while(i<=len) caused infinite loop; fixed to while(i<len)
  with trailing literal flush after loop exit.
scripts/regenerate_parser_and_lexer_from_sources.sh: raku section added.
test/raku/rk_interp.raku + .expected: 6 interpolation cases.
Gate: PASS=9 FAIL=0 (raku harness); smoke PASS=27 FAIL=0.
HEAD: 2e0d5d46 (SCRIP)
Next: RK-13 (given/when scalar smart-match).

Session 2026-04-14 (continued): RK-13 DONE.

given/when scalar smart-match lowered to nested E_IF chain.
raku.l: given, when, default, elsif keywords.
raku.y: given_stmt + when_list grammar rules; %type decls added.
raku_ast.h/c: RK_GIVEN/RK_WHEN/RK_DEFAULT; raku_node_given/raku_node_when constructors.
raku_lower.c: RK_GIVEN -> right-to-left E_IF chain; string when -> E_LEQ, int -> E_EQ.
test/raku/rk_given.raku + .expected: 6 cases (int + string when, default).
Gate: PASS=10 FAIL=0 raku; smoke PASS=28 FAIL=0.
SCRIP HEAD: 75ba531b
Next: RK-14 (arrays: push/pop/elems/index).

Session 2026-04-14 (continued): RK-14 DONE.

Arrays: push/pop/elems/arr_get/arr_set builtins; @arr[$i] get/set syntax.
Storage: \x01-separated strings in normal DESCR_t slots (no new runtime structs).
scrip.c: push writes back to caller env slot; pop removes last segment;
  arr_get walks segments by \x01; arr_set rebuilds string with replacement.
raku.y: @arr[$i] atom -> RK_ARR_GET; @arr[$i]=expr stmt -> RK_ARR_SET.
raku_ast.h/c: RK_ARR_GET + RK_ARR_SET + constructors.
raku_lower.c: both -> E_FNC("arr_get"/"arr_set") calls.
test/raku/rk_arrays.raku + .expected: int+string arrays, push/pop/index.
Gate: PASS=11 FAIL=0 raku; smoke PASS=29 FAIL=0.
SCRIP HEAD: 51fe9434
Next: RK-15 (hashes: %h<key>, %h{$k}, keys, values, exists).

Session 2026-04-14 (continued): RK-15 DONE.

Hash operations: %h<key>/%h{$k} sigil syntax + hash_get/set/exists/keys/values builtins.
Storage: \x02-separated "key\x03value" pair strings (distinct from array \x01 separator).
raku.l: '%' sigil -> VAR_HASH token.
raku.y: VAR_HASH token declared; my %h = expr; %h<key>=val; %h{expr}=val stmt rules;
  %h<key> and %h{expr} atom rules.
raku_ast.h/c: RK_HASH_GET + RK_HASH_SET enums + raku_node_hash_get/set() constructors.
raku_lower.c: strip_sigil extended to %; RK_HASH_GET/SET -> E_FNC(hash_get/set).
scrip.c: hash_set (upsert), hash_get, hash_exists, hash_keys (\x01-sep), hash_values (\x01-sep).
  Uses interp_eval (OE-5 landscape — icn_interp_eval is now a forwarder).
test/raku/rk_hashes.raku + .expected: set/get/exists/update + sigil syntax (9 assertions).
Gate: PASS=12 FAIL=0 raku; smoke PASS=30 FAIL=0.
SCRIP HEAD: dacec523
Next: RK-16 (for @arr -> $x with real array variable).
