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

- [ ] **RK-1** — `src/frontend/raku/raku_lex.c` + `raku_lex.h`.
  Tokens: integer/string literals, `$`-sigil vars, `@`-sigil arrays,
  keywords (`gather`, `take`, `for`, `my`, `say`, `print`, `if`, `while`),
  operators (`+ - * / ~ = := ==`), punctuation `{ } ( ) ; ,`.
  Gate: tokeniser round-trips test snippets correctly.

- [ ] **RK-2** — `src/frontend/raku/raku_parse.c` + `raku_parse.h`.
  Recursive descent. Produces a `RakuNode*` AST (same pattern as Icon's
  `IcnNode*`). Parses the supported subset from RK-1.
  Gate: parses `gather { take $_ for 1..5 }` without error.

### Phase 2 — Lowering to IR

- [ ] **RK-3** — `src/frontend/raku/raku_lower.c` + `raku_lower.h`.
  `raku_lower_file(RakuNode**, int, int*) → EXPR_t**`.
  Key mappings:
  - `gather { ... }` → `E_ITERATE` wrapping body (mirrors Icon `every`)
  - `take expr`      → `E_SUSPEND` (yield one value, same as Icon suspend)
  - `for @arr -> $x` → `E_TO` / `E_ITERATE` over array elements
  - `say expr`       → `E_FNC("write", [expr])`  (reuse Icon write builtin)
  - `my $x = expr`   → `E_VAR` assignment
  Gate: lowers `gather { take $_ for 1..3 }` to IR that `icn_eval_gen`
  can drive via BB_PUMP.

- [ ] **RK-4** — `src/frontend/raku/raku_driver.c` + `raku_driver.h`.
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

## Current state

Goal created 2026-04-14. No steps started.
Prerequisite: GOAL-UNIFIED-BROKER complete (U-1..U-20 done ✓).
Recommended: U-22 complete before RK-6 (cross-call).
