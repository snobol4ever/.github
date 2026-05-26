# GOAL-CLI-3MODE — Collapse 4 modes to 3, delete AST-interp

**Status:** ✅ COMPLETE 2026-05-18.

## End state

Three execution modes, one orthogonal BB strategy axis (under `--interp` only):

| Flag | Meaning | BB strategy |
|------|---------|-------------|
| `--interp` | SM emulator (interprets `SM_Program`) | `--bb=brokered` (default) or `--bb=wired` |
| `--run` | SM/BB emit to memory, execute in-process (JIT) | wired only (forced) |
| `--compile` | SM/BB emit asm → assemble+link → separate process | wired only (forced) |

Mode 1 (AST-interp, `--ast-run`/`----interp`) and all deprecated aliases deleted. `interp_eval.c` / `interp_exec.c` / `interp_call.c` gone; live runtime moved to `icn_runtime.c`, `interp_globals.c`, `interp_hooks.c`, `interp_data.c`. One name per concept across the codebase.

## Closed step trail (git log is authority)

CLI-3M-1..12 — alias-add → script sweep → BB-strategy gates → deprecation warnings → audit/triage → monitor demoted to 2-way → AST-interp flag deletion → `interp_*.c` rip → alias deletion + variable renames → docs sweep → AR-3 reframe.

Key commits: `a6efc60d` (canonical flags), `c91de33c` (script sweep A), `00dc6cd7` (BB gate), `b65882ea` (alias removal sweep, 104 files), `730da38e` (argv-parser rewrite), `188475d7` / `9aeede7d` / `8c799b2e` (mode-1 file deletion).

## Unblocked downstream

- `tree_t`→`PARSE_t` rename (AR-3) — `tree_t` no longer an execution vehicle.
- PST-REBUS Bug #2 framing — moot; the `interp_exec.c` SUBJ-PAT split sketched against a file that no longer exists.

## Authorship

Goal file + steps CLI-3M-1..12 authored by Claude Opus 4.7 and Claude Sonnet (sessions 2026-05-17 through 2026-05-18).
