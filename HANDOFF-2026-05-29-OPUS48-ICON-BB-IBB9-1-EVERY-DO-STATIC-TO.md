# HANDOFF — ICON-BB IBB-9-1 — `every x := 1 to N do body` (static-TO assign)

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-9-1 (landed) + IBB-9-2 (diagnosed, NOT landed)
**one4all:** `e8f66866` (on origin/main, rebased onto concurrent Prolog/SNOBOL4 work)
**Repos touched:** one4all (2 files), .github (GOAL watermark + this doc)

---

## What landed — IBB-9-1 (`e8f66866`, pushed)

`every x := 1 to N do body` now runs in mode-3, byte-identical to mode-2, zero SM.

**JCON grounding (read this session from `jcon/tran/irgen.icn`):** `ir_a_Every`
(irgen.icn:309) does NOT special-case `x := …`. It treats `every x := GEN do B`
as `every (x:=GEN) do B` where `p.expr` is the assignment. Because `:=` is in
`ir_a_Binop`'s `funcs` set, `ir_binary` (irgen.icn:438-444) routes
`expr.resume → right.resume` — the assignment is **transparent to resume**, just
forwarding it into the rhs generator. The generator yields, `right.success`
re-applies the store, re-yields. That is the model.

**SCRIP transcription (2 files):**

1. `src/lower/lower_icn.c` `lower_icn_new_Every_ag`: intercept TT_EVERY whose
   `c[0]` is TT_ASSIGN wrapping a **static literal TT_TO** (lowers to BB_TO with
   α==β==NULL) and a plain TT_VAR lhs. Build an interposed BB_ASSIGN store node:
   - `store->α = lhs` (BB_VAR), `store->β = togen` (non-NULL so the mode-2
     null guard at bb_exec.c:1157 passes; NOT recursed because ival=1),
     `store->ival = 1`.
   - ival=1 topology: `gen.γ=store, store.γ=body, body.γ=gen, body.ω=gen,
     gen.ω=bb`, `bb->α=gen_chain_entry`, `bb->β=store`, `bb->ival=1`.
   - **TT_TO_BY excluded**: `lower_icn_new_ToBy` keeps α=lo/β=hi operand boxes
     for TO_BY even with literal bounds (template uses a BB_LIT_I fast-path, not
     α/β scrubbing), so it never matches the α==β==NULL static shape. `to…by`
     needs separate BB_TO_BY mode-3 generator wiring (not done).

2. `src/emitter/emit_bb.c` `flat_drive_every` ival=1: detect the interposed
   store (`pBB->β->t == BB_ASSIGN && pBB->β->ival == 1 && pBB->β->γ`) and emit
   three segments — walk gen, walk store, walk the real do-body (`store->γ`) → gen_β.
   - **Critical bug found + fixed:** the store walk's `lbl_β` must NOT be `gen_β`.
     `flat_drive_assign` calls `EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω)` which would define
     `gen_β: jmp gen_β` — an infinite self-jump. Routed the store's β to a dead
     `xevery%d_store_ω` stub instead.

Mode-2 reads the yielded value via `ag_ring_peek(0)` (chain walker pushes every
step to the ring); mode-3 pops it from the vstack via `rt_pop_nv_set` (BB_TO
pushes via rt_push_int, BB_ASSIGN template pops via rt_pop_nv_set — same vstack).

**Result:** corpus same-sweep **213→216 (+3)**: `rung37_every_do_hello`,
`rung35_block_body_nested_block`, `range_to`. **Zero regressions** (verified by
diffing the full pass-set before/after — 0 lost). SEGV 0. Canonical byte-identical
+ zero-SM. Gates: smoke icon/prolog 5/5, broker 42/11, FACT 0.

---

## Gate methodology used this session

`/tmp/sweep.sh` — for each `/home/claude/corpus/programs/icon/*.icn`: run m2
(`--interp`), skip if m2 rc≠0; run m3 (`--run`); PASS iff `m3 rc==0 && m2==m3`.
Counts PASS/SEGV(139)/ABORT(≥134)/FAIL(other). **Baseline at `e8f66866` = 216 PASS,
SEGV 0.** Use this exact filter to compare; a drop below 216 is a regression.

---

## IBB-9-2 — `while C do B` — DIAGNOSED, NOT LANDED (next session start here)

I investigated the while-cond routing and **deliberately did NOT commit** the
attempt (it regressed 26 programs). The diagnosis is solid; the fix needs the
correction below.

**The bug:** `flat_drive_while` (emit_bb.c:1029, a JCON-faithful driver added by
concurrent work today) wires the loop topology correctly, but the relop
condition's RESULT does not gate the loop. Probe: `i:=5; while i<=3 do write(i);
write(99)` → m3 prints `5 5 5…` (infinite), m2 prints `99`. The cond's γ is taken
unconditionally → body always runs.

**Two CONFIRMED facts that change the obvious fix:**

1. **The while-cond relop is TREE-SHAPE, not AG-pure.** Debug-confirmed:
   `pBB->α->t == BB_BINOP` but **α/β operand children are NON-NULL**, `ival` = the
   relop opcode (observed `ival=6`). This is unlike BB_IF conds (which are AG-pure
   α==β==NULL). So detecting the relop by `α==NULL && β==NULL` FAILS — my first
   conditional-router attempt never fired and the loop still ran infinitely.
   **Detect by the BB_BINOP opcode (`ival` ∈ relop set), not by shape.**

2. **A router must fire ONLY for relop conds.** My first (unconditional) router
   regressed 26 programs of the form `while line := read() do …`, `while c := a[i]
   do …`. A non-relop cond (BB_ASSIGN, generator, plain call) signals truth via its
   OWN γ (produced a value) / ω (none) and does NOT set LAST_OK. Inserting a
   `rt_last_ok` router there branches on garbage. These must keep the existing
   direct γ/ω routing.

**Before coding the fix:** inspect `flat_drive_binop_tree` (emit_bb.c:805) and the
tree-shape relop apply arm in `bb_binop.cpp` to determine whether a tree-shape
relop (a) sets LAST_OK + does an unconditional `jmp γ` (→ needs the `bb_if.cpp`
router, like IBB-8b) or (b) already routes true/false via its own γ/ω (→ no router;
just ensure `flat_drive_while` passes cond_true as γ and cond_false as ω and the
relop honors ω). If (b), the fix may be as small as making the relop's ω reach
`cond_false` instead of falling through. Do NOT assume the BB_IF pattern transfers
— the AG-pure vs tree-shape distinction is exactly why it doesn't transfer cleanly.

**Note on `read()`:** several would-be while targets (`meander`, `rung36_jcon_*`,
the read-loop programs) ALSO need `read()` builtin support and/or user-proc
dispatch — they will still ABORT after the cond-router lands. Use a proc-free,
read-free repro (`i:=N; while i<=M do {…; i+:=1}`) to gate IBB-9-2; the target is
`rung35_block_body_while_do_block` → `1 2 3` WITHOUT dropping the 216.

---

## Remaining IBB-9 rungs (in GOAL-ICON-BB.md, JCON-grounded)

- IBB-9-3 until (shares the while driver; `ir_a_Until` flips the two cond edges;
  most corpus `until` tests also need user-proc dispatch).
- IBB-9-4 every ival=2 (gen-bearing chain, simple body) — mode-3 emit gap.
- IBB-9-5 every ival=3 (BODY-MEDIATED block body); **note a mode-2 bug** —
  `every x:=1 to 3 do {y:=x*2;write(y)}` prints `2 2 2` in m2 (should be `2 4 6`,
  which my m3 already produces); fix mode-2 ival=3 x-rebind alongside or the
  byte-identical gate cannot pass.
- IBB-9-6 user-proc dispatch (JCON `ir_a_Call:360`) — largest ABORT cluster;
  needs `rt_call_proc` + BB_RETURN flat-wire.
- IBB-9-7 write(BB_CALL) / write(proc-result) — depends on 9-6.
- IBB-9-8 DEFERRED: unbounded/expression-context resume (computed-goto
  continuation, JCON `ir_MoveLabel`+`ir_IndirectGoto`; the `bounded` flag SCRIP
  ignores). Only when a corpus program assigns a generator-bearing if/case/alt to
  a var and resumes it.

---

## Reference material extracted this session

`jcon-master.zip` → `/home/claude/jcon_icon/jcon-master/tran/irgen.icn` (1559 lines,
the Icon→IR translator; the canonical CFG SCRIP's lowering mirrors). Procedures
read in full: `ir_a_Every` (309), `ir_a_ToBy` (1168), `ir_a_Binop`/`ir_binary`
(430-512), `ir_a_While` (1008), `ir_a_Until` (981), `ir_a_Repeat` (847),
`ir_a_Suspend` (937), `ir_a_Break`/`ir_a_Next` (1082-1165), `ir_init_loop` (1435).
The spine of every loop form: body-success/failure routes to `expr.resume` (every:
pull next generator value) vs `expr.start` (while/until: re-evaluate cond fresh).
