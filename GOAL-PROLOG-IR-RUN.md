# GOAL-PROLOG-IR-RUN — Get Prolog Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.pl` files run correctly via `scrip --ir-run file.pl`, passing
the existing Prolog corpus rung tests.

---

## Current state (2026-04-12, one4all 2f32fba5)

S-1 through S-9 complete (prolog_interp.c, one4all 4b4e7b3c).
hello.pl: PASS. palindrome.pl: needs string_chars/2. queens.pl: needs format/2.
SNOBOL4 regression: PASS=204 unchanged.

```
./scrip --ir-run test/prolog/hello.pl
→ Error 5 in statement 1  (E_CHOICE not handled in interp_eval)
```

**IR structure produced by `prolog_lower()`:**
- One `STMT_t` per predicate, subject = `E_CHOICE` node
- `E_CHOICE`: `sval="foo/2"`, children = `E_CLAUSE` nodes (one per clause)
- `E_CLAUSE`: `ival=n_vars`, `dval=n_args`,
  `children[0..n_args-1]` = head arg terms,
  `children[n_args..]` = body goals
- Body goals: `E_FNC` (calls), `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`
- Terms: `E_QLIT` (atoms), `E_ILIT` (integers), `E_VAR` (ival=slot index),
  `E_FNC` (compound terms / calls)

**Runtime infrastructure already available:**
- `Trail`, `trail_init()`, `trail_push()`, `trail_unwind()`, `trail_mark()` — `prolog_unify.c`
- `unify(t1, t2, trail)` — full Robinson unification with trail — `prolog_unify.c`
- `Term` heap type — `term.h`

**Execution model needed:** mini-WAM interpreter in `scrip.c`:
- Variable env = `Term*[]` array, one slot per `n_vars`
- Call stack for goal continuation
- `E_CHOICE` α/β: try clauses in order, backtrack on fail
- `E_CLAUSE` α: unify head args, execute body goals in sequence
- `E_UNIFY`: call `unify()` on two lowered terms
- `E_CUT`: seal β port of enclosing choice (no more backtrack past here)
- `E_TRAIL_MARK` / `E_TRAIL_UNWIND`: save/restore trail top

---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

- [x] **S-1** — Add Prolog frontend files to Makefile.
  Gate: `make scrip` clean with prolog objects included.

- [x] **S-2** — Write `prolog_driver.c` + wire `.pl` in `scrip.c`.
  Gate: `./scrip --ir-run hello.pl` reaches ir-run (Error 5, not parse error).

- [x] **S-3** — Allocate `PlInterp` state in `scrip.c` for Prolog programs:
  `Trail`, global atom table pointer, predicate lookup table (functor/arity → `E_CHOICE*`).
  Build predicate table by walking `prog->head` stmts (each stmt subject is one `E_CHOICE`).
  Gate: predicate table built, `write/1` and `nl/0` registered as builtins.

- [x] **S-4** — Implement `pl_term_from_expr()`: convert lowered `EXPR_t` to `Term*`
  using a per-call variable env (`Term*[n_vars]`).
  Handles: `E_QLIT`→atom, `E_ILIT`→integer, `E_VAR`→env slot, `E_FNC`→compound.
  Gate: `write('Hello, World!')` argument converts to correct atom Term.

- [x] **S-5** — Implement `pl_call_builtin()`: handle `write/1`, `nl/0`, `fail/0`, `true/0`.
  Gate: `./scrip --ir-run test/prolog/hello.pl` prints `Hello, World!`.

- [x] **S-6** — Implement `pl_exec_body()`: execute a sequence of body goals
  (children of `E_CLAUSE` after the head args) left to right.
  Each goal is an `E_FNC` → look up predicate → call `pl_exec_choice()`.
  Gate: `main/0` body executes `write` + `nl` in sequence.

- [x] **S-7** — Implement `pl_exec_choice()`: α/β over `E_CLAUSE` children.
  For each clause: `trail_mark()`, unify head args, on success execute body,
  on fail `trail_unwind()` and try next clause.
  Gate: single-clause predicates work; `hello.pl` passes fully.

- [x] **S-8** — Implement `E_UNIFY` in body: call `unify(t1, t2, trail)`.
  Implement `E_CUT`: set a flag that prevents β from trying further clauses.
  Gate: programs using `=` and `!` work correctly.

- [x] **S-9** — Implement `E_TRAIL_MARK` / `E_TRAIL_UNWIND` in body goals.
  Gate: multi-clause predicates with backtracking work.

- [ ] **S-10** — Run rung01 Prolog corpus tests. Fix failures one at a time.
  Gate: rung01 PASS count ≥ prior JVM-emitter baseline.

- [ ] **S-11** — Run rung01–rung05 full Prolog corpus ladder.
  Gate: PASS count matches or exceeds prior JVM-emitter baseline.

- [ ] **S-12** — Add `test/frontend/prolog/run_prolog_ir_rung.sh` runner.
  Gate: script runs clean, results reproducible.

- [ ] **S-13** — Update PLAN.md ☑ done.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/prolog/prolog_lower.c` | `prolog_lower()` → `Program*` |
| `src/frontend/prolog/prolog_lower.h` | E_CLAUSE layout documentation |
| `src/frontend/prolog/prolog_unify.c` | `unify()`, `trail_*` — use as-is |
| `src/frontend/prolog/prolog_runtime.h` | `Trail`, `EnvLayout` types |
| `src/frontend/prolog/term.h` | `Term` type |
| `src/driver/scrip.c` | Add `pl_*` interpreter functions here (S-3–S-9) |
| `test/prolog/hello.pl` | Primary smoke test |
| `test/prolog/palindrome.pl` | Secondary smoke test |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate before every commit: `make scrip` + `run_interp_broad.sh` must not regress.
- No ad-hoc builds — use/extend `Makefile` and `test/` scripts.

---

## Phase 2 — Stack Machine and x86 Byrd Box execution

Once `--ir-run` (tree-walk interpreter) is passing corpus tests, Prolog should
graduate to the same execution pipeline as SNOBOL4: SM lowering → SM interpreter
→ JIT x86 Byrd boxes. The Proebsting technique that `prolog_emit.c` already
implements in C output maps directly to the SM instruction set.

- [ ] **S-14** — Wire Prolog IR through `sm_lower.c`:
  Add cases for `E_CLAUSE`, `E_CHOICE`, `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`,
  `E_TRAIL_UNWIND` in `sm_lower()`. Each Byrd box port (α/β/γ/ω) maps to
  SM instructions exactly as SNOBOL4 patterns do.
  Gate: `./scrip --sm-run hello.pl` produces `Hello, World!`.

- [ ] **S-15** — Wire Prolog IR through `sm_codegen.c` (x86 JIT):
  Add x86 emission for the Prolog SM opcodes. The Byrd box wiring (α→β→γ→ω)
  is identical to the pattern engine — reuse the existing four-port infrastructure.
  Gate: `./scrip --jit-run hello.pl` produces `Hello, World!`.

- [ ] **S-16** — Run full Prolog corpus on `--jit-run`. Fix failures.
  Gate: PASS count matches `--ir-run` baseline.

- [ ] **S-17** — Update PLAN.md ☑ done (Phase 2).

---

## Phase 2 architecture note

`prolog_emit.c` already generates C with labeled gotos that is structurally
identical to what `sm_codegen.c` emits for SNOBOL4 patterns. The mapping is:

| Prolog emit_clause construct | SM instruction |
|------------------------------|---------------|
| α entry label                | `SM_CLAUSE_ALPHA` |
| β retry label                | `SM_CLAUSE_BETA` |
| `trail_mark()` + head unify  | `SM_UNIFY` |
| `trail_unwind()` on fail     | `SM_TRAIL_UNWIND` |
| body goal call               | `SM_CALL` |
| γ success goto               | `SM_GOTO_GAMMA` |
| ω failure goto               | `SM_GOTO_OMEGA` |

These SM opcodes may need to be added to `sm_prog.h` if not already present.
Check `sm_prog.h` and `sm_lower.c` before starting S-14.
