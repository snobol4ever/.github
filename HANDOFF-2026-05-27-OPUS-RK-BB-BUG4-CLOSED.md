# HANDOFF — RK-BB-SEGFAULT-CLUSTER bug 4 closed; SM_LOAD_FRAME mode-4 analyzed

**Date:** 2026-05-27
**Model:** Opus 4.7
**Watermark:** one4all `ecd561b1`, .github HEAD, corpus unchanged

---

## What this session delivered

### bug 4 ✅ CLOSED — `lower_return` Raku return-value preservation

Single-file change to `src/lower/lower.c` (+2 -0):

```c
} else if (t->n > 0 && t->c[0] && g_lang == LANG_RAKU) {
    lower_expr(t->c[0]);
}
```

Inserted between the Snocone `g_sc_func_name` branch and the generic
non-Snocone branch in `lower_return`. Leaves the return-value expression
result on stack-top where `SM_RETURN` (sm_interp.c:1432) expects it — no
VOID_POP discarding it.

### Gates

| Gate              | Before | After  | Delta |
|-------------------|--------|--------|-------|
| GATE-RK mode-2    | 16/33  | 18/33  | +2    |
| GATE-RK4 mode-4   | 15/33  | 15/33  | HOLD  |
| Smoke raku        | 5/0    | 5/0    | HOLD  |
| Smoke icon        | 5/5    | 5/5    | HOLD  |
| Smoke prolog      | 5/5    | 5/5    | HOLD  |
| Smoke snobol4     | 13/0   | 13/0   | HOLD  |
| Broker Icon       | 198    | 198    | HOLD  |
| FACT RULE grep    | 0      | 0      | HOLD  |
| Build             | clean  | clean  | HOLD  |

**Flipped rungs:** `rk_subs`, `rk_combinator` (both depended on
return-value preservation through sub calls).

**Still failing (separate from bug 4):**
- `rk_try_catch25` — try/CATCH "Error 5 Undefined function"; not return-value related
- 13 other rungs — junctions, regex, hashes, file/stdio, gather (mode-2 BB_SUSPEND open)

---

## What this session analyzed but did NOT implement

### RK-BB-SM-FRAME-MODE4 — full mode-4 frame-slot architecture

The mode-4 x86 backend has **zero** frame-slot mechanism today. When
emit_sm.c hits an SM op without a dispatch arm, it emits the literal
text `"UNHANDLED SM_LOAD_FRAME\n"` which the assembler then treats as
an unknown instruction. Same for SM_STORE_FRAME.

**Why Raku is the first to hit this:** Icon mode-4 corpus passes 5/5
because Icon procs route through BB graphs and
`icn_bb_pump_proc_by_name`, bypassing SM entirely. Raku eager subs
route through SM_CALL_FN → SM_LABEL → SM_LOAD_FRAME body — the unbacked
path.

**Four pieces missing in mode-4** (designed but not built; see goal
file for full detail):

1. **User-sub callsite dispatch.** Today `SM_CALL_FN .S0, 1` (string
   "double") goes through `rt_call("double", 1)` which only knows about
   SNOBOL4 Define()-registered chunks. Need: in `sm_calls.cpp` X86 arm,
   check `g_stage2.proc_table[]` (already visible at emit) for the
   target name; if found, emit `call .L<entry_pc>` directly.

2. **Frame push at proc entry.** New SM op `SM_FRAME_ENTER nparams`
   emitted right after SM_LABEL in `lower_proc_skeletons` for LANG_RAKU.
   Template emits `mov edi, nparams; call rt_frame_enter@PLT`.

3. **Frame pop at proc exit.** `lower_return` LANG_RAKU branch
   additionally emits `SM_FRAME_LEAVE` before `SM_RETURN`. Template
   emits `call rt_frame_leave@PLT`.

4. **`rt_load_frame` / `rt_store_frame` in libscrip_rt.** New file
   `src/runtime/rt/rt_frame.c` mirroring `icn_runtime.c` IcnFrame shape.
   Templates in new `src/emitter/SM_templates/sm_frame_slots.cpp` with
   MEDIUM_MACRO_DEF + MEDIUM_TEXT arms; wired into `sm_op_is_dispatched`
   in emit_core.c and `codegen_sm_dispatch`.

**Estimated scope:** 6-10 hours. High risk of regressing Icon mode-4
(5/5) and broker Icon (198). Must run all four smokes + GATE-RK4 +
GATE-PK4 + broker after every substantive edit. The PEERS RULE and
FACT RULE both apply — every byte of x86 must come from templates.

**Lightweight alternative considered and rejected:** Lower Raku params
to SM_PUSH_VAR/STORE_VAR (global name table) instead of SM_LOAD/STORE_FRAME.
Cheap demo win but architecturally wrong — breaks recursion, breaks
nested calls. Not pursued.

---

## State of all four RK-BB-SEGFAULT-CLUSTER bugs

| Bug | Status | Commit | Description |
|---|---|---|---|
| 1 | ✅ | `0f3561c0` | union-clobber deref in polyglot_init |
| 2 | ✅ | `2a70abed` | lower_stmt + lower_proc_skeletons TT_SUB_DECL gating |
| 3 | ✅ | `2a70abed` | build_proc_scope TT_SUB_DECL branch |
| 4 | ✅ | `ecd561b1` | lower_return LANG_RAKU branch |

ALL FOUR CLOSED. The cluster is done; mode-2 Raku subs now correct.

---

## Commit on origin

```
ecd561b1 RK-BB-SEGFAULT-CLUSTER bug 4: lower_return preserves Raku return value
```

Visible on `origin/main`.

---

## Next session entry point

Goal: **GOAL-RAKU-BB.md**, step **RK-BB-SM-FRAME-MODE4**.
Goal file ⛔ NEXT SESSION block has the full 4-piece design.

Alternative goals if RK-BB-SM-FRAME-MODE4 is too large for a single
session:
- **rk_try_catch25** — separate try/CATCH "Error 5" issue; likely
  smaller scope.
- **bb 4 followup: SM dead-code trim** — proc bodies emit
  `RETURN; VOID_POP; RETURN` trailer; the trailing two SM ops are dead
  after an explicit return. Pre-existing structure, not a regression,
  but worth a sweep if mode-4 frame work lands.

Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Addendum — de-risking probes (same session, no code changes)

Two load-bearing assumptions of the RK-BB-SM-FRAME-MODE4 design were
verified empirically before close, to save the next session debugging time.
No source files in one4all were modified by these probes (read-only
analysis); findings folded into GOAL-RAKU-BB.md design pieces #1 and #3.

**Probe 1 — label resolution off-by-one (would have broken `call .L<entry_pc>`).**
`proc_table[].entry_pc` resolves to the named SM_LABEL's own pc
(double=1, greet=12, add=21, classify=32 in rk_subs), via
`sm_label_pc_lookup` → `instrs[i].a[1].i`. But the named SM_LABEL emits NO
`.L<pc>:` symbol (the LABEL macro is empty, sm_jumps.cpp:116). The emitted
`.L<pc>:` lands at `entry_pc + 1` because `pc_used_mark(pc+1)` fires for
named labels. Empirically `.L1` is absent from the .s but `.L2` present.
⟹ `call .L<entry_pc>` would assemble-fail with "undefined label .L1".
FIX recorded: emit a stable `.L_sub_<name>:` symbol in sm_jumps.cpp
sm_label_str MEDIUM_TEXT arm (pSM->a[0].s already available, currently
`(void)pSM`), callsite emits `call .L_sub_<name>`. No pc arithmetic.

**Probe 2 — call/ret machine-stack convention.**
The RETURN macro is bare x86 `ret`. SM_RETURN emits `pop rbp` before it
ONLY under `g_in_define_body`. So Raku subs entered via plain `call`
return natively via the paired `ret` — no setjmp/longjmp. Two constraints
recorded in goal: (i) proc body must keep rsp balanced (SM vstack is heap,
so SM pushes are safe; watch raw machine `push`); (ii) `g_in_define_body`
must be FALSE during Raku skeleton emission or SM_RETURN emits a spurious
`pop rbp` (no matching push) → corruption. Verify, or gate pop rbp on a
new g_in_raku_sub flag.

Net effect: piece #1 and #3 of the design are now concrete and de-risked;
piece #2 (frame enter) and #4 (rt_frame.c + templates) remain as specified.

