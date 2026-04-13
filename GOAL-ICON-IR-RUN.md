# GOAL-ICON-IR-RUN — Get Icon Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.icn` files run correctly via `scrip --ir-run file.icn`, passing
rung01–rung11 of the Icon corpus ladder.

---

## Current state (2026-04-12, one4all 3cceedf5 + session changes uncommitted)

**Session findings (critical architecture notes):**

1. **Generator model must mirror Byrd boxes** — `icn_collect()` pre-materialising
   values is wrong. The emitter emits Byrd boxes (α/β/γ/ω); the interpreter must
   mirror the same protocol. Follow the Prolog model: `pl_exec_choice` is a for-loop
   where each iteration is one β re-entry. `icn_drive(gen, env, body)` is the C
   translation of `emit_every`'s `gbfwd` wiring — a for-loop that drives gen's
   α then repeated β, running body each iteration. Consult `emit_every`,
   `emit_to`, `emit_bang` in `emit_x64.c` before touching any generator node.

2. **`E_IF` was missing** — `if cond then E [else E]` is a Byrd-box goal: cond
   succeeds (γ) or fails (ω). Without it, `if`-containing procs segfaulted.
   Added this session: `E_IF`, `E_GLOBAL` (no-op), `E_KEYWORD` (&subject/&pos).

3. **`ICN_GLOBAL` lowering was dropping local names** — fixed: now lowers to
   `E_GLOBAL` with `E_VAR` children so `icn_call` can build scope.

4. **Scope/slot resolution added** — `icn_call` now builds a name→slot map from
   param names + `E_GLOBAL` local decl children, patches `E_VAR.ival` in body.

5. **`g_returning` propagation fixed** — body loop breaks on return, uses
   `g_return_val`, restores `prev_returning` for recursive calls.

**Score after this session: 45/59 PASS** (was 38/59 at session start)

| Rung | Feature | PASS | FAIL | Notes |
|------|---------|------|------|-------|
| rung01 | generators (paper examples) | 6/6 | 0 | ✅ complete |
| rung02_arith_gen | arithmetic generators | 5/5 | 0 | ✅ complete |
| rung02_proc | user procedures, params, return | 2/3 | 1 | locals accumulation needs icn_drive |
| rung03 | suspend / user generators | 1/5 | 4 | suspend needs Byrd-box coroutine |
| rung04_string | string concat | 5/5 | 0 | ✅ complete |
| rung05 | string scanning (?) | 2/5 | 3 | &subject returns 0; nested scan wrong |
| rung06 | cset builtins (any/many/upto) | 4/5 | 1 | any_fail: & conjunction wrong |
| rung07 | control flow | 5/5 | 0 | ✅ complete |
| rung08 | string builtins (find, match, move, tab) | 4/5 | 1 | find() as generator needs icn_drive |
| rung09 | loops (repeat/break, until, while) | 5/5 | 0 | ✅ complete |
| rung10 | augmented ops | 4/5 | 1 | break_while needs icn_drive |
| rung11 | augmented concat, ! bang | 2/5 | 3 | !string/!list need icn_drive |

---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

All steps mirror the corresponding `emit_*` function in `emit_x64.c`.

- [x] **S-1** — Add Icon frontend files to Makefile.
- [x] **S-2** — Write `icon_driver.c/h`: `icon_compile()` entry point.
- [x] **S-3** — Wire `.icn` extension in `scrip.c`.
- [x] **S-4** — Implement `icn_exec()` + initial generator support.
- [x] **S-5** — Fix E_RETURN, E_IF, ICN_GLOBAL lowering, scope/slot resolution,
  E_KEYWORD. Gate: rung02_proc 2/3 (locals still failing → S-5B).

- [ ] **S-5B** — Implement `icn_drive(gen, env, nenv, body, out)` — Byrd-box
  generator driver mirroring `emit_every` gbfwd wiring (Prolog model).
  One for-loop per generator type; each iteration = one β re-entry:
  - E_TO: cur=lo..hi loop
  - E_TO_BY: cur=lo..hi..step loop
  - E_ASSIGN/E_AUGOP with embedded E_TO: drive E_TO, re-exec full expr each tick
  Replace `icn_collect` in `E_EVERY` case with `icn_drive`.
  Consult `emit_every` + `emit_to` in `emit_x64.c`.
  Gate: rung02_proc 3/3.

- [ ] **S-6** — `icn_drive` for E_ITERATE (!string/!list) (mirror `emit_bang`).
  !str: β loop advances char position. !list: stub/fail ok.
  Gate: rung11 5/5.

- [ ] **S-7** — `icn_drive` for find() as generator (mirror `emit_find`).
  find(pat,str): β loop scans all match positions.
  Gate: rung08 5/5.

- [ ] **S-8** — Fix &subject / &pos in scan context (rung05).
  Trace &subject from icon_parse.c → icon_lower.c → icn_exec.
  Is it E_KEYWORD or E_VAR("&subject")? Check what node kind the parser emits.
  Gate: rung05 5/5.

- [ ] **S-9** — Fix & conjunction short-circuit in scan (rung06_cset_any_fail).
  any(cs) & expr must not execute expr if any fails.
  Check how & is lowered (E_AND / E_CONJ?); mirror emit_and.
  Gate: rung06 5/5.

- [ ] **S-10** — Fix nested scan subject restore (rung05_scan_nested).
  Inner ? must fully restore outer &subject on exit.
  Gate: rung05 5/5.

- [ ] **S-11** — Implement suspend / user-defined generators (rung03).
  suspend expr = yield expr, resume body on β.
  Use setjmp/longjmp for genuine β re-entry coroutine semantics.
  Mirror emit_suspend(), emit_every() in emit_x64.c.
  Gate: rung03 5/5.

- [ ] **S-12** — Run full rung01–rung11. All pass.
  Gate: 59/59.

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
| `src/frontend/icon/icon_interp.c` | Interpreter — mirror of emit_x64.c |
| `src/backend/emit_x64.c` | Emitter — canonical reference for ALL semantics |
| `src/frontend/prolog/prolog_interp.c` | Model for Byrd-box C translation |
| `src/ir/ir.h` | EKind enum |
| `corpus/programs/icon/rung*` | Test programs |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate: `make scrip` clean + SNOBOL4 PASS=204 unchanged after every commit.
- Mirror `emit_x64.c` one-to-one — consult before implementing any node kind.
- Generator nodes MUST use Byrd-box β re-entry (icn_drive for-loop).
  icn_collect pre-materialisation is WRONG — do not use it for generators.
