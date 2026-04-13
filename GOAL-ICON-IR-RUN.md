# GOAL-ICON-IR-RUN — Get Icon Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.icn` files run correctly via `scrip --ir-run file.icn`, passing
rung01–rung11 of the Icon corpus ladder.

---

## Current state (2026-04-12, one4all f6439fd7)

**Score: 45/59 PASS through unified interpreter in scrip.c**

Icon now runs through `icn_execute_program_unified` → `icn_interp_eval` →
`icn_call_proc` in `scrip.c` — same file as SNOBOL4 `execute_program` /
`interp_eval`. One IR, one interpreter.

Old fork (`icon_execute_program` / `icn_exec` / `IcnVal` in `icon_interp.c`)
is superseded but not yet deleted — kept until unified path reaches 46/59+.

**Unified path failures (14):**
- rung03 suspend (3): E_SUSPEND needs setjmp/longjmp (S-11)
- rung05 scan (5): &subject keyword + nested scan restore
- rung06_cset_any_fail (1): & conjunction short-circuit (S-9)
- rung08 find_gen + match (2): find() generator form (S-7) + scan pos reset
- rung11 bang (2): E_ITERATE / !str not yet implemented (S-6)
- rung01_nested_to (1): nested every cross-product generator

| Rung | Feature | PASS | FAIL | Notes |
|------|---------|------|------|-------|
| rung01 | generators (paper examples) | 6/6 | 0 | ✅ complete |
| rung02_arith_gen | arithmetic generators | 5/5 | 0 | ✅ complete |
| rung02_proc | user procedures, params, return | 2/3 | 1 | locals accumulation |
| rung03 | suspend / user generators | 1/5 | 4 | suspend not implemented |
| rung04_string | string concat | 5/5 | 0 | ✅ complete |
| rung05 | string scanning (?) | 2/5 | 3 | &subject, nested scan |
| rung06 | cset builtins | 4/5 | 1 | & conjunction short-circuit |
| rung07 | control flow | 5/5 | 0 | ✅ complete |
| rung08 | string builtins | 4/5 | 1 | find() as generator |
| rung09 | loops | 5/5 | 0 | ✅ complete |
| rung10 | augmented ops | 4/5 | 1 | break_while |
| rung11 | augmented concat, ! bang | 2/5 | 3 | !string/!list |

---

## Architecture — READ THIS FIRST every session

### What the emitter does
`emit_x64.c` emits Byrd boxes as x86 NASM labels. Each `emit_*` function
takes `(node, γ, ω, *out_α, *out_β)` and emits:
- **α label**: entry point — evaluate, push value, jump γ (succeed)
- **β label**: re-entry point — advance state, push next value, jump γ; or jump ω (exhausted)
- γ = success continuation (caller's next step)
- ω = failure/backtrack continuation (caller's retry)

`emit_every(gen, body)` wires: gen-α → body → gbfwd → gen-β → body → gbfwd → ... → ω

### The correct interpreter approach
**Translate each `emit_*` function directly into a C function** — same logic,
no assembly emission. This is exactly what `engine.c` did for SNOBOL4 patterns:
`engine.h` implements PROCEED/SUCCEED/CONCEDE/RECEDE + Psi/Omega stacks over
`Pattern*` nodes. The Icon interpreter needs the same over `EXPR_t` + `IcnVal`.

**Template: `engine.h`** — copy its structure:
- Four signals: PROCEED=0 SUCCEED=1 CONCEDE=2 RECEDE=3
- Psi stack: continuation stack (where to go on success)
- Omega stack: backtrack stack, each entry owns a deep-copied Psi snapshot
- Dispatch: `(node_type << 2 | signal)` — one switch, no indirect calls

**OR simpler (Prolog model):** The C call stack IS the Psi stack. Each emit_*
becomes a C function; β re-entry is a for-loop in the caller (like
`pl_exec_choice` iterating clauses). This works for non-coroutine generators:

```c
// emit_to → icn_exec_to: α sets up lo/hi; β = loop increment
// emit_every → icn_exec_every: for-loop calls gen then body each tick
// emit_bang → icn_exec_bang: for-loop over string chars
// emit_find → icn_exec_find: for-loop over match positions
```

For `suspend` (rung03) — genuine β re-entry across procedure boundaries —
`setjmp/longjmp` is required (or ucontext). That's S-11.

### What the current interpreter does (and why it's wrong)
`icn_exec()` is a recursive tree-walker returning 1/0. It does NOT implement
Byrd boxes. `icn_collect()` pre-materialises all generator values into an array
— this is wrong because:
- Side-effecting expressions (assignments) don't re-evaluate between ticks
- `find()` only returns first match
- `!string` doesn't generate all characters
- `suspend` cannot be pre-collected at all

### The fix (one emit_* at a time, incremental rungs)
Do NOT rewrite everything at once. Translate one `emit_*` to C per step,
gate on the rung it fixes. Consult `emit_x64.c` for each node before touching
`icon_interp.c`. Follow the Prolog model (for-loop β re-entry) for all
generators except `suspend` (which needs setjmp/longjmp).

### SCRIP broker/driver — check before starting
Before implementing, check whether SCRIP has a central broker/driver that
could host the Icon Byrd-box engine. Pattern: `engine.c` is shared across
SNOBOL4 modes. Is there an analogous driver for Icon expressions? Check
`src/driver/scrip.c` and `src/runtime/x86/` for any reusable dispatch
infrastructure.

---

## Steps

- [x] **S-1** — Add Icon frontend files to Makefile.
- [x] **S-2** — Write `icon_driver.c/h`.
- [x] **S-3** — Wire `.icn` in `scrip.c`.
- [x] **S-4** — `icn_exec()` initial (rung01, rung02_arith_gen pass).
- [x] **S-5** — E_RETURN, E_IF, ICN_GLOBAL lowering, scope/slots, E_KEYWORD.
  (rung04, rung07, rung09 now complete; rung02_proc 2/3)

- [x] **S-5B** — Translate `emit_to` → C for-loop β re-entry.
  Implemented `icn_exec_driven` with gen-substitution stack (gen_stack[16]).
  Fixes `every total := total + (1 to n)` and cross-product generators.
  Gate: rung02_proc 3/3. ✅ Score: 46/59 on old fork.

- [ ] **S-5C** — Unify Icon IR interpreter into scrip.c (one interpreter).
  **IN PROGRESS — 45/59 PASS.** One IR, one interpreter.
  Implemented in scrip.c:
  - `icn_execute_program_unified`: proc table + call main
  - `icn_interp_eval(root,e)→DESCR_t`: all Icon node kinds
  - `icn_call_proc`: frame push/pop with `icn_scope_patch`
  - `icn_scope_patch`: adds ALL E_VAR names to scope (including undeclared)
  - `icn_drive`: β re-entry gen stack using DESCR_t
  - `icn_scan_subj/pos/stack/depth`, `icn_loop_break` globals
  - String relops (E_LEQ/LNE/LLT/LLE/LGT/LGE), scan builtins in E_FNC
  Key bug fixed: E_FNC name in children[0]->sval; undeclared vars added to scope.
  Remaining: delete `icon_interp.c` fork once 46/59+ reached.
  Gate: 46/59+ PASS through unified path; `icon_execute_program` deleted.

- [ ] **S-6** — Translate `emit_bang` → C for-loop over string chars.
  `!str` generates each character; β = advance position.
  Gate: rung11 5/5.

- [ ] **S-7** — Translate `emit_find` (find() builtin) → C for-loop over positions.
  `find(pat,str)` generates all match positions; β = advance past last match.
  Gate: rung08 5/5.

- [ ] **S-8** — Fix `&subject` / `&pos` in scan context (rung05).
  Trace &subject: icon_parse.c → icon_lower.c → icn_exec.
  Is it E_KEYWORD("subject") or E_VAR("&subject")? Verify node kind emitted.
  Gate: rung05 5/5.

- [ ] **S-9** — Fix `&` conjunction short-circuit (rung06_cset_any_fail).
  `any(cs) & expr` must not execute expr if any() fails.
  Check how `&` is lowered (E_AND? E_CONJ? E_SEQ?); mirror emit_and.
  Gate: rung06 5/5.

- [ ] **S-10** — Fix nested scan subject restore (rung05_scan_nested).
  Gate: rung05 5/5.

- [ ] **S-11** — Translate `emit_suspend` → C using setjmp/longjmp.
  `suspend expr` = yield expr, resume body on β re-entry.
  This is the only node requiring genuine coroutine semantics.
  Mirror emit_suspend() + emit_every() composition in emit_x64.c.
  Gate: rung03 5/5.

- [ ] **S-12** — Full rung01–rung11 pass. Gate: 59/59.
- [ ] **S-13** — Add run_icon_ir_rung.sh runner script.
- [ ] **S-14** — Update PLAN.md done.

---

## Phase 2 — Stack Machine and x86 Byrd Box execution

- [ ] **S-15** — Wire Icon IR through sm_lower.c.
- [ ] **S-16** — Wire Icon IR through sm_codegen.c (x86 JIT).
- [ ] **S-17** — Run full rung ladder on --jit-run.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/icon/icon_interp.c` | Interpreter — translate emit_x64.c to C |
| `src/backend/emit_x64.c` | **Canonical reference — read before every node** |
| `src/runtime/x86/engine.h` | Byrd-box engine template (PROCEED/SUCCEED/CONCEDE/RECEDE) |
| `src/runtime/x86/engine.c` | Byrd-box engine implementation — study this |
| `src/frontend/prolog/prolog_interp.c` | Prolog model: for-loop β re-entry |
| `src/ir/ir.h` | EKind enum — all Icon node kinds |
| `corpus/programs/icon/rung*` | Test programs |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate: `make scrip` clean + SNOBOL4 PASS=204 unchanged after every commit.
- **Read `emit_x64.c` for the node BEFORE implementing it.**
- **One emit_* per step. Gate on its rung. Do not batch.**
- Generator β re-entry = for-loop in C (Prolog model), NOT icn_collect array.
- `suspend` only: use setjmp/longjmp for genuine β re-entry.
