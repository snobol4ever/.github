# GOAL-POLYGLOT-CALC-DEMO.md — Polyglot Demo: Icon Generator + Snocone Parser

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
**Done when:** A `.scrip` demo file runs end-to-end where Icon generates random
calculator expressions (strings like `"3 + 47 * 2"`) and the Snocone section
parses and evaluates each one, printing the result. Output is deterministic
(seeded RNG) and matched against a `.ref` file. Gate passes.

---

## Motivation

The unified broker makes cross-language calls natural. This demo makes that
concrete and compelling: two languages doing what each does best in one file.

- **Icon** — generator idiom. Each BNF production is an Icon procedure that
  suspends (`suspend`) once per alternative. Productions compose: calling a
  production from another production chains generators, so the whole grammar
  is a lazy generator tree driven by BB_PUMP. This is the classic Icon
  "BNF-as-generators" pattern — each nonterminal is a procedure that yields
  every string it can derive, on demand.
- **Snocone** — pattern/parse idiom. Snocone's recursive descent grammar
  parses the expression string, evaluates it, prints `expr = result`.

This is `demo11` (the first cross-language demo). It follows the `demo/scrip/`
naming convention and the `.scrip` fenced-block format.

---

## Architecture

```
Icon section (BB_PUMP generator tree — BNF-as-generators)

  procedure expr()          ← nonterminal: every derivation of <expr>
      suspend (term() || " + " || term())
      suspend (term() || " - " || term())

  procedure term()          ← nonterminal: every derivation of <term>
      suspend (factor() || " * " || factor())
      suspend factor()

  procedure factor()        ← nonterminal: every leaf
      suspend string(?(1 + ?98))   ← random integer 1..99

  every write(expr())       ← drives the generator; each tick = one expression
        ↓  yields: "3 + 47 * 2",  "12 - 5 * 3", ...
        ↓  cross-call (U-22)
Snocone section
  parse_and_eval(expr_str)  →  "3 + 47 * 2 = 97"
                             →  "12 - 5 * 3 = -3"
                             →  print result
```

Each Icon procedure IS a BNF production. `suspend` makes it a generator.
Composing productions composes generators — the full expression language
falls out of the structure, not from explicit iteration. The broker (BB_PUMP)
drives the whole tree without any explicit loop at the call site.

---

## BNF being generated

```
<expr>   ::= <term> "+" <term>
           | <term> "-" <term>

<term>   ::= <factor> "*" <factor>
           | <factor>

<factor> ::= integer (1..99, seeded RNG)
```

Phase 1: depth-1 (one operator). Each production has 1–2 alternatives.
Future: add division, parenthesised subexpressions (recursive), variables.

---

## Steps

### Phase 1 — Icon generator (BNF-as-generators)

- [ ] **PC-1** — Write `demo/scrip/demo11/calc_demo.scrip` Icon section.
  Three procedures: `factor()`, `term()`, `expr()`. Each is a BNF production
  implemented as an Icon generator using `suspend`. `factor()` yields a
  random integer string (seeded LCG so output is deterministic). `term()`
  yields `factor() || " * " || factor()` and plain `factor()`. `expr()`
  yields `term() || " + " || term()` and `term() || " - " || term()`.
  Top-level: `every generate(n)` calls `expr()` and suspends each result,
  stopping after `n` expressions.
  Gate: Icon section standalone (`scrip --interp` with a `main` that drives
  `generate(5)` and writes each) produces 5 deterministic expression strings.

### Phase 2 — Snocone parser/evaluator

- [ ] **PC-2** — Write the Snocone section: `parse_and_eval(s)`.
  Snocone pattern: `INTEGER OP INTEGER` where INTEGER = `SPAN(&DIGITS)`,
  OP = one of `+`, `-`, `*`. Extract operands and operator, compute result,
  print `s ' = ' result`. Fail on malformed input (print `? s`).
  Gate: Snocone section standalone parses and evaluates a fixed set of
  expressions correctly.

### Phase 3 — Cross-language wiring

- [ ] **PC-3** — Wire U-22 cross-call: Icon generator calls Snocone
  `parse_and_eval` per expression. Requires U-22 (SNO→ICN cross-call) to be
  working. If U-22 is not yet complete, use a SNOBOL4 bridge section instead:
  SNO drives the Icon generator via BB_PUMP and calls Snocone parse_and_eval.
  Gate: `scrip --interp calc_demo.scrip` produces deterministic output
  (seed = 42, n = 5 expressions).

### Phase 4 — Ref file and test integration

- [ ] **PC-4** — Generate `.ref` file using SPITBOL to validate the arithmetic
  (SPITBOL verifies the expected results are correct). Add
  `calc_demo.expected` for the full polyglot output. Extend
  `scripts/test_scrip_demos.sh` to include demo11. Gate: demo test suite
  passes including demo11.

---

## Key files

| File | Role |
|------|------|
| `demo/scrip/demo11/calc_demo.scrip` | The polyglot demo |
| `demo/scrip/demo11/calc_demo.expected` | Expected output (3 lines: Icon drives 5 exprs × SNO/SCN output) |
| `scripts/test_scrip_demos.sh` | Extended to include demo11 |

---

## Prerequisite

U-22 (GOAL-UNIFIED-BROKER cross-call hook) should be complete before PC-3.
PC-1 and PC-2 can proceed independently.

---

## Notes

- **BNF-as-generators** is the key architectural insight: in Icon, a grammar
  production and a generator are the same thing. `suspend` inside a procedure
  makes it yield one derivation per call. Composing productions composes
  generators — no explicit iteration, no list accumulation. This is Icon
  doing what it was designed for. The broker (BB_PUMP) drives the whole
  derivation tree from outside.
- Seed the Icon RNG so output is deterministic and `.ref`-testable.
- Snocone is the right parser here — its pattern primitives (BREAK/SPAN/LEN)
  are exactly suited to tokenising infix expressions. SNOBOL4 could do it too
  but Snocone is cleaner for structured parsing.
- Future: extend `expr()` to recursive depth (parenthesised subexpressions).
  Each level of recursion is just another `suspend` alternative — the BNF
  structure maps directly.
- Future: add a PROLOG section that validates results via `is/2` arithmetic.
  Three languages, three roles: Icon generates, Snocone parses, Prolog verifies.

---

## Current state

Goal created 2026-04-14. No steps started. Prerequisite: U-22 complete.
