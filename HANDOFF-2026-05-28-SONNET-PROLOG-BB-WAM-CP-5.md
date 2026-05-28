# HANDOFF 2026-05-28 — Sonnet 4.6 — PROLOG-BB: WAM-CP-5 COMPLETE

**Goal:** GOAL-PROLOG-BB.md — WAM-CP-5 (mode-4 CP record for BB_CHOICE + BB_PL_CALL).

## State at handoff
- HEAD `b1e27f56`, tree clean, pushed.
- GATE-1 5/5 · GATE-2 132/0 (5 ORACLE_MISS) · GATE-3 mode-2 91/107 · GATE-4 4/4 · FACT RULE 0
- Sibling smokes: icon 5/5 · snocone 5/5 · raku 5/5 · snobol4 13/13
- Full mode-4 corpus (with .expected): **40/107** (+7 vs session-start baseline of 33)

## What landed this session (3 commits)

### `414d5da3` — WAM-CP-5: BB_CHOICE + BB_PL_CALL migrate rsp-frame cursor to heap pl_choice
- **BB_CHOICE** (`bb_pl_choice.cpp`): replaced 16-byte rsp stack frame with `pl_cp_push` heap record.
  Cursor in `cp->cursor` (offset 48); trail mark in `cp->trail_mark` (offset 16); callee_env in `cp->env` (offset 24).
  `exit_γ` just `jmp γ` — no `add rsp,16`. CP stays live across γ→β cycle. Exhausted pops CP.
- **BB_PL_CALL** (`bb_pl_call.cpp`): no own CP. Delegates to callee CHOICE's CP.
  On α success: `pl_bb_env_install(caller_env)` + `rt_pl_cp_save_caller_env()` stores caller_env into `g_pl_bfr->saved_args` (offset 40).
  β: `pl_cp_current()->env` = callee_env (reinstall), call `_redo` **NO pre-unwind** (CHOICE `pre[i]` handles trail within its own mark — arg-alias bindings from `pl_bb_bind_arg` survive). On redo success: restore caller_env from `cp->saved_args`.
- **rt.c/rt.h**: `rt_pl_cp_save_caller_env(void*)` — stores caller_env into `g_pl_bfr->saved_args`.
- New passes: rung02_facts (brown/jones/smith), +2 others.

### `60dea34f` — WAM-CP-5b: BB_PL_CALL compound args via emit_build_compound_term
- `bb_pl_call.cpp`: `build_arg()` helper dispatches `BB_PL_STRUCT` nodes to `emit_build_compound_term` (extern decl, already in `bb_builtin.cpp`). Leaf args unchanged.
- Fixes rung05_backtrack (member/2 with `[a,b,c]`), rung06_lists.
- New passes: rung05, rung06, +3 others.

### `b1e27f56` — rt_pl_arith: bitwise, shift, max/min, mod/rem, power
- `rt_pl_arith`: added `/\` AND, `\/` OR, `xor`, `>>`, `<<`, `max`, `min`, `mod`, `rem`, `**`, `^`.
- Fixes rung23_bitwise, rung23_max_min.

## Key design decisions (for next session)

**Trail discipline:** BB_CALL β does NOT pre-unwind. CHOICE's `pre[i>0]` unwinds to its own trail mark (taken INSIDE the callee, AFTER `pl_bb_bind_arg` arg-alias bindings). This is correct: arg aliases survive across redo, and new clause bindings propagate back through the alias chains. Mirror of mode-2 `BB_PL_CALL` β comment: "Do NOT pre-unwind the trail here."

**CP stack discipline:** `g_pl_bfr` is guaranteed to be CHOICE's CP at BB_CALL's β time because CHOICE leaves it live on success and pops it only on exhaustion. Nested calls push their own CPs and pop them before returning — so the stack is disciplined.

**`saved_args` reuse:** `pl_choice.saved_args` (offset 40) is repurposed as `caller_env` store for BB_PL_CALL. WAM-CP-11 (deep-backtracking arg restore) will need this field for its own purpose — when WAM-CP-11 lands, BB_PL_CALL should get a dedicated field or a separate mechanism.

## Open bugs / next steps

### rung23_arith_ext_power (`**` prefix clash)
`rt_pl_arith` checks `op[0]=='*'` for multiply BEFORE checking `strcmp(op,"**")` — so `**` fires the multiply branch, giving `5*10=50` instead of `5**10=9765625`. Fix: reorder so `strcmp(op,"**")` is checked before the single-char `*` check.

### Unary sign/truncate/integer/float (different BB path)
`sign(-5)`, `truncate(7.2)`, `integer(4)` go through a different BB node (NOT BB_ARITH with two operands). They appear to go through `rt_arith` (SNOBOL4 helper) in the emitted asm — indicating the Prolog IS expression lowerer routes them to a non-Prolog arith path. Needs investigation. These produce `_` in mode-4.

### rung07_cut_cut (WAM-CP-9)
Still fails mode-4 — cut semantics need WAM-CP-9 (committed-ITE node + cut-truncate).

### Findall mode-4 (rung11, 5 rungs)
`BB_BUILTIN findall` hits the unknown stub. The `nd->ival` holds a `bb_pl_findall_state_t*` (not an arity integer), so the dispatcher can't find it. Needs a dedicated template path that runs the goal sub-graph via `sm_interp_run` or emits it inline.

### rung14/15 (retract/abolish), rung19 (format), rung20 (numbervars), rung21 (char_type), rung22 (write_canonical), rung24-26 (string/concat) — all mode-4 emit gaps for already-mode-2-correct builtins.

## Next recommended steps (in priority order)
1. Fix `**` prefix clash in `rt_pl_arith` (trivial — reorder checks).
2. Investigate unary arith path (sign/truncate) — find which BB node type they emit.
3. WAM-CP-6 (LCO) — principled fix for deep recursion stack growth.
4. CAT-D mode-4 emit for format/numbervars/char_type/write_canonical (each ~5 rungs).
5. WAM-CP-9 (committed-ITE / cut fix) — rung07 + rung15.
6. Findall mode-4 template.

## Verify-before-commit checklist for next session
```bash
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_prolog.sh        # GATE-1: 5/5
bash scripts/test_prolog_rung_suite.sh   # GATE-3: 91/107
bash scripts/test_crosscheck_prolog.sh   # GATE-2: 132/0
bash scripts/test_prolog_mode4_rung.sh   # GATE-4: 4/4
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l  # FACT: 0
```
