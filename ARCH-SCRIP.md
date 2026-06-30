# ARCH-SCRIP.md — SCRIP Frontend + Execution Modes

⛔⛔ **STALE — "THREE EXECUTION MODES" BELOW IS WRONG (flagged 2026-06-30, Claude Sonnet 4.6, against SCRIP
HEAD `8e296381`/`08b68cf3`).** Verified empirically: `grep -rn "sm_interp_run\|sm_jit_run" src/` returns
ZERO hits anywhere in the current tree — neither symbol exists. Only `sm_lower` survives, as a bare
failure-message string in `src/driver/scrip_sm.c` ("scrip: sm_lower failed"), not as the multi-mode
pipeline described below. Verified against `scrip.c`'s actual argv parser: it recognizes exactly **two**
execution-mode flags, `--run` and `--compile` — not the three-mode (2/3/4) table this section describes.
**Current reality:** `scrip --run f` = native x86 BINARY in-process (one mode, not modes 2+3 collapsed into
one flag as the table below half-suggests — the SM-interp/SM-JIT distinction it draws no longer exists at
all). `scrip --compile f` = x86 TEXT asm → `gcc -no-pie` + `libscrip_rt.so`. Both reach the result through
`src/emitter/emit.cpp`'s single driver walking the IR graph at emit time, then freeing it — no SM array, no
per-opcode C dispatch loop, at runtime in either mode. This matches `GOAL-IR-IMMUTABLE-EMIT.md`'s
"ORIENTATION SYNOPSIS" exactly (independently re-verified 2026-06-30, build+smoke+gates+corpus all
reproduced) — treat that synopsis as authoritative over this file for current execution-mode questions.
The "Isolation invariants" and "Former mode-1 entry points" sections further below remain accurate as
*historical* record of what was deleted and why; only the "three modes remain" framing and the `sm_lower`→
`sm_interp_run`/`sm_jit_run` pipeline claim are corrected here.

## Frontend

SCRIP. Produces shared IR (tree_t/STMT_t). See ARCH-IR.md.

## Execution modes (RS-15, updated CLI-3M-9 2026-05-18) — CORRECTED 2026-06-30, see banner above

Mode 1 (AST interpreter) is **deleted**. ~~Three execution modes remain~~ **Exactly TWO execution modes
remain** (the three-mode table below is stale — `sm_interp_run`/`sm_jit_run` do not exist):

| Flag | Purpose | Pipeline (corrected) |
|------|---------|----------|
| `--run` | native x86 binary, in-process | IR → `src/emitter/emit.cpp` (`emit_drive` + dispatch) → BINARY → jump in |
| `--compile` | full native binary path via toolchain | IR → `src/emitter/emit.cpp` → x86 TEXT `.s` → `gcc -no-pie` + `libscrip_rt.so` → exec |

~~Old (stale) table, retained struck through so the correction is traceable, not silently vanished:~~

| # | Mode | Flag | Purpose | Pipeline |
|---|------|------|---------|----------|
| ~~2~~ | ~~SM gen / interp~~ | ~~`--run` (default)~~ | ~~program in SM/BB form, dispatched in C~~ | ~~IR → `sm_lower` → `sm_interp_run`~~ |
| ~~3~~ | ~~SM gen / exec~~ | ~~`--run`~~ | ~~speed without asm/link/process overhead~~ | ~~IR → `sm_lower` → `sm_codegen` → `sm_jit_run`~~ |
| ~~4~~ | ~~SM gen / asm / link / exec~~ | ~~`--compile`~~ | ~~full native binary path~~ | ~~IR → `sm_lower` → asm-emit → link → exec~~ |

**SNOBOL4 native pattern matching (modes 3 & 4)** — the 5-phase `SUBJ ? PAT [= REPL]` model (build subject,
build pattern via builder-BBs-that-build-BBs, run via the generic BB_MATCH box, build replacement, do replace),
plus the INVARIANT-PATTERN-BAKE optimization — is specified in **ARCH-SNOBOL4.md → "Native pattern architecture
— modes 3 & 4 (pattern = built BB graph)"**; step ladder in GOAL-SNOBOL4-BB.md (SBL-PAT-BB). Read it before
mode-3/4 SNOBOL4 pattern work.

## Shared substrate (all three modes)

⛔ **CORRECTED 2026-06-30 (Claude Sonnet 4.6) — several symbols below are dead, several survive under
different file names than stated. Verified by `grep -rln`/`find` against the current tree, not assumed.**

These are the components every mode reaches through:

- `INVOKE_fn` / `APPLY_fn` — builtin dispatch. Symbols confirmed to survive; the file names
  `snobol4_invoke.c`/`snobol4.c` cited here are **NOT FOUND** in the current tree — re-grep for the
  current location rather than trusting these names.
- `NV_GET_fn` / `NV_SET_fn` — name-value table. Confirmed live.
- `exec_stmt` / `bb_build` — pattern engine, confirmed live, in `src/runtime/core/stmt_exec.c` (file survives,
  just not at the bare `stmt_exec.c` root path implied here). `bb_broker` / `bb_boxes` — **DO NOT EXIST**
  (confirmed by `grep -rln`/`find`; this matches `GOAL-ICON-BB.md`'s own "NO C BYRD-BOX FUNCTIONS" FACT RULE,
  which documents `bb_broker.c` and the whole brokered-BB driver as deleted 2026-06-01 — this file simply
  never caught up to that deletion).
- `sm_lower` — confirmed live (`src/driver/scrip_sm.c`, not a standalone `sm_lower.c`). **"IR → SM_sequence_t
  lowering" is the WRONG description** — `SM_sequence_t` does not exist in the current tree.
- `sm_prog` (`src/machine/sm_prog.c`, not `src/emitter/`) — confirmed live. **`SM_sequence_t` itself —
  DOES NOT EXIST** (confirmed: zero `grep` hits anywhere in `src/`); whatever flat-array type `sm_prog.c`
  actually defines now, it isn't this name — re-derive from the file directly rather than trusting this name.
- `eval_node` — confirmed live, but in `src/runtime/runtime_eval.c`, **not** `eval_code.c` (file doesn't exist).
- `coerce.c` — confirmed live at `src/runtime/core/coerce.c` (not bare root `coerce.c`).
- `_usercall_hook` — confirmed live, but `interp_hooks.c` **does not exist** as a file name; re-grep for the
  current location.

## Isolation invariants (RS-15)

⛔ **CORRECTED 2026-06-30 (Claude Sonnet 4.6) — this entire section describes machinery from the dead
3-mode architecture (see the top-of-file banner). Retained below struck through for traceability, not
silently deleted, since the underlying INVARIANT ("no AST/SM/BB walking at runtime in `--run`/`--compile`")
is still real policy — it's restated correctly right after the strikethrough, and is independently
consistent with `GOAL-IR-IMMUTABLE-EMIT.md`'s "NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION" FACT RULE
in `GOAL-ICON-BB.md`, which is current and Icon-verified.**

~~No mode 2/3/4 code path may walk the AST (`tree_t *` / `STMT_t`).~~

~~**No SM/BB walking at runtime in modes 3/4 (RULES.md absolute rule).** Modes 3 (`--run`) and 4
(`--compile`) execute **native x86 only** at runtime. At runtime they may NOT (a) index the SM array
by program counter (`g_jit_prog->instrs[STATE->pc]` opcode-dispatch loop / per-opcode `h_*` C handler)
nor (b) traverse a `BB_t` graph in C (`bb_exec_once` / `bb_exec_resume` / `bb_exec_node` / `bb_broker`).
Mode 4's emitter walks SM/BB **at emit time** (required and permitted) then frees the graph
(`stage2_free_bb_after_emit`); the standalone binary holds no graph. The C SM/BB walkers
(`sm_interp_run`, `bb_exec_*`) belong to **mode 2 (`--run`) ONLY**. The SB-LINEAR endpoint is
`sm_emit_linear` → `sm_run_linear` (enter native blob); the legacy `sm_jit_run` trampoline is itself an
SM-walking loop and is a migration target, not the end state. The single documented temporary exception
is Prolog `--run` → `sm_interp_run` (AGW-1c), to be removed once `bb_pl_*.cpp` templates land.~~ —
**every underlined symbol in the struck paragraph above (`g_jit_prog`, `bb_exec_once`, `bb_exec_resume`,
`bb_exec_node`, `bb_broker`, `sm_interp_run`, `sm_emit_linear`, `sm_run_linear`, `sm_jit_prog`) confirmed
DOES NOT EXIST in the current tree.**

**Corrected, current statement of the same invariant:** Neither `--run` nor `--compile` walks the AST or
IR at runtime. `src/emitter/emit.cpp` walks the IR graph exactly once, at EMIT TIME, to produce either an
in-process BINARY blob (`--run`) or a `.s` text file (`--compile`), then the IR is no longer referenced —
the running program is pure emitted x86, with zero per-opcode C dispatch loop and zero `BB_t`-graph C
traversal at runtime in either mode. (Prolog's `--run` path may still be a documented temporary exception
per its own goal file — not re-verified by this Icon-only correction pass; check `GOAL-PROLOG-BB.md`
directly rather than trusting this file for Prolog specifics.) Runtime
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
