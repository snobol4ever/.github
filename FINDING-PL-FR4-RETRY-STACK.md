# FINDING-PL-FR4-RETRY-STACK — Prolog ζ-frame choice-point retry stack implementation

**Date:** 2026-08-07  
**Author:** Claude Sonnet 4.6 (session s6)  
**Status:** RUNTIME IMPLEMENTED; EMITTER INTEGRATION PENDING (see GOAL-PL-ZFRAME-RESTORE.md)

---

## What this finding covers

The `rt_pl_retry_push` / `rt_pl_retry_pop` pair added to `src/runtime/rt/rt.c` in this session.  These are the WAM B-register equivalent for the ζ-frame Prolog backtrack rendezvous — the frame-independent choice-point store that the MOVE_LABEL/DISJUNCTION backtrack scheme requires once the ζ-frame epilogue invalidates `rbp` before the backtrack read.

---

## The defect (Defect 2 per cursor)

`bb_move_label` stores the retry continuation into `[rbp + op_off + 16]`.  The ζ-frame epilogue (`xa_flat_zframe_epilogue_γ`) restores `rbp` to the caller's frame before backtrack fires — so the slot the caller reads is not the slot this box wrote.  Measured: the slot also aliases param-0 / result-cell-0, so the read returns a DESCR (`0x0000000100000028`), not a code pointer.  `jmp rax` with a DESCR value → rip=0 → SEGV.

---

## Canonical shape (verified from reference sources this session)

**GNU Prolog** (`EnginePl/wam_inst.h:92-107`):
- `ALTB(b)` on the B-register stack — entirely separate from the E (environment) stack
- `CHOICE_STATIC_SIZE = 8` words per choice point; retry address at `ALTB(b)` = word 7
- Read via `return ALTB(B)` with no frame pointer involved (`wam_inst.c:1097`)

**SWI-Prolog** (`pl-incl.h:1825-1838`):
- `struct choice { Choice parent; LocalFrame frame; union { Code pc; } value; }`
- `frame` is a **reference**, never storage; choice-point lifetime INDEPENDENT of activation-frame lifetime
- The `value.pc` field (the retry address) survives frame teardown by design

Both engines store the retry address off the activation frame.  LIFO discipline is sound: Prolog backtracking is stack-disciplined by the language definition; cut discards a contiguous top segment.

---

## Implementation in rt.c

```c
/* PL-FR-4 RETRY CONTINUATION STACK — the WAM B register for the ζ-frame regime. */
void **g_pl_retry;
int    g_pl_retry_top;
int    g_pl_retry_cap;

void rt_pl_retry_push(void *addr);   /* push retry continuation (WAM ALTB write) */
void *rt_pl_retry_pop(void);         /* pop retry continuation; 0 = exhausted = fail */
```

Dynamic array, doubling growth, `rt_ws_realloc`-backed.  Killswitch: emitter arms are gated on `g_emit.zframe_graph`, so unflagged graphs (SCRIP_PL_ZFRAME=0, SN4, Icon) never call these.

---

## What is NOT yet done (emitter integration)

The emitter arms in `bb_move_label.cpp` and `bb_indirect_goto.cpp` were NOT committed because their integration revealed a deeper architectural conflict: the medium for the retry address is correct (the choice-point stack), but the **value** pushed is wrong.

### Current (incorrect) emitter state
`bb_move_label`'s ζ-frame arm pushes `&n82_call_proc_staged_β` (TGT0 = the β of call_proc_staged).  `bb_indirect_goto`'s ζ-frame arm calls `rt_pl_retry_pop` → `jmp rax` to reach β.  Then β calls `rt_gen_spine_resume_enter`, restores rsp via `FRQ(act+8)`, and dispatches via either `jmp [rsp]` (legacy, crashes under ζ) or `jmp L(3)` (tried; infinite-loops on clause 1).

### Root cause of the loop
L(3) at the call_proc_staged site:
1. Saves rsp into `FRQ(act+8)`
2. Checks `first_done` flag (`FRQ(act)`)
3. If 0: sets flag to 1, calls `rt_proc_call_epilogue_γ` (delivers clause 1 result)
4. If nonzero: calls `rt_gen_spine_pass_γ` — **WRONG for Prolog**

`rt_gen_spine_pass_γ` is the Icon generator pass-through; it re-delivers its argument unchanged without advancing the clause selector.  For Prolog multi-clause predicates, `rt_proc_call_epilogue_γ` IS the next-clause mechanism (it pops the pcall record and the Prolog resolution machinery in bb_choice_state_t advances the cursor).  But calling it again on the second resume pops an empty pcall stack and returns FAILDESCR — also wrong.

### Correct fix (NOT YET IMPLEMENTED)

The retry address pushed by `bb_move_label`'s ζ-frame arm must be the **α label** of call_proc_staged (`lbls[k]`, not `betas[k]`), not β.  Then:

1. `n84_disjunction_α` → `rt_pl_retry_pop` → `jmp n82_call_proc_staged_α`
2. α re-stages args and calls `rt_proc_call_open_det` again — the Prolog runtime advances the clause cursor internally and returns the next clause's body pointer
3. The next clause executes, fires γ → `n83_move_label_α` → `rt_pl_retry_push(&n82_call_proc_staged_α)` again (for the third clause if any)
4. After all clauses exhausted, `rt_proc_call_open_det` returns 0 → `je L(1)` → ω path

This requires staging the α label into a second `g_emit` field (e.g., `lbl_t1`) at emit.cpp ~:2627, gated on `g_emit.zframe_graph && wantb`.

### One-line change set for next session

1. `src/emitter/emit.cpp` ~:2627 — after `g_move_label_tgt = wantb ? betas[k] : lbls[k]`, add:
   ```c
   if (wantb && g_emit.zframe_graph) g_emit.lbl_t1 = lbls[k]->name;  /* PL-FR-4: α re-entry */
   ```
2. `src/emitter/emit.h` — add `const char *lbl_t1;` to `emit_state_t`
3. `src/templates/bb_move_label.cpp` — `ml_retry_store` ζ-frame arm: use `lbl_t1` instead of TGT0
4. `src/templates/bb_indirect_goto.cpp` — ζ-frame arm: `rt_pl_retry_pop → jmp rax` (already correct; no β needed)
5. `src/templates/bb_call_proc_staged.cpp` — NO CHANGE to β; it is never entered on the ζ-frame path

---

## Witness program

```prolog
% /tmp/bt_minimal.pl
color(red). color(green). color(blue).
main :- color(X), write(X), nl, fail ; true.
```
Expected: `red\ngreen\nblue\n`, rc=0.  Currently: SEGV (mode 3) / infinite "red" loop (mode 4 with partial fix).

---

## Confirmed NOT the issue

Defect 1 (earlier, per cursor): `bcps_spine_gen_arm`'s β at `jmp qword ptr [rsp]` with `[rsp]=0`.  This fires BEFORE Defect 2.  Under ζ-frame, γ-retain restores rsp to entry_rsp = caller's spine frontier; `[rsp]` is caller data, not a landing word.  Once the retry address correctly points to α (not β), β is NEVER entered on the Prolog multi-clause backtrack path — Defect 1 disappears automatically.

