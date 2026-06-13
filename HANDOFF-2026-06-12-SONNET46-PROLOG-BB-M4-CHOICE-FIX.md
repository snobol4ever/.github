# HANDOFF — 2026-06-12 — Sonnet 4.6 — PROLOG-BB m4 bb_choice + callee-label investigation

**Goal:** GOAL-PROLOG-BB.md · m3/m4 parity.
**Watermark:** SCRIP `27b9fe7` · .github `(this commit)` (both green).

## Landed

### bb_choice.cpp — THREE m4 assembler bugs fixed (27b9fe7)

**Bug 1 — `mov edi, [rax+48]` / `mov edi, [rax+16]`:** x86 assembler rejected `mov r32, qword ptr [base+N]` (size mismatch). `[rax+48]` = `cursor` field (int), `[rax+16]` = `trail_mark` field (int) of `resolve_choice` struct. Fixed by adding three helpers to `resolution.c/.h`:
- `void rt_cp_trail_unwind(void)` — `rt_trail_unwind(resolve_cp_current()->trail_mark)`
- `void rt_cp_inc_cursor(void)` — `resolve_cp_current()->cursor++`
- `int  rt_cp_get_cursor(void)` — returns `resolve_cp_current()->cursor`

Template now calls these instead of direct field access.

**Bug 2 — β label defined twice:** `x86("label", _.lbl_β)` appeared inline in the dispatch loop AND `x86("def", "β")` at the tail — assembler rejected duplicate. Removed the trailing `def β + jmp ω`.

**Bug 3 — `.Lplch0_β_nosol` undefined:** code jumped to `plch("β_nosol")` but no label was ever defined. Added `x86("label", plch("β_nosol")) + x86("jmp", _.lbl_ω)` after the dispatch-retry block.

### emit_bb.c — IR_GOAL callee name uses zc->callee (27b9fe7)

`bb_prepare` for `IR_GOAL` now uses `zc->callee` (from `bb_goal_state_t`) as the authoritative callee name, falling back to `IR_LIT(nd).sval` only when `zc->callee` is absent. Rationale: `zc->callee` is set by `lower_prolog.c` directly from the AST functor name and is more reliable.

## NOT FIXED — C-LABEL bug (rung05/06/28/30 m4 linker errors)

`.Lplpred__S1_2` undefined at link. `_S1` is a DCG fresh-var name that somehow ends up as the callee label for what should be `member/2`'s recursive call.

**Diagnosis so far:**
- `--dump-bb` shows `sval="member"` on the IR_GOAL node — correct at IR level.
- `bb_prepare` debug print confirmed: `sval="member"`, `zc->callee="member"`, `_goal_nm="member"` at emit time for THAT node.
- Yet asm output still has `call .Lplpred__S1_2`.
- Conclusion: the `_S1_2` label is being emitted by a **different** IR_GOAL node than the one instrumented, or by a code path that bypasses `bb_prepare` entirely.

**Next step:** The `_S1_2` label appears inside `member`'s clause-2 body (the recursive call). `codegen_clause_dispatch` → `codegen_callee_block` → `codegen_graph_block` → `walk_bb_flat` → `case IR_GOAL: FILL(nd,...)` → `walk_bb_node` → `emit_core.c case IR_GOAL: bb_prepare(nd); bb_emit_x86(bb_goal())`. Add `fprintf(stderr, ...)` directly inside `emit_core.c case IR_GOAL` (BEFORE `bb_prepare`) to print `IR_LIT(nd).sval` and `((bb_goal_state_t*)(intptr_t)IR_LIT(nd).ival)->callee` for every IR_GOAL node emitted. This will identify which IR_GOAL node has `_S1` — it may be in a different `IR_graph_t` than expected (perhaps a callee graph built by `pl_gz_callee_get_any` that embeds a stale node).

## Gates

- GATE-1: m2/m3/m4 5/5 HARD ✓
- GATE-3: m2=114 · m3=**91**/24-FAIL (floor=91) · m4=**44**/61-FAIL+10-EXCISED (floor=44) ✓
- `bb_bin_t`: 0 · `g_vstack`: 0 · `test_gate_bb_one_box`: PASS ✓

## m4 failure taxonomy (HEAD)

- **Assembler errors gone** — bb_choice fix eliminated `operand type mismatch for 'mov'` and `β already defined` from rung05/06/27/30.
- **`_S1_2` linker errors** — rung05/06 (member recursion), rung28 (catch/DCG scope), rung30 (DCG nonterminals). Root cause: C-LABEL above.
- **Silent FAIL (wrong output)** — rung03/09/11/12/17/19/20/22/23/25/26/29/40/43 — rich-body-root path; `g_resolve_env` / GZ frame cell disconnection partially addressed by `rt_pl_frame_sync_env` but parity not yet achieved.
