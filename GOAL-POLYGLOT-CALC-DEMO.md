# GOAL-POLYGLOT-CALC-DEMO.md — Polyglot Demo: Icon Generator + Snocone Parser

**Repo:** one4all
**Done when:** A `.scrip` demo file runs end-to-end where Icon generates random
calculator expressions (strings like `"3 + 47 * 2"`) and the Snocone section
parses and evaluates each one, printing the result. Output is deterministic
(seeded RNG) and matched against a `.ref` file. Gate passes.

---

## Motivation

The unified broker makes cross-language calls natural. This demo makes that
concrete and compelling: two languages doing what each does best in one file.

- **Icon** — generator idiom. `every` + random number generation produces a
  lazy stream of expression strings. BB_PUMP drives the generator; each tick
  yields one expression to the Snocone section.
- **Snocone** — pattern/parse idiom. Snocone's recursive descent grammar
  parses the expression string, evaluates it, prints `expr = result`.

This is `demo11` (the first cross-language demo). It follows the `demo/scrip/`
naming convention and the `.scrip` fenced-block format.

---

## Architecture

```
Icon section (BB_PUMP generator)
  every generate_expr(seed) →  "3 + 47 * 2"
                             →  "12 - 5 * 3"
                             →  ... (N expressions)
        ↓  cross-call (U-22)
Snocone section
  parse_and_eval(expr_str)  →  "3 + 47 * 2 = 97"
                             →  "12 - 5 * 3 = -3"
                             → print result
```

The Icon section drives; the Snocone section is called per-expression.
Both sections live in one `.scrip` file. No host language needed.

---

## Steps

### Phase 1 — Icon generator

- [ ] **PC-1** — Write `demo/scrip/demo11/calc_demo.scrip` Icon section.
  `procedure generate_expr(seed, n)`: uses a simple LCG (seed-based) to
  produce `n` infix expressions over `+`, `-`, `*` with integer operands
  1–99. Each expression is a string. `every` suspends after each one.
  No floating point — integer arithmetic only. Keep expressions to depth 1
  (two operands, one operator) for Phase 1 simplicity.
  Gate: Icon section standalone (`scrip --ir-run` with a `main` that calls
  `generate_expr` and `write`s each) produces expected output.

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
  Gate: `scrip --ir-run calc_demo.scrip` produces deterministic output
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

- Seed the Icon RNG so output is deterministic and `.ref`-testable.
- Snocone is the right parser here — its pattern primitives (BREAK/SPAN/LEN)
  are exactly suited to tokenising infix expressions. SNOBOL4 could do it too
  but Snocone is cleaner for structured parsing.
- Future: extend to depth-2 expressions (nested parens) once PC-4 is green.
- Future: PROLOG section validates results via arithmetic predicates (is/2).

---

## Current state

Goal created 2026-04-14. No steps started. Prerequisite: U-22 complete.
