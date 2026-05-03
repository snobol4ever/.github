# ARCH-SCRIP.md — SCRIP Frontend + Execution Modes

## Frontend

SCRIP. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## Execution modes (RS-15)

A SCRIP program (or any frontend producing IR) runs through one of four
execution modes. Every mode shares the same IR input and the same runtime
substrate. They differ in how they walk and dispatch the program.

| # | Mode | Flag | Purpose | Pipeline |
|---|------|------|---------|----------|
| 1 | IR interp | `--ir-run` | correctness reference; in-memory tree walk | IR → `execute_program` |
| 2 | SM gen / interp | `--sm-run` (default) | program in final SM/BB form, dispatched in C | IR → `sm_lower` → `sm_interp_run` |
| 3 | SM gen / exec | `--jit-run` | speed without asm/link/process overhead | IR → `sm_lower` → `sm_codegen` → `sm_jit_run` |
| 4 | SM gen / asm / link / exec | future | full native binary path | IR → `sm_lower` → asm-emit → link → exec |

## Shared substrate (all four modes)

These are the components every mode reaches through:

- `INVOKE_fn` / `APPLY_fn` (`snobol4_invoke.c`, `snobol4.c`) — builtin dispatch
- `NV_GET_fn` / `NV_SET_fn` — name-value table
- `exec_stmt` / `bb_build` / `bb_broker` / `bb_boxes` (`stmt_exec.c`, `bb_*.c`) — pattern engine
- `coro_eval` / `coro_call` / `coro_drive` (`coro_runtime.c`) — generator/coroutine substrate (Icon, Prolog, Raku)
- `sm_lower` (`sm_lower.c`) — IR → SM_Program lowering. Modes 2, 3, 4.
- `sm_prog` / `SM_Program` (`sm_prog.c`) — flat instruction array. Modes 2, 3, 4.
- `eval_node` (`eval_code.c`) — value-context expression evaluator. Modes 1, 2, 3 via various paths.
- `coerce.c` — DESCR_t coercion helpers
- `_usercall_hook` (`interp_hooks.c`) — single user-function dispatch hook for all modes; internal guards select per-mode behaviour

## Isolation invariants (RS-15)

The IR-only entry points must never be called from SM-mode code paths.

**IR-only entry points:**

| Symbol | File | Role |
|--------|------|------|
| `execute_program` | `interp_exec.c` | mode-1 main dispatch loop |
| `interp_eval` | `interp_eval.c` | recursive IR tree-walk evaluator |
| `interp_eval_pat` | `interp_pat.c` | pattern-context tree-walk evaluator |
| `interp_eval_ref` | `interp_ref.c` | lvalue (DESCR_t*) evaluator |
| `call_user_function` | `interp_call.c` | mode-1 user-function dispatcher |
| `label_lookup` (when stmt fields are live) | `interp_label.c` | IR statement-pointer table |

**Invariant:** Modes 2, 3, 4 must not call any of the above for SNOBOL4-frontend code paths. Where a function is structurally callable from a shared path (e.g. `_usercall_hook`, `_eval_str_impl_fn`), an internal guard on `g_current_sm_prog` MUST short-circuit before reaching the IR-only path.

**Icon and Prolog generators (RS-17 / RS-18 / RS-19, closed 2026-05-03):** `coro_runtime.c` and `pl_runtime.c` are now full members of the isolation gate. Icon Byrd-box drive routes value-context subexpressions through `bb_eval_value` (`coro_value.c`, RS-17a, 60 sites) and statement-context bodies through `bb_exec_stmt` (`coro_stmt.c`, RS-17b, 13 sites). Prolog user-predicate clause-body invocation routes through `bb_eval_value` (RS-18, 3 sites). Neither file references `interp_eval` or `interp_eval_pat` any more. The `bb_eval_value` and `bb_exec_stmt` adapter files retain a documented `interp_eval` fallthrough as their migration scaffold, and are therefore intentionally not yet in the isolation gate themselves; sub-rungs RS-17a-cont / RS-17b-cont absorb specific kinds into their dispatch and (when the fallthrough becomes unreachable) those files can be promoted too.

**RS-20 (decision recorded 2026-05-03):** BB stays everywhere it makes sense; SM is the **carrier** for the four-mode pipeline rather than necessarily the **executor**. Icon and Prolog programs may lower thinly into SM (often a single `SM_BB_PUMP`/`SM_BB_ONCE` instruction that hands the whole program to the BB engine); SNOBOL4 lowers richly into many SM opcodes. Both are valid SM_Programs. The hard requirement is that no mode 2/3/4 path may walk the IR — the BB adapters' remaining `interp_eval` fallthrough is the last violation and is closed by RS-21/22/23. We do not invent SM_GEN_SUSPEND/SM_CHOICE_PUSH opcodes to flatten Icon/Prolog into SNOBOL4-shaped streams; their semantics live in BB and stay there.

**State markers:**

- `g_current_sm_prog` — set by `sm_preamble()` to the live `SM_Program*`. NULL in mode 1. Any shared-path function that branches on IR vs SM must consult this.
- `label_table_clear_stmts()` — called by `sm_preamble()` after `code_free()`. Defence in depth: if any IR-only path is reached anyway, `label_lookup` returns NULL rather than dereferencing freed `STMT_t`.

## Mode-specific notes

**Mode 1 (IR interp):** never sets `g_current_sm_prog`. Calls `execute_program` which walks `STMT_t` chains and uses `interp_eval` recursively. Free to call any IR symbol.

**Mode 2 (SM gen / interp):** `sm_preamble()` followed by `sm_run_with_recovery(sm, sm_interp_run)`. `SM_CALL` dispatches user functions via SM call frames; pattern-context `*func()` reaches `_usercall_hook` which dispatches via nested `sm_interp_run` (RS-11).

**Mode 3 (SM gen / exec):** `sm_preamble()` followed by `sm_codegen(sm)` followed by `sm_run_with_recovery(sm, sm_jit_run)`. Handlers in `sm_codegen.c` mirror `sm_interp.c` semantics — including `kw_rtntype` writes on return (RS-11).

**Mode 4 (future):** Will share `sm_preamble()`. Will replace `sm_codegen` + `sm_jit_run` with an asm-emitter + linker + child-process exec. The same isolation invariants apply.

## Driver helpers (RS-14)

Two helpers in `src/driver/scrip_sm.{c,h}`:

- `sm_preamble(prog) -> SM_Program*` — `label_table_build` + `prescan_defines` + `g_sno_err_active = 1` + `sm_lower` + `g_current_sm_prog = sm` + `code_free` + `label_table_clear_stmts`. Returns NULL on failure.
- `sm_run_with_recovery(sm, runner)` — initialises `SM_State`, drives a `setjmp(g_sno_err_jmp)` loop calling `runner(sm, &st)` until normal halt or fatal error. Used by both `--sm-run` and `--jit-run`.

Mode 4 will use both helpers verbatim — only the runner-equivalent step changes.
