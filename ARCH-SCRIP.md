# ARCH-SCRIP.md — SCRIP Frontend + Execution Modes

## Frontend

SCRIP. Produces shared IR (tree_t/STMT_t). See ARCH-IR.md.

## Execution modes (RS-15, updated CLI-3M-9 2026-05-18)

Mode 1 (AST interpreter) is **deleted**. Three execution modes remain:

| # | Mode | Flag | Purpose | Pipeline |
|---|------|------|---------|----------|
| 2 | SM gen / interp | `--run` (default) | program in SM/BB form, dispatched in C | IR → `sm_lower` → `sm_interp_run` |
| 3 | SM gen / exec | `--run` | speed without asm/link/process overhead | IR → `sm_lower` → `sm_codegen` → `sm_jit_run` |
| 4 | SM gen / asm / link / exec | `--compile` | full native binary path | IR → `sm_lower` → asm-emit → link → exec |

**SNOBOL4 native pattern matching (modes 3 & 4)** — the 5-phase `SUBJ ? PAT [= REPL]` model (build subject,
build pattern via builder-BBs-that-build-BBs, run via the generic BB_MATCH box, build replacement, do replace),
plus the INVARIANT-PATTERN-BAKE optimization — is specified in **ARCH-SNOBOL4.md → "Native pattern architecture
— modes 3 & 4 (pattern = built BB graph)"**; step ladder in GOAL-SNOBOL4-BB.md (SBL-PAT-BB). Read it before
mode-3/4 SNOBOL4 pattern work.

## Shared substrate (all three modes)

These are the components every mode reaches through:

- `INVOKE_fn` / `APPLY_fn` (`snobol4_invoke.c`, `snobol4.c`) — builtin dispatch
- `NV_GET_fn` / `NV_SET_fn` — name-value table
- `exec_stmt` / `bb_build` / `bb_broker` / `bb_boxes` (`stmt_exec.c`, `bb_*.c`) — pattern engine
- `sm_lower` (`sm_lower.c`) — IR → SM_sequence_t lowering
- `sm_prog` / `SM_sequence_t` (`sm_prog.c`) — flat instruction array
- `eval_node` (`eval_code.c`) — value-context expression evaluator
- `coerce.c` — DESCR_t coercion helpers
- `_usercall_hook` (`interp_hooks.c`) — single user-function dispatch hook for all modes

## Isolation invariants (RS-15)

No mode 2/3/4 code path may walk the AST (`tree_t *` / `STMT_t`).

**No SM/BB walking at runtime in modes 3/4 (RULES.md absolute rule).** Modes 3 (`--run`) and 4
(`--compile`) execute **native x86 only** at runtime. At runtime they may NOT (a) index the SM array
by program counter (`g_jit_prog->instrs[STATE->pc]` opcode-dispatch loop / per-opcode `h_*` C handler)
nor (b) traverse a `BB_t` graph in C (`bb_exec_once` / `bb_exec_resume` / `bb_exec_node` / `bb_broker`).
Mode 4's emitter walks SM/BB **at emit time** (required and permitted) then frees the graph
(`stage2_free_bb_after_emit`); the standalone binary holds no graph. The C SM/BB walkers
(`sm_interp_run`, `bb_exec_*`) belong to **mode 2 (`--run`) ONLY**. The SB-LINEAR endpoint is
`sm_emit_linear` → `sm_run_linear` (enter native blob); the legacy `sm_jit_run` trampoline is itself an
SM-walking loop and is a migration target, not the end state. The single documented temporary exception
is Prolog `--run` → `sm_interp_run` (AGW-1c), to be removed once `bb_pl_*.cpp` templates land. Runtime
stub sites in modes 3/4 print `[NO-SM-BB] <opcode>` and set `last_ok=0`.

**Former mode-1 entry points — all deleted (CLI-3M-9, 2026-05-18):**

| Symbol | Former file | Status |
|--------|-------------|--------|
| `execute_program` | `interp_exec.c` | file deleted |
| `interp_eval` | `interp_eval.c` | function deleted; file deleted |
| `interp_eval_ref` | `interp_ref.c` | call sites stubbed to FAILDESCR |
| `call_user_function` | `interp_call.c` | call sites stubbed to FAILDESCR |

**Live runtime (moved from interp_eval.c to proper homes):**

| What | Now lives in |
|------|-------------|
| `icn_try_call_builtin_by_name`, `kw_assign`, `icn_kw_*`, `real_str`, g_icn_* globals | `src/runtime/interp/icn_runtime.c` |
| `rs24_diag_*`, `set_and_trace` | `src/driver/interp_globals.c` |
| `PAT_FNC_NAMES`, `_is_pat_fnc_name`, `_expr_is_pat` | `src/driver/interp_hooks.c` |
| `data_field_ptr` | `src/driver/interp_data.c` |

**Invariant:** `g_current_sm_prog` is always non-NULL in modes 2/3/4 (set by `sm_preamble()`). Any shared-path function that historically branched on IR vs SM must consult this.

**State markers:**

- `g_current_sm_prog` — set by `sm_preamble()` to the live `SM_sequence_t *`.
- `label_table_clear_stmts()` — called by `sm_preamble()` after `code_free()`.

## Mode-specific notes

**Mode 2 (SM gen / interp):** `sm_preamble()` followed by `sm_run_with_recovery(sm, sm_interp_run)`. `SM_CALL` dispatches user functions via SM call frames; pattern-context `*func()` reaches `_usercall_hook` which dispatches via nested `sm_interp_run`.

**Mode 3 (SM gen / exec):** `sm_preamble()` followed by `sm_codegen(sm)` followed by `sm_run_with_recovery(sm, sm_jit_run)`.

**Mode 4 (SM gen / emit):** `sm_preamble()` followed by emit through `src/emitter/*.c` templates with `bb_emit_mode = EMIT_TEXT` — produces GAS assembly text. Same SM_sequence_t, same template bodies as mode 3.

## Driver helpers (RS-14)

Two helpers in `src/driver/scrip_sm.{c,h}`:

- `sm_preamble(prog) -> SM_sequence_t *` — `label_table_build` + `prescan_defines` + `g_sno_err_active = 1` + `sm_lower` + `g_current_sm_prog = sm` + `code_free` + `label_table_clear_stmts`. Returns NULL on failure.
- `sm_run_with_recovery(sm, runner)` — initialises `SM_State`, drives a `setjmp(g_sno_err_jmp)` loop calling `runner(sm, &st)` until normal halt or fatal error. Used by both `--run` and `--run`.
