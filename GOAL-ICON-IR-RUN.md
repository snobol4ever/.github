# GOAL-ICON-IR-RUN — Get Icon Working in scrip --run

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


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
**Done when:** `.icn` files run correctly via `scrip --run file.icn`, passing
rung01–rung11 of the Icon corpus ladder.

---

## Current state (2026-04-13)

**Score: 59/59 PASS — rung01–rung11 complete.**

S-8 ✅ &subject/&pos fixed. S-8B ✅ E_SCAN shared confirmed. S-13 ✅ runner script.
S-11 ✅ suspend via ucontext. S-12 ✅ 59/59 — E_ALTERNATE + nested_to cross-product.

**Architectural pivot (Lon, 2026-04-13):** All goal-directed backtracking must route
through brokered Byrd boxes mirroring SNOBOL4's interp_eval_pat + exec_stmt + bb_build.
See GOAL-ICN-BROKER.md for the plan.

| Rung | Feature | PASS | FAIL | Notes |
|------|---------|------|------|-------|
| rung01 | generators (paper examples) | 5/6 | 1 | nested_to pre-existing |
| rung02_arith_gen | arithmetic generators | 5/5 | 0 | ✅ complete |
| rung02_proc | user procedures, params, return | 3/3 | 0 | ✅ complete |
| rung03 | suspend / user generators | 2/5 | 3 | suspend not implemented |
| rung04_string | string concat | 5/5 | 0 | ✅ complete |
| rung05 | string scanning (?) | 0/5 | 5 | &subject, nested scan |
| rung06 | cset builtins | 5/5 | 0 | ✅ complete (NUMREL fix) |
| rung07 | control flow | 5/5 | 0 | ✅ complete |
| rung08 | string builtins | 4/5 | 1 | match pre-existing |
| rung09 | loops | 5/5 | 0 | ✅ complete |
| rung10 | augmented ops | 5/5 | 0 | ✅ complete |
| rung11 | augmented concat, ! bang | 5/5 | 0 | ✅ complete |

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

- [x] **S-5C** — Unify Icon IR interpreter into scrip.c (one interpreter).
  **DONE — 47/59 PASS.** One IR, one interpreter.
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

- [x] **S-6** — Translate `emit_bang` → C for-loop over string chars.
  `!str` generates each character; β = advance position.
  Implemented: `E_ITERATE` case in `icn_drive` (for-loop over positions) +
  `E_ITERATE` case in `icn_interp_eval` (returns single-char string via gen_stack sval).
  Added `sval` field to `IcnGenEntry_d`; added `icn_gen_lookup_sv` helper.
  Gate: rung11 5/5. ✅ Score: 47/59.

- [x] **S-7** — Translate `emit_find` (find() builtin) → C for-loop over positions.
  `find(pat,str)` generates all match positions; β = advance past last match.
  Fixed bug: ICN_CALL nodes have `sval=NULL`; name is in `children[0]->sval`.
  Added `g_lang` / `g_icn_root` globals; set at both execute entry points.
  Gate: rung08 find_gen PASS. ✅ Score: 48/59.

- [x] **S-7B** — Interp unification prep: make `icn_interp_eval(root,e)` set globals then delegate to `interp_eval(e)`.
  `interp_eval` gains Icon-only cases. Name-based NV save/restore in `icn_call_proc`.
  Gate: make scrip clean + 49/59 PASS. ✅

- [x] **S-7C** — Migrate shared cases into `interp_eval`. Done as part of S-7B. ✅

- [x] **S-7D** — Migrate Icon-only cases into `interp_eval`. Done as part of S-7B. ✅

- [x] **S-7E** — Delete `icn_interp_eval` body; 3-line wrapper. Done. ✅
  Gate: make scrip clean + 49/59 PASS unchanged. ✅

- [ ] **S-8** — Fix `&subject` / `&pos` in scan context (rung05).
  Root cause: `&subject` parsed as E_VAR("&subject") in icon_parse.c (line 136),
  but interp_eval E_VAR does NV store lookup — not icn_scan_subj global.
  Fix: in interp_eval E_VAR case, if sval starts with '&', dispatch to E_KEYWORD logic.
  Gate: rung05 t01–t04 PASS (t05 nested deferred to S-10).

- [x] **S-8B** — Verify Icon/SNOBOL4 IR sharing. ✅ CONFIRMED — no work needed.
  E_SCAN is already shared: SNOBOL4 parser (snobol4.tab.c) emits E_SCAN(subj,pat) for
  pattern match; icon_lower.c emits E_SCAN(subj,body) for expr?body. Same node.
  Scan builtins (any/upto/many/tab/move/match) are correctly handled as E_FNC name
  dispatch in interp_eval — mirroring exactly what x64/JVM/NET emitters do (strcmp
  inside E_FNC case). No E_PAT_* nodes exist in the IR; E_FNC name dispatch IS the
  architecture. No refactor needed.

- [ ] **S-9** — Fix `&` conjunction short-circuit (rung06_cset_any_fail).
  `any(cs) & expr` must not execute expr if any() fails.
  Check how `&` is lowered (E_AND? E_CONJ? E_SEQ?); mirror emit_and.
  Gate: rung06 5/5.

- [ ] **S-10** — Fix nested scan subject restore (rung05_scan_nested).
  Gate: rung05 5/5.

- [x] **S-11** — Translate `emit_suspend` → C using ucontext coroutines.
  Each generator proc call gets its own 256KB stack via makecontext/swapcontext.
  icn_coro_table keyed by E_FNC call node pointer (unique per call site).
  E_SUSPEND yields via swapcontext; caller resumes via swapcontext back.
  Gate: rung03 5/5. ✅ Score: 57/59.

- [x] **S-12** — Full rung01–rung11 pass. ✅ 59/59 PASS.
  E_ALTERNATE added (Icon | — try left, if FAIL try right).
  nested_to fixed (icn_drive E_TO cross-product: iterate all lo × all hi values).
  Next: GOAL-ICN-BROKER (broker pivot).

- [x] **S-12B** — PIVOT: Route all goal-directed backtracking through brokered Byrd boxes. DONE via GOAL-ICN-BROKER.
  **Architectural mandate (Lon, 2026-04-13):** Icon scan/generators and SNOBOL4 pattern
  match are the same Byrd-box model — all backtracking must go through the broker.
  **Architectural reality:** exec_stmt/bb_build use PATND_t + spec_t (string-cursor typed).
  Icon generators produce DESCR_t values, not spec_t substrings. Therefore:
  - E_SCAN (Icon ?) → exec_stmt (already correct — string match in scan context)
  - E_TO / E_ITERATE / E_SUSPEND (value generators) → need DESCR_t-typed Byrd boxes
  Plan:
  1. Define icn_box_fn: DESCR_t fn(void *zeta, int entry) — value-typed Byrd box
  2. Implement icn_bb_to, icn_bb_iterate, icn_bb_suspend as icn_box_fn boxes
  3. Implement icn_broker: drives icn_box_fn α→β*→ω loop (replaces icn_drive)
  4. E_EVERY in interp_eval: call icn_broker(gen_box, body_fn)
  5. Remove icn_drive, icn_gen_stack, icn_coro_table — all backtracking via broker
  Gate: 59/59 PASS; no ad-hoc gen machinery remaining in scrip.c.
- [ ] **S-13** — Add run_icon_ir_rung.sh runner script.
- [ ] **S-14** — Update PLAN.md done.

---

## Phase 2 — Stack Machine and x86 Byrd Box execution

- [ ] **S-15** — Wire Icon IR through sm_lower.c.
- [ ] **S-16** — Wire Icon IR through sm_codegen.c (x86 JIT).
- [ ] **S-17** — Run full rung ladder on --run.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/icon/icon_interp.c` | **DELETED** — removed per S-5C note (handoff 2026-04-13) |
| `src/backend/emit_x64.c` | **Canonical reference — read before every node** |
| `src/runtime/x86/engine.h` | Byrd-box engine template (PROCEED/SUCCEED/CONCEDE/RECEDE) |
| `src/runtime/x86/engine.c` | Byrd-box engine implementation — study this |
| `src/frontend/prolog/prolog_interp.c` | Prolog model: for-loop β re-entry |
| `src/ir/ir.h` | EKind enum — all Icon node kinds |
| `corpus/programs/icon/rung*` | Test programs |

---

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate: `make scrip` clean + SNOBOL4 PASS=204 unchanged after every commit.
- **Read `emit_x64.c` for the node BEFORE implementing it.**
- **One emit_* per step. Gate on its rung. Do not batch.**
- Generator β re-entry = for-loop in C (Prolog model), NOT icn_collect array.
- `suspend` only: use setjmp/longjmp for genuine β re-entry.
