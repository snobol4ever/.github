# GOAL-ICON-IR-RUN — Get Icon Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.icn` files run correctly via `scrip --ir-run file.icn`, passing
rung01–rung11 of the Icon corpus ladder.

---

## Current state (2026-04-12, one4all a34ef96d)

S-1 through S-4 complete. `icon_interp.c` (289 lines) mirrors `emit_x64.c` one-to-one.

**Baseline: 17/42 tests PASS across rungs 01–11**

| Rung | Feature | PASS | FAIL | Notes |
|------|---------|------|------|-------|
| rung01 | generators (paper examples) | 6/6 | 0 | ✅ complete |
| rung02_arith_gen | arithmetic generators | 5/5 | 0 | ✅ complete |
| rung02_proc | user procedures, params, return | 0/3 | 3 | return value wrong |
| rung03 | suspend / user generators | 0/5 | 5 | suspend not implemented |
| rung04_string | string concat | 4/5 | 1 | `||` augmented concat chain |
| rung05 | string scanning (`?`) | 1/5 | 4 | scan operator not wired |
| rung06 | cset builtins (any/many/upto) | 1/5 | 4 | scan-context builtins missing |
| rung07 | control flow (not, repeat/break, seq, `==`) | 2/5 | 3 | string eq, break, seq missing |
| rung08 | string builtins (find, match, move, tab) | 0/5 | 5 | scan-context builtins missing |
| rung09 | loops (repeat/break, until, while) | 0/5 | 5 | repeat/break/until missing |
| rung10 | augmented ops (`:=+`, `:=*` etc.) | 0/5 | 5 | aug-assign not wired |
| rung11 | `||=` augmented concat, `!` bang | 0/5 | 5 | aug-concat, bang missing |

---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

All steps mirror the corresponding `emit_*` function in `emit_x64.c`.

- [x] **S-1** — Add Icon frontend files to Makefile.
  Gate: `make scrip` clean.

- [x] **S-2** — Write `icon_driver.c/h`: `icon_compile()` wraps `EXPR_t**` → `Program*`.
  Gate: `icon_compile()` returns non-NULL.

- [x] **S-3** — Wire `.icn` extension in `scrip.c`, route to `icon_execute_program()`.
  Gate: `hello.icn` produces `Hello, World!`.

- [x] **S-4** — Implement `icn_exec()` + `icn_collect()` generator cross-product.
  Gate: rung01 6/6, rung02_arith_gen 5/5.

- [ ] **S-5** — Fix user procedure `return` value (rung02_proc).
  `return expr` in Icon sets the procedure result. Currently returning 0 instead of
  the expression value. Check `E_RETURN` handling in `icn_exec()` vs emitter.
  Gate: rung02_proc 3/3.

- [ ] **S-6** — Implement augmented assignment operators (rung10, rung11 partial).
  `x +:= 5` = `x := x + 5`. Check `E_AUGOP` / `E_AUG*` node kinds in `ir.h`.
  Mirror `emit_augop()` in `emit_x64.c`.
  Gate: rung10 5/5.

- [ ] **S-7** — Implement `repeat`/`break`/`until` loops (rung09).
  `repeat body` loops until `break`. `until cond do body` = while not cond.
  Check `E_REPEAT`, `E_BREAK`, `E_UNTIL` in `ir.h`. Mirror `emit_repeat()` etc.
  Gate: rung09 5/5.

- [ ] **S-8** — Implement string equality `==` / `~==` and `not` (rung07).
  String comparisons are `E_SEQ`, `E_SNE`, `E_SLT` etc. — distinct from `E_EQ`.
  `not E` = `E_NOT`. Mirror `emit_strrelop()`, `emit_not()`.
  Gate: rung07 5/5.

- [ ] **S-9** — Implement augmented concat `||=` and bang `!list` (rung11).
  `s ||:= t` appends. `!list` generates list elements.
  Check `E_AUGCAT`, `E_BANG` in `ir.h`. Mirror `emit_augcat()`, `emit_bang()`.
  Gate: rung11 5/5.

- [ ] **S-10** — Implement string scanning operator `?` (rung05, rung06, rung08).
  `s ? expr` sets scan subject/position. Builtins `any(cs)`, `many(cs)`, `upto(cs)`,
  `find(s1,s2)`, `match(s1,s2)`, `move(n)`, `tab(n)` operate on scan position.
  Mirror `emit_scan()`, `icn_any()`, `icn_many()`, `icn_upto()`, `icn_match()` etc.
  Gate: rung05 5/5, rung06 5/5, rung08 5/5.

- [ ] **S-11** — Implement `suspend` / user-defined generators (rung03).
  `suspend expr do body` yields expr then executes body on resume.
  Requires coroutine-style resumption — most complex step.
  Approach: collect all suspend values via recursive `icn_collect()` extension,
  or use `setjmp/longjmp` for genuine coroutine semantics.
  Mirror `emit_suspend()`, `emit_every()` generator composition.
  Gate: rung03 5/5.

- [ ] **S-12** — Fix rung04 concat chain and any remaining rung04/rung07 failures.
  Gate: rung04 5/5, rung07 5/5.

- [ ] **S-13** — Run full rung01–rung11. All pass.
  Gate: 42/42.

- [ ] **S-14** — Add `test/frontend/icon/run_icon_ir_rung.sh` runner script.
  Wraps `scrip --ir-run` as the binary for the existing rung runner scripts.
  Gate: script runs clean.

- [ ] **S-15** — Update PLAN.md ☑ done.

---

## Phase 2 — Stack Machine and x86 Byrd Box execution

Once `--ir-run` passes the full rung ladder, Icon graduates to:

- [ ] **S-16** — Wire Icon IR through `sm_lower.c`:
  Add cases for `E_TO`, `E_TO_BY`, `E_EVERY`, `E_SUSPEND`, `E_WHILE` etc.
  Gate: `./scrip --sm-run hello.icn` produces `Hello, World!`.

- [ ] **S-17** — Wire Icon IR through `sm_codegen.c` (x86 JIT).
  Gate: `./scrip --jit-run hello.icn` produces `Hello, World!`.

- [ ] **S-18** — Run full rung ladder on `--jit-run`. Fix failures.
  Gate: PASS matches `--ir-run` baseline.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/icon/icon_interp.c` | Interpreter — mirror of `emit_x64.c` |
| `src/frontend/icon/icon_driver.c` | `icon_compile()` entry point |
| `src/backend/emit_x64.c` | Emitter — canonical reference for all semantics |
| `src/ir/ir.h` | EKind enum — all Icon-specific node kinds |
| `corpus/programs/icon/rung*` | Test programs |
| `test/frontend/icon/run_rung*.sh` | Rung runners |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate: `make scrip` clean + SNOBOL4 PASS=204 unchanged after every commit.
- Mirror `emit_x64.c` one-to-one — consult it before implementing any node kind.
