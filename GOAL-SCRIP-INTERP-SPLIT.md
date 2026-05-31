# GOAL-SCRIP-INTERP-SPLIT.md — Extract IR interpreter from scrip.c

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
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
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
**Done when:** `src/driver/scrip.c` contains only the driver (CLI parsing, frontend dispatch,
SM/JIT paths, main). The IR tree-walk interpreter lives in `src/runtime/x86/ir_interp.c`
with public interface in `src/runtime/x86/ir_interp.h`. All gates pass.

---

## Motivation

`scrip.c` is 3450 lines. ~2500 of those are the IR interpreter (SNOBOL4 `interp_eval`,
Icon `icn_interp_eval`, Prolog `pl_execute_program_unified`, plus shared globals:
label table, call stack, user-call hook, define prescan). The driver (CLI, SM-run,
JIT-run, frontend dispatch) is only ~400 lines. Separating them makes both easier
to read, test, and extend.

---

## Key files

| File | Role |
|------|------|
| `src/driver/scrip.c` | Before: 3450 lines. After: ~900 lines (driver only) |
| `src/runtime/x86/ir_interp.c` | NEW — IR interpreter, all three languages |
| `src/runtime/x86/ir_interp.h` | NEW — public entry points + exported globals |

`ir_interp.h` stub already created (GOAL-UNIFIED-BROKER U-11 session).

---

## What moves to ir_interp.c

Approximately scrip.c lines 98–2635 (as of commit 74cef6a5):

- `label_table`, `label_table_build`, `label_lookup`
- `call_stack`, `CallFrame`
- `g_prog`, Icon state globals (`icn_proc_table`, `icn_env`, `icn_gen_stack`, etc.)
- Prolog forward types + globals (`g_pl_pred_table`, `g_pl_trail`, `g_pl_cut_flag`, etc.)
- `icn_drive`, `icn_interp_eval`, `icn_scope_*`, `icn_call_proc`, `icn_execute_program_unified`
- `g_opt_trace`, `g_opt_dump_bb`
- `define_spec_from_expr`, `define_entry_from_expr`, `prescan_defines`
- `interp_eval`, `interp_eval_ref`, `interp_eval_pat`
- All Prolog IR eval helpers: `pl_pred_table_*`, `pl_unified_term_from_expr`,
  `pl_unified_deep_copy`, `pl_unified_eval_arith`, `is_pl_user_call`,
  `interp_exec_pl_builtin`, `pl_execute_program_unified`
- `NAME_DEREF`, `NAME_SET`, `set_and_trace`, `_is_pat_fnc_name`, `_expr_is_pat`
- `data_field_ptr`, `call_user_function`
- `_usercall_hook` (wired into `g_user_call_hook` at startup — stays with interp)

## What stays in scrip.c

- All `#include` directives (or a minimal subset — ir_interp.c gets its own)
- `#include "ir_interp.h"`
- `stmt_init` stub
- `main` and all CLI flag parsing
- SM-run path (`sm_lower`, `sm_interp_run` loop)
- JIT-run path (`sm_codegen`, `sm_jit_run` loop)
- `g_user_call_hook = _usercall_hook` wiring (calls into ir_interp.c)
- Frontend dispatch (sno_parse, icon_driver, prolog_driver, snocone_driver, rebus)

---

## Tricky parts

1. **`_usercall_hook`** — defined in scrip.c, references `call_user_function` (in interp).
   Move it to ir_interp.c. scrip.c wires `g_user_call_hook = _usercall_hook` at startup
   via an `extern` declaration.

2. **`g_sno_err_jmp` / `g_sno_err_active`** — defined in snobol4.c, used by both
   execute_program (interp) and the SM/JIT loops (driver). Both files include snobol4.h —
   no change needed.

3. **`g_pl_trail` / `g_pl_cut_flag`** — currently non-static in scrip.c, referenced by
   pl_broker.c via pl_interp.h. Move definitions to ir_interp.c; pl_interp.h extern
   declarations remain correct.

4. **Makefile** — add `ir_interp.c` to the scrip object list. Pattern is same as other
   `src/runtime/x86/*.c` files already compiled in.

---

## Steps

- [ ] **IS-1** — Create `src/runtime/x86/ir_interp.c`: copy the interp block from scrip.c,
  add all necessary includes (same set scrip.c has, minus driver-only ones like sm_lower.h).
  Make all formerly-static globals that are referenced externally `extern`-declared in ir_interp.h.
  Gate: `make scrip` clean.

- [ ] **IS-2** — Remove the interp block from scrip.c; add `#include "../runtime/x86/ir_interp.h"`.
  Wire `g_user_call_hook = _usercall_hook` via `extern DESCR_t _usercall_hook(...)` declaration.
  Gate: `make scrip` clean; smoke PASS=2 FAIL=0; regression non-regressing.

- [ ] **IS-3** — Update Makefile to compile ir_interp.c as a separate object.
  Gate: `make scrip` clean from scratch (`make clean && make scrip`).

- [ ] **IS-4** — Commit. Update PLAN.md.

---

## Current state

IS-1 not started. `ir_interp.h` stub exists (created GOAL-UNIFIED-BROKER U-11 session, commit 74cef6a5).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```
