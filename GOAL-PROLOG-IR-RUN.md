# GOAL-PROLOG-IR-RUN — Get Prolog Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.pl` files run correctly via `scrip --ir-run file.pl`, passing
the existing Prolog corpus rung tests.

---

## Current state (2026-04-12, one4all HEAD)

S-1 through S-9 complete. S-10a, S-10b, S-10c complete.
PASS=13/107.
Passing: rung01 rung02 rung03 rung04 rung05 rung06 rung07 rung08 rung09
         rung14_retract_all rung14_retract_nonexistent rung22_print rung23_max_min.

S-10c DONE: recursive backtracking fixed via continuation-passing interpreter.
  Root cause: the flat retry-loop in pl_exec_body exhausted inner recursive calls
  before retrying outer clauses. The CP for inner member(X,[b,c]) was popped before
  the suffix (write,nl,fail) ran, so longjmp on fail hit the outer CP at the wrong
  clause index.

  Fix: replaced pl_exec_body with pl_exec_body_k — a continuation-passing interpreter.
  For each user call U followed by suffix S:
    - Push CP with setjmp (retry point for this call site).
    - Build Body_cont(S, caller_env, outer_cont) as the continuation.
    - Run clause body via pl_exec_body_k(body, clause_env, ..., &suffix_bc).
    - suffix_bc invokes S in caller_env when body succeeds.
    - S failure longjmps back to the setjmp, advancing cp->next_clause.
  This mirrors emit_body's retry_N label pattern exactly: the suffix is
  inlined on the C stack below the inner CP, so failure propagates correctly.

  Architecture: Cont_t / Body_cont struct in prolog_interp.c.
  pl_exec_body() is a wrapper calling pl_exec_body_k(..., cont_done).
  pl_call() unchanged — used by pl_exec_goal for \+ and single-shot calls.

Next: S-10d findall/3.

SNOBOL4 smoke: sm-run PASS, ir-run PASS (x86 emit pre-existing failure).

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

- [x] **S-10a** — Fix `,/N`, `;/N`, `->/N` arity guards in pl_exec_goal (lowerer emits n-ary).
  Gate: rung02 PASS.

- [x] **S-10b** — Fix cut scope: cut must not short-circuit forward body execution;
  only prevents retry. pl_call uses own local cut_flag, never propagates past predicate boundary.
  Gate: rung07 PASS. ✓

- [x] **S-10c** — Replace Proebsting retry-loop with proper choice point stack for recursive backtracking.
  Flat retry-loop (start++) cannot backtrack into recursive sub-calls (e.g. member/2, append/3).
  Implement ChoicePoint struct {clause_idx, trail_mark, env snapshot} pushed on each user call;
  on failure pop and resume. Mirror pl_call's clause loop but save continuation across C stack frames.
  Gate: rung05 PASS (member/2 with fail-loop finds all 3 solutions).

- [ ] **S-10d** — `findall/3`: save trail mark, call Goal collecting solutions, restore trail.
  Gate: rung11 5/5 PASS.

- [ ] **S-10e** — `assertz/asserta/retract/abolish`: dynamic predicate table mutation.
  Gate: rung13 5/5, rung14 5/5, rung15 5/5.

- [ ] **S-10f** — atom builtins: `atom_length/2`, `atom_chars/2`, `atom_codes/2`, `atom_concat/3`.
  Gate: rung12 5/5.

- [ ] **S-10g** — `@</2`, `@>/2`, `@=</2`, `@>=/2` term ordering comparisons.
  Gate: rung16 5/5.

- [ ] **S-10h** — `sort/2`, `msort/2`.
  Gate: rung17 5/5.

- [ ] **S-10i** — `succ/2`, `plus/3`.
  Gate: rung18 5/5.

- [ ] **S-10j** — `format/2` (`~w`, `~a`, `~d`, `~i`, `~n`).
  Gate: rung19 5/5.

- [ ] **S-10k** — `numbervars/3`.
  Gate: rung20 5/5.

- [ ] **S-10l** — `char_type/2`.
  Gate: rung21 5/5.

- [ ] **S-10m** — `write_canonical/1`, `writeq/1`, `print/1`.
  Gate: rung22 5/5.

- [ ] **S-10n** — arith ext: bitwise ops, `max/min`, `**`, `sign`, `truncate/round/floor/ceiling`.
  Gate: rung23 5/5.

- [ ] **S-10o** — string/IO builtins: `atom_string`, `number_string`, `string_concat`, `string_length`, `string_lower/upper`.
  Gate: rung24 5/5.

- [ ] **S-10p** — `term_string/2`, `term_to_atom/2`.
  Gate: rung25 5/5.

- [ ] **S-10q** — `copy_term/2`, `concat_atom/2`, `atom_to_term/3`.
  Gate: rung26 5/5.

- [ ] **S-10r** — aggregate: `nb_setval/nb_getval`, `aggregate_all`.
  Gate: rung27 5/5.

- [ ] **S-10s** — exceptions: `throw/1`, `catch/3`.
  Gate: rung28 5/5.

- [ ] **S-10t** — float ops: `float/1`, `float_integer_part`, `float_fractional_part`, `sin/cos/exp/log`, `gcd`.
  Gate: rung29 5/5.

- [ ] **S-10u** — DCG: `phrase/2,3`, `-->` rule expansion.
  Gate: rung30 5/5.

- [ ] **S-11** — Run rung01–rung05 full Prolog corpus ladder.
  Gate: PASS count matches or exceeds prior JVM-emitter baseline.

- [ ] **S-12** — Add `test/frontend/prolog/run_prolog_ir_rung.sh` runner.
  Gate: script runs clean, results reproducible.

- [ ] **S-13** — Update PLAN.md ☑ done.

---

## Phase 1B — Unify: eliminate prolog_interp.c, wire Prolog into execute_program()

**Architectural correction.** SCRIP has one IR and one `--ir-run` interpreter:
`execute_program()` in `scrip.c`. The six Prolog IR nodes (`E_CHOICE`, `E_CLAUSE`,
`E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`) are already canonical in
`ir.h` alongside SNOBOL4 and Icon nodes. The separate `pl_execute_program()` /
`prolog_interp.c` tree-walker is wrong — it duplicates interpreter infrastructure
that belongs in one place. These steps eliminate it.

All Prolog runtime helpers (unify, trail, term, atom, builtin) remain as support
libraries — only the top-level dispatch loop and clause/choice execution move into
`execute_program()`.

- [ ] **S-1B-1** — Add Prolog runtime state to `execute_program()`:
  Trail, atom table, predicate table (functor/arity → E_CHOICE*), CP stack.
  Build predicate table by walking `prog->head` stmts at program start,
  identical to what `pl_execute_program()` does today.
  Gate: compiles clean; no behaviour change yet.

- [ ] **S-1B-2** — Add `interp_eval_prolog_term()` to `scrip.c`:
  Converts `EXPR_t*` → `Term*` using a per-clause variable env.
  Mirrors `pl_term_from_expr()` from `prolog_interp.c` — move, don't duplicate.
  Gate: compiles clean.

- [ ] **S-1B-3** — Add `E_CHOICE` / `E_CLAUSE` handling to `execute_program()`
  statement loop. When the top-level stmt subject is `E_CHOICE` (predicate
  definition), register it in the predicate table. When stmt subject is `E_CLAUSE`
  (a bare clause at top level), execute it directly. Entry point: call `main/0`
  after all stmts are registered, using the shared CP-stack dispatcher.
  Gate: `./scrip --ir-run hello.pl` prints `Hello, World!`.

- [ ] **S-1B-4** — Add `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`,
  `E_FNC` (Prolog builtins) to `interp_eval()` in `scrip.c`.
  These are goal-context evaluations: return success/failure signal rather than
  a DESCR_t value. Add a `interp_exec_goal()` wrapper that dispatches by kind.
  Gate: rung01–rung04 still PASS, rung07 still PASS.

- [ ] **S-1B-5** — Delete `prolog_interp.c` and `prolog_interp.h`.
  Remove `pl_execute_program()` call from `scrip.c` main dispatch.
  Remove `lang_prolog` branch that called `pl_execute_program()` — Prolog now
  falls through to the unified `execute_program()` path.
  Gate: `make scrip` clean; all previously passing rungs still PASS.

- [ ] **S-1B-6** — Run full rung01–rung09 regression. Fix any delta.
  Gate: PASS count ≥ 12/107 (session-start baseline).

---

## Key files
| File | Role |
|------|------|
| `src/ir/ir.h` | Canonical IR node kinds — 6 Prolog nodes already defined |
| `src/driver/scrip.c` | `execute_program()` — THE one IR interpreter; Prolog goes here |
| `src/frontend/prolog/prolog_lower.c` | `prolog_lower()` → `Program*` (frontend, keep) |
| `src/frontend/prolog/prolog_lower.h` | E_CLAUSE layout documentation (keep) |
| `src/frontend/prolog/prolog_unify.c` | `unify()`, `trail_*` — runtime support, keep |
| `src/frontend/prolog/prolog_runtime.h` | `Trail`, `EnvLayout` types — keep |
| `src/frontend/prolog/term.h` | `Term` type — keep |
| `src/frontend/prolog/prolog_interp.c` | DELETE after Phase 1B complete |
| `src/frontend/prolog/prolog_interp.h` | DELETE after Phase 1B complete |
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
