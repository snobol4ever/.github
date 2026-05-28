# HANDOFF — RK-BB-SM-FRAME-MODE4 pieces 4a/4b done + piece 1 scaffolded

**Date:** 2026-05-28
**Model:** Opus 4.7
**Watermark:** one4all `3eece6a3`, .github HEAD, corpus unchanged

---

## What this session delivered (3 commits, zero regressions)

Started the RK-BB-SM-FRAME-MODE4 implementation that prior sessions had
analyzed and deferred. Committed each piece as it went green so the tree is
always bisectable and never left half-broken.

### piece 4a — `d6fe17e2` — runtime frame stack
`src/runtime/rt/rt.c` + `rt.h` (+73). Four functions in libscrip_rt:
- `rt_frame_enter(nparams)` — pops nparams source-order args off the vstack
  into a fresh frame; slot[0]=arg0 … slot[n-1]=arg(n-1).
- `rt_frame_leave()` — pops the top frame.
- `rt_load_frame(slot)` — pushes slot value onto vstack.
- `rt_store_frame(slot)` — pops vstack-top into slot, pushes it back
  (non-consuming, parallel to rt_nv_set so a following VOID_POP balances).
Fixed-size 256-frame × 64-slot stack. All four symbols exported (nm -D).
Pure addition, no callers → gates HOLD.

### piece 4b — `7c9d4570` — slot templates (THE BLOCKER FALLS)
New `src/emitter/SM_templates/sm_frame_slots.cpp` (sm_frame_slot) with
MACRO_DEF + BINARY + TEXT x86 arms, calling rt_load_frame/rt_store_frame.
Wired into sm_templates.h, codegen_sm_dispatch, sm_op_is_dispatched,
the emit_sm.c one_per_group prelude, and the Makefile (source + compile rule).

**Effect:** the original mode-4 wall — assembler error `no such instruction:
'unhandled SM_LOAD_FRAME'` — is GONE. `rk_subs` mode-4 emission now shows
zero UNHANDLED, emits `LOAD_FRAME 0` / `LOAD_FRAME 1` with correct slots, and
**assembles cleanly**. Gates HOLD (the new opcodes only fire for Raku subs,
which weren't passing mode-4 anyway).

### piece 1 — `3eece6a3` — linkage helpers (SCAFFOLDING, not wired)
- `rk_sub_lookup(name)` [emit_sm.c] → nparams if `name` is a LANG_RAKU sub
  with resolved entry_pc in g_stage2.proc_table, else -1. (g_stage2 + LANG_RAKU
  in scope here via icn_runtime.h → scrip_cc.h.)
- `rk_sub_label(d,sz,name)` [emit_bb.c] → mints `.Lrksub_<sanitized-name>`,
  mirroring pl_call_block_label. Pure string, byte-free (FACT RULE).
Declared in emit_sm.h / emit_bb.h. Defined-but-unused → identical behavior to
4b. Build clean, gates HOLD.

---

## Current state of rk_subs in mode-4

Assembles + links + runs, but prints `Error 5 Undefined function`: the
callsite still does `rt_call("double",1)` which never enters the sub body or
sets up a frame. The two template wirings (piece 1, below) close the loop.

---

## THE LAST MILE — piece 1 wiring (next session)

Two template edits. Helpers are ready; both templates must add
`#include "stage2.h"` and `#include "emit_bb.h"` (the latter for rk_sub_label;
emit_sm.h already declares rk_sub_lookup). Model the includes on
sm_bb_calls.cpp which already pulls stage2.h inside its extern "C" block.

**WIRE 1 — sm_jumps.cpp, sm_label_str, X86 MEDIUM_TEXT arm.**
Currently `(void)pSM;` then `return s_1asm("LABEL");`. Change: if
`rk_sub_lookup(pSM->a[0].s) >= 0`, build `<lbl>` via rk_sub_label and return
`s_directive("<lbl>:") + s_1asm("LABEL")`. Else unchanged. Remove `(void)pSM`.

**WIRE 2 — sm_calls.cpp, sm_call_str, X86 MEDIUM_TEXT arm.**
Currently emits `CALL_FN .Sx, n`. Change: `int np = rk_sub_lookup(pSM->a[0].s);`
if `np >= 0`, return (with `<lbl>` from rk_sub_label):
```
mov edi, <np>
call rt_frame_enter@PLT
call <lbl>
call rt_frame_leave@PLT
```
as raw MEDIUM_TEXT lines (assembler text, FACT-RULE-safe — same class as
PUSH_INT's `call rt_push_int@PLT`). Else the existing CALL_FN path unchanged.

**Invariants already handled — do NOT redo:**
- Arg order: rt_frame_enter reverses on pop (slot0=arg0). Don't re-reverse.
- call/ret: SM_RETURN is bare `ret`; the `call <lbl>` pairs with it natively.
  Retval left on vstack by the bug-4 lower_return LANG_RAKU branch.
  rt_frame_leave runs at the callsite AFTER the call returns → SM_RETURN
  stays untouched, no new SM opcodes.
- g_in_define_body must be FALSE during Raku skeleton emission (else SM_RETURN
  emits spurious `pop rbp`). Verify no `pop rbp` in a Raku sub body in the .s.

**Verify in order (commit only when all pass):**
1. emission has zero UNHANDLED
2. `.Lrksub_double:` defined once; `call .Lrksub_double` present
3. `run_raku_via_x86_backend.sh rk_subs.raku` → 14 / hello raku / 7 /
   positive / zero / negative
4. GATE-RK4 (expect rk_subs flip, maybe rk_combinator), Icon mode-4 5/5 HOLD,
   broker 198 HOLD, smokes 5/5/13/5 HOLD, FACT RULE 0
5. recursion sanity: a factorial Raku sub (fixed 256-frame stack + nested
   call/ret).

---

## Commit lineage (one4all, all on origin/main)

```
3eece6a3 RK-BB-SM-FRAME-MODE4 piece 1 SCAFFOLDING: rk_sub_lookup + rk_sub_label
7c9d4570 RK-BB-SM-FRAME-MODE4 piece 4b: SM_LOAD_FRAME/STORE_FRAME x86 templates
d6fe17e2 RK-BB-SM-FRAME-MODE4 piece 4a: rt_frame_* runtime in libscrip_rt
ecd561b1 RK-BB-SEGFAULT-CLUSTER bug 4: lower_return preserves Raku return value
```

(b2f773bc Icon Step 10a-9 and other concurrent commits interleave via rebase.)

---

## Gates at handoff

| Gate | Result |
|---|---|
| GATE-RK mode-2 | 18/33 HOLD |
| GATE-RK4 mode-4 | 15/33 HOLD (moves when piece 1 wiring lands) |
| Smoke raku/icon/prolog/snobol4 | 5/5/5/13 HOLD |
| Icon mode-4 corpus | 5/5 HOLD |
| Broker Icon | 198 HOLD |
| FACT RULE grep | 0 |
| Build | clean |

Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
