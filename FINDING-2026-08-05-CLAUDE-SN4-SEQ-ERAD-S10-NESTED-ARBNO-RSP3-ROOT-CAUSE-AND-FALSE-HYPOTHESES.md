# FINDING 2026-08-05 CLAUDE SN4 SEQ-ERAD S10 — NESTED-ARBNO rsp=3 ROOT CAUSE AND TWO FALSIFIED HYPOTHESES

**Gate entering:** 90 pass / 11 xfail / 35 XPASS / 5 REGRESSION (H24 H25 X02 X06 X11 — all nested ARBNO SIGSEGV).
**Gate exiting:** 90 pass / 11 xfail / 35 XPASS / 5 REGRESSION (unchanged — root cause diagnosed, fix deferred).
**SCRIP commit:** `18e65150` (cleanup of false WIP hypothesis + op_body_has_arbno scaffolding).

---

## TWO FALSIFIED HYPOTHESES (do not retry)

### Hypothesis 1 — WIP commit geometry-buffer mn-=40 (FALSIFIED)

The s9 WIP commit `f9764db2` proposed: the inner ARBNO's `op_sa` is 16B or 40B too high because the deleted IR_MATCH_SEQUENCE container anchored `mn` lower. The fix attempted to lower `mn` by detecting the sentinel IR_GOTO at `g->all[i0-1]`.

**Falsified:** (a) the sentinel detection predicate `g->all[i0-1]->op == IR_GOTO && n_operands == 0` was wrong — the sentinel is at `g->all[before]` not reliably at `i0-1`; (b) the corrected value (-40 or -16) was not measured against a known-good; (c) gdb showed the crash is `rsp = 0x3` (a STRING descriptor tag loaded into RSP), not a frame geometry misalignment. This class of fix addresses the wrong level.

### Hypothesis 2 — View-restore at PAIR(2)/PAIR(3) (FALSIFIED)

After correct analysis showing the inner ARBNO β sets `zv()=rbp` to the inner element view, I attempted unconditional `lea rbp,[rsp+(24-op_sa)]` at PAIR(2)/PAIR(3) in the chain arm (originally gated by `arbno_u2_frame()`). With the gate removed entirely: 17 regressions (D09/D12/D13 DEFER-TAIL cases + F06 FENCE-in-ARBNO + G12/G19/G20 FENCE0-nested + X01–X11). Gated by the new `op_body_has_arbno` flag: 11 regressions (all nested-ARBNO, worse than baseline). Both forms break programs.

**Falsified by reasoning:** The inner ARBNO σ (PAIR(2)) already restores `zv()` at line 234 of the chain arm: `mov zv(), FRQ(op_sa - 24)` restores the outer element view BEFORE `x86_gamma()`. So by the time the outer ARBNO's PAIR(2) fires, rbp IS the outer element view. The view is not the problem.

---

## TRUE ROOT CAUSE — confirmed by gdb

### gdb measurement (X02 binary, compiled from `./scrip --compile`)

```
Break at n21_match_arbno_af L(2) exhaust (0x4018dc):
  rbp = 0x7fffffffe830
  rsp = 0x3           ← ALREADY CORRUPTED at this point
  [rbp + 0xf8] = 0x0  ← saved_rsp slot is ZERO (was overwritten)
```

RSP = 0x3 = STRING type tag. The stack pointer was overwritten with a DESCR tag value BEFORE L(2) fires. The corruption happens somewhere between inner ARBNO α (which correctly stores `rsp` at `[rbp+248]`) and the L(2) exhaust.

### Slot layout (outer element, X02)

With outer ARBNO `op_off_loff = 160`, `op_sa = 192`, outer element view = `outer_elem - 168`:
- `[outer_view + 160]` = outer ARBNO entry cursor
- `[outer_view + 164]` = yield cursor
- `[outer_view + 168]` = count
- `[outer_view + 176]` = COLLECTION ptr
- `[outer_view + 184]` = outer ARBNO saved_rsp ← outer α saves here

Inner ARBNO `op_off_loff = 224`, `op_sa = 256`, inner element view = `inner_elem - 232`:
- `[outer_view + 224]` = inner ARBNO entry cursor (at flat slot 224 in outer element)
- `[outer_view + 228]` = yield cursor
- `[outer_view + 232]` = count
- `[outer_view + 240]` = COLLECTION ptr
- `[outer_view + 248]` = inner ARBNO saved_rsp ← inner α saves here
- `[outer_view + 256]` = NOTANY result slot (body node at flat offset 256)
- `[outer_view + 264]` = NOTANY result slot upper 8B

The outer element is 128B. The inner ARBNO saved_rsp lives at outer element offset 80 (`248 - 168 = 80`). The body window is 96B (`mx - mn = 288 - 192`). All slots fit within the 128B outer element. This is sound.

### What the gdb data tells us

The saved_rsp slot is ZERO when L(2) fires. Zero is not a valid stack pointer. The slot was written by n21 α as `mov [rbp+248], rsp` where rbp was the outer element view. Something subsequently **zeroed `[outer_view + 248]`**. The most likely source: the outer element's initialization in β zeroes the element body window via `arbno_fill_window`. Let me check: `arbno_fill_window` zeros `[rsp + 24 .. rsp + op_sb)` = `[rsp + 24 .. rsp + 128)`. Relative to the element view `rbp = rsp - 168`, this is `[rbp + 192 .. rbp + 296)`. The inner ARBNO saved_rsp is at `[rbp + 248]` — **which falls inside `[192, 296)`**!

### The actual bug

**The outer ARBNO β's `arbno_fill_window` zeroes the inner ARBNO's saved_rsp slot** on EVERY outer iteration's β, because the saved_rsp slot at `[outer_view + 248]` = element offset 80 is within the body window range `[24, 128)` that `arbno_fill_window` clears.

The inner ARBNO α stores saved_rsp. Then outer ARBNO β for the NEXT iteration pushes a new outer element, which calls `arbno_fill_window` on the NEW element. This doesn't touch the previous element's saved_rsp. BUT — within a SINGLE outer iteration, if the inner ARBNO's saved_rsp slot is reachable from the outer element fill, the fill happens at outer β time (before inner α), so the order is:

1. Outer β fires, pushes outer element, fills body window (zeros [rbp+192..rbp+296))
2. Inner α fires, stores saved_rsp to [rbp+248] ✓ (AFTER the fill)
3. Inner β fires, pushes inner element
4. Inner body runs... succeeds... inner ARBNO iterates
5. Inner ARBNO exhausts at L(2): reads [rbp+248] — should still be the saved_rsp from step 2 ✓

Actually the fill happens BEFORE inner α within the same outer iteration. So the fill doesn't clobber the save. But gdb shows rsp=3 at L(2), meaning [rbp+248] = 0 (not 3, but the saved_rsp was zero, and then L(2) does `mov rsp, [rbp+248]` → rsp=0... not 3).

Wait — gdb showed `rsp = 0x3` at L(2), not rsp=0. And `[rbp+0xf8] = 0` at that point. So `mov rsp, [rbp+248]` would have set rsp=0, not 3. The rsp=3 is from a DIFFERENT instruction. The `[rbp+0xf8]=0` shows the slot is zero at the WATCHPOINT stop (which was at `4018dc`, the start of L(2)), before `mov rsp,[rbp+0xf8]` executes. So rsp=3 was set by something ELSE before L(2).

The rsp=3 must have been set by the earlier part of n21_af (before the `jz .Lx66_2` branch). Specifically, `lea rsp, [rbp + 0x118]` in n21_af sets rsp = `rbp + 280`. If rbp itself was corrupted at that point...

**Revised hypothesis:** rbp (the outer element view) is corrupted. `mov rbp, rdx` in n21_af sets rbp = RSP(0) of the inner element. If RSP(0) of the inner element holds a corrupted value, rbp becomes wrong, then `mov rsp, [rbp + 0xf8]` reads from a wrong address.

RSP(0) of the inner element is set by β: `mov [rsp+0], rbp` = outer element view. If the outer element view (rbp at β time) was already corrupted...

**This needs another session with breakpoints at n21 β specifically** to catch when RSP(0) gets a wrong value. The corruption chain is: outer element view → RSP(0) of inner element → rbp at n21_af → [rbp+0xf8] computation → wrong rsp.

---

## NEXT RUNG

**Set breakpoint at n21_match_arbno_β (`0x40183d`), run to X02 crash, print rbp and [rsp+0] after `mov [rsp], rbp` to see what outer element view is at the time of the inner element push that leads to the crash.**

Specifically: after the first outer ARBNO iteration completes (inner ARBNO succeeded, LIT ')' matched), outer β fires for the second outer iteration. At that point the inner elements from the first iteration are STILL on the stack. Does the second outer β push land its element at a location that was supposed to be clean but was already occupied by an inner element?

The key measurement: at each n21 β firing, print `rbp` (= outer element view) and `rsp` (= new inner element top). Confirm that `rsp - 48 >= outer_elem_bottom` — i.e., the inner element fits within available stack space and doesn't overlap with something the outer ARBNO needs.

**Suspect:** the inner element from the first outer iteration is still alive (not yet popped — it's a suspended backtrack frame). When the outer ARBNO β fires for the second outer iteration, it pushes the new outer element ON TOP of the first outer element AND the first inner elements. The second outer element is at `rsp_after_first_outer_and_inner_pushes - 128`. Inside the second outer element's body window, slots like `[outer_view2 + 248]` (inner ARBNO saved_rsp within element 2) may overlap with slots in the first outer element's frame or first inner elements' frames. If so, the inner ARBNO within the second outer iteration writes to a slot that the first outer iteration's frames occupy.

**Measurement needed:** compare addresses of `[outer_view1 + 248]` vs `[outer_view2 + 248]` vs any inner element slot addresses from iteration 1. Overlap = the bug.

---

## SCAFFOLD IN TREE (SCRIP `18e65150`)

- `emit.h`: `g_emit.op_body_has_arbno` — 1 when outer ARBNO body contains nested IR_MATCH_ARBNO
- `emit.cpp`: sets it by scanning `g_emit_cfg->all[i0..i1]` in the chain arm dispatch
- `zeta_storage.c`: false WIP geometry-buffer blocks removed (clean)

The scaffold is useful for any fix that needs to gate behavior on nested-ARBNO detection. The template (`bb_match_arbno.cpp`) is unchanged from the pre-WIP baseline.
