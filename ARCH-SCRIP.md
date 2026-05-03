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

**Exception — Icon and Prolog generators:** `coro_runtime.c` and `pl_runtime.c` legitimately call `interp_eval` and `interp_eval_pat` to evaluate value-context subexpressions during Byrd-box drive. The Icon and Prolog frontends do not have SM lowerings of their own — `sm_lower` emits `SM_BB_PUMP` / `SM_BB_ONCE` opcodes that pass the raw `EXPR_t*` to `coro_eval`, which builds a drivable box that recursively evaluates IR subtrees. Modes 2, 3, 4 reach `interp_eval` only through this Icon/Prolog path, never for SNOBOL4 statement bodies. This is by design: the drive-loop semantics of Icon's `every` / `while` and Prolog's choice points are most naturally expressed by walking the IR tree, and the value subexpressions inside those drive loops are pure (no SM-frame-related state).

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
