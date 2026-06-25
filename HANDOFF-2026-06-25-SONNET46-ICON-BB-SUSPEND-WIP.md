# HANDOFF: ICON-BB SUSPEND (User-Defined Generators) — WIP, Two Bugs Remaining

**Date:** 2026-06-25  
**Model:** Claude Sonnet 4.6  
**Commit:** 044c181 (SCRIP main)  
**Status:** WIP — all six pieces coded and building clean; two bugs block output  
**Baseline:** m3 PASS=169 (rung03_suspend_* EXCISED at gate before this session)

---

## What Was Done This Session

Six-file implementation of Icon user-defined generators (`suspend`/`resume`) for
GOAL-ICON-BB (100% Byrd-Box codegen, stackless x86, four-port boxes).
Architecture: five-piece resume-spine from DESIGN-ICON-SUSPEND.md §4A (Lon-approved).

### Files Changed (all in commit 044c181)

| File | Change |
|------|--------|
| `src/runtime/rt/rt.h` | Declared `rt_proc_set_generator` / `rt_proc_is_generator` |
| `src/runtime/rt/rt.c` | Added `is_generator` to `rt_proc_t`; setter/getter scanning `g_rt_gen_procs` |
| `src/driver/scrip.c` | (1) Generator flag at first-pass registration (before resolve); (2) `g_gen_proc_active` gated around per-proc chain build in both m3 + m4 loops; (3) Gate flip: IR_SUSPEND admitted if operand[0] present |
| `src/emitter/emit_bb.c` | (1) Defined `g_gen_proc_active`; (2) `resolve_call_kinds_descr`: gen procs → `IR_PROC_GEN`; (3) `walk_bb_flat`: `case IR_PROC_GEN` dispatches as staged call; (4) `descr_chain_arity`: `IR_PROC_GEN` → 0; (5) BFS ω-queue admits `IR_PROC_GEN`; (6) `bb_call_route_classify` line ~2915: `rt_proc_is_registered+rt_proc_is_generator` guard above the `rt_builtin_is_generator` BYNAME line |
| `src/emitter/XA_templates/xa_flat.cpp` | TEXT frame-active prologue emits `cmp esi,0 / jne β` when `g_gen_proc_active` |
| `src/emitter/BB_templates/bb_call_proc_staged.cpp` | Added extern decls; `bcps_bin_gen_arm` + `bcps_txt_gen_arm` (α: stage args→`rt_proc_call_gen`→slot→cmp 99/jω/jγ; β: `rt_proc_resume_gen`→slot→cmp 99/jω/jγ); dispatch branches on `rt_proc_is_generator(_.op_sval)` |

### Verified Working
- Both `scrip` and `libscrip_rt.so` build clean after all edits
- M4 asm for `proc_upto_α` shows `cmp esi, 0 / jne proc_upto_β` — TEXT prologue correct
- Gate flip: `rung03_suspend_gen` no longer EXCISED; reaches runtime (no hang)

---

## Two Remaining Bugs (next session picks these up in order)

### BUG A — Name Collision (call-site routing: `upto` shadows to builtin)

**Symptom:** `rung03_suspend_gen` (which uses `upto`) runs but prints nothing.  
**Root cause:** The caller's m4 asm shows `upto` is routed via `rt_call_arr` by-name,
not the `IR_PROC_GEN` route. Even though `bb_call_route_classify` (line 2915) now
has the `is_registered+is_generator` guard, the **IR node was already rewritten** by
`resolve_call_kinds_descr` — BUT the node's op-code is `IR_CALL` (dv=3.0, subgraph)
because `upto` arguments are lowered as subgraph-call subgraphs, not as the staged
flat-call subgraphs. Check whether `resolve_call_kinds_descr` is even reaching the
node for the `upto(4)` call (it might be on the main BB graph, not a proc graph,
so `g_gen_proc_active` is 0 there).

**Probable fix:** The collision guard in `resolve_call_kinds_descr` (emit_bb.c, the block
around line 3808) only triggers when the node is `IR_CALL` with dv==3.0 **and** the
global `rt_proc_is_generator` returns true. Verify `rt_proc_is_generator("upto")` is
returning 1 at that point (add a `fprintf(stderr,...)` probe). If it is, check whether
the node op is actually `IR_CALL_PROC_STAGED` already (from a prior rewrite) — in that
case add `|| nd->op == IR_CALL_PROC_STAGED` to the rewrite condition and re-route to
`IR_PROC_GEN`. If it isn't, the flag isn't being set before the resolve runs.

**Isolate first with `downto`** (rung03_suspend_gen_filter.icn) — `downto` doesn't
collide with any builtin, so it exercises the non-collision path cleanly.

### BUG B — Do-Body Slot Threading

**Symptom:** Generator procs with arithmetic in the do-body (e.g. `i := i + 1`)
produce a BOMB: `bb_assign_local: needs descr flat-chain + rhs slot + varslot + own slot`.

**Root cause:** `descr_chain_operand_refs` (emit_bb.c ~line 3762) does a BFS/DFS over
the IR to wire RPN operand slots before emission. It traverses γ edges and call/binop ω
edges, but **never descends into `IR_SUSPEND` operand[1]** (the do-body). So any node
inside the do-body (BINOP, ASSIGN, etc.) never gets its operand slots registered →
slot is -1 at emit time → BOMB.

**Fix (exact edit):** In `descr_chain_operand_refs`, find the loop body that pushes
nodes onto the traversal stack (around line 3762, just before the `if (c->γ.node ...)`
γ-push). Add immediately after the existing IR_MAP/IR_GREP ω-push line:

```c
if (c->op == IR_SUSPEND && c->n_operands > 1 && c->operands[1] && sv < 512)
    stkv[sv++] = (IR_t *)c->operands[1];
```

This mirrors the BFS fix already applied at ~line 3505 for the chain-wiring pass.

**Test order after fixes:**
1. `./scrip --run .../rung03_suspend_gen_filter.icn` → expect `4\n3\n2\n1`  (downto, no collision)
2. `./scrip --run .../rung03_suspend_gen.icn` → expect `1\n2\n3\n4`  (upto, collision)
3. `./scrip --run .../rung03_suspend_gen_compose.icn` → expect `1\n2\n1\n2`  (compose)

---

## Architecture Recap (suspend resume-spine, for context)

- **Piece 1 (rt.c, LANDED):** `rt_proc_call_gen(name,nargs)` allocates persistent activation
  frame, calls proc slab with entry=0 (fresh); `rt_proc_resume_gen()` calls top activation
  with entry=1 (resume). entry=1 → slab's prologue `cmp esi,0 / jne β` jumps to β.
- **Piece 2 (xa_flat.cpp, LANDED):** TEXT frame-active prologue emits entry-dispatch for
  generator procs (gated on `g_gen_proc_active`).
- **Piece 3 (lower_icon.c, LANDED):** `TT_SUSPEND` → `IR_SUSPEND`; `icn_body_has_suspend`
  sets `proc_table[pi].is_generator`.
- **Piece 4 (emit_bb.c, LANDED):** `flat_drive_suspend` wires the suspend α (yield+copy to
  frame[0], jmp γ) and β (jmp do-body). Chain-wiring sets `g_suspend_dobody_beta`.
- **Piece 5 (bb_call_proc_staged.cpp, LANDED):** Generator arms dispatch `rt_proc_call_gen`
  (α) and `rt_proc_resume_gen` (β).

---

## Key Rules (do not violate)

- TEMPLATE-ONLY emission — only `x86(...)` in templates
- BOTH-MEDIUM MANDATORY — every template must have both MEDIUM_BINARY and MEDIUM_TEXT arms
- No MEDIUM_* tokens inside BB_templates (xa_flat.cpp is XA_templates, ok to switch there)
- Stackless one-register frame: r12=ζ, r13=Σ, r14=δ, r15=Δ, rbx=NV-hash
- Four Greek port names always: α β γ ω
- No C Byrd-box functions
- Icon SEMICOLON-REQUIRED in .icn programs
- `(void*,int entry)` proc re-entry ALLOWED (Lon ruling 2026-06-24)

---

## What NOT To Do

- Do not claim victory until all three rung03 programs are green AND regression confirms
  no loss below PASS=169
- Do not commit directly to main without verifying rung03 green — use a WIP commit message
- Do not run `--interp` (mode-2 is gone); use `--run` (m3) and `--compile ... | as...` (m4)
- The `.expected` files in corpus are the oracle, not `--interp` output

