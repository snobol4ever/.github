# FINDING 2026-07-14 (Claude) — the RSP obstacle for RUNG ZS, proven under gdb: the MATCH_DEFER frame's lifetime spans γ→β, which a call/ret rsp frame cannot survive

**Context:** session on GOAL-ICON-BB (Lon), redirected to the live cross-language cursor in GOAL-SNOBOL4-BB.md
where RUNG ZS ("all ζ on the stack … except co-expressions/generator procedures → heap") is the head.
Directive: "move toward RSP, free R12; your choice; continue." Baseline proven fresh BEFORE any edit,
byte-identical to the s57 watermark (m3 304/2, m4 303/2/1, DIVERGE=1(1017), smoke 7/7×2). **No code changed.**

## The question answered: is there a problem moving to RSP? YES — and it is the whole point of ZS-2.

### What allocates the 5.5M off-stack frames (gdb-proven, correcting an earlier misattribution)
The ZS-0 gate fails only on `pattern_bt.sno` (`PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd') . W`): ZLS2 pushes=0
(ZS-1 done), but ZLS1 allocs=5,500,011. Telemetry: `allocs=5500011 releases=5500011 live=0 COHERENT`.

- **NOT `rt_proc_call_gen_h`.** A gdb breakpoint on `rt_proc_call_gen_h` running pattern_bt to completion
  **never fired** — that helper (the generator/escapee path) is not called here at all. (An earlier note
  attributed the allocs to it from a grep; the breakpoint disproves that.)
- **It is `MATCH_DEFER`.** A gdb breakpoint on `rt_zls_alloc` shows the caller (frame #1) is JIT-emitted code
  (`??`) under `m3_enter_with_rbx` — i.e. a TEMPLATE emits the `call rt_zls_alloc`. That template is
  `src/templates/bb_match_defer.cpp:43`. The IR confirms: pattern_bt lowers to `MATCH_DEFER [80]` wrapping the
  whole pattern (`MATCH_SEQUENCE → MATCH_ALTERNATE + MATCH_ASSIGN_SAVE + MATCH_SPAN`). 500k iters × sub-pattern
  retries = 5.5M.
- **Therefore `bb_match_defer.cpp` is NOT clean** (an earlier note said it was — that grepped the wrong path
  `src/runtime/rt/bb_match_defer.cpp`, which does not exist; the real file is `src/templates/bb_match_defer.cpp`).
  The cursor's ZS-2 "delete rt_zls from bb_match_defer" is CORRECT and is the real work.

### The RSP obstacle, from the template's own code (bb_match_defer.cpp)
Lifetime, read directly off the box:
- **α (line 43):** `rt_zls_alloc(rt_fn_frame_bytes(fn))` → frame ptr stored in ζ slot `FRQ(dscr()+8)`.
- **α (line 49):** `call rcx` = enter the frozen pattern blob (entry esi=0).
- **γ (line 105):** on match success, control goes to γ **keeping the frame alive** (frame ptr retained in
  the ζ slot).
- **β (line 110-116):** on backtrack from the consumer, β re-enters the **same** frame: `call rcx` with esi=1,
  resuming the blob's interior generator (ARBNO/SPAN) from saved state.
- **release (lines 52-54 and 119-121):** the frame is `rt_zls_release`d only on the FAIL paths (α-fail and
  β-fail → ω). On success it persists for the next β.

**The frame's live range spans γ→β: it must survive being suspended (γ hands control UP to the consumer) and
later resumed (β re-enters it).** Under the current CALL/RET transfer, γ returns up the emitted/C stack to the
consumer, so the box's own rsp frame is destroyed before β runs. That is *why* the frame is allocated
off-stack (`rt_zls` arena): so the pointer stays valid across the suspension. An rsp frame on the box's own
call/ret frame cannot have a γ→β lifetime — this is structural, not incidental.

**Corollary compounding constraint (same file, lines 65-69, the box's own comment):** an emitted BB→BB
transfer preserves only the frame register, so the box must hand-save **r13/r14/r15** across the transfer
(`x86_xfer_enter/leave`). An rsp-frame model needs a home for those spills too — one of the three ZB-OWN-1a
blockers (xfer_enter/leave → ζ grant under RSP).

### What this means for RSP
- The `MATCH_DEFER` frame is a **transient** (LIFO, released within the enclosing match — `live=0 COHERENT`),
  so it IS rsp-eligible in principle — it does NOT belong to the heap/escapee carve-out.
- But it can only move to rsp via **jmp-topology**: the box must NOT `ret` at γ; it must `jmp` to the consumer,
  leaving its frame in place on ONE shared rsp stream that unwinds only at ω. That is the ZB-PORTS → ZB-ACT-0
  jmp-entry rung (GOAL-IR-IMMUTABLE-EMIT §ZB-ACT). **Moving the storage to rsp REQUIRES changing the transfer.**
- This is the same wall as the Icon FRONTIER-DISPLACEMENT measurement (`every write(1 to 5)` hangs when a
  counter cell is re-accessed after rsp is displaced by a consumer round-trip) and the reason the s28
  `ZC_FRAME_RSP` ablation regressed to m3 174/118, m4 5/286 — a naive rsp flip breaks exactly these γ→β
  suspended-frame lifetimes.

### Secondary finding: the ZS-0 gate can't distinguish the two destinations
The directive is two-destination (rsp for transient activation ζ; heap for co-expr/generator escapees). The
ZS-0 gate asserts `ZLS1 allocs == 0`, which for pattern_bt is a **transient** that SHOULD go to rsp (via ZS-2),
not a heap escapee. So here the strict gate is measuring real ZS-2 debt (good) — but the gate cannot tell a
transient-owed-to-rsp from a lawful heap escapee; when the escapee path (`rt_proc_call_gen_h`) is exercised by
some other program it will also trip the same counter, and that one is NOT ZS-2 debt. The gate predicate
should attribute each residual ZLS1 alloc to its site (MATCH_DEFER = ZS-2 debt; rt_proc_call_gen_h = heap goal;
rt_zcol grow = by-law exclusion) rather than counting them all as one failure.

## R12 status (the ultimate goal), unchanged and honest
Not unblocked by anything here. `x86_align_save()` (x86_asm.h:280) still returns **rbp** when the frame reg is
r12, so r12 AND rbp are both still in use. Freeing R12 is the `ZC_FRAME_RSP` flip (ZB-OWN-1a: align_enter/leave
no-ops under RSP + 16-align audit; xfer_enter/leave spilling r13/r14/r15 to a ζ grant under RSP) — a separate
ladder, gated independently. RUNG ZS is a *precondition* (no static r12 frame once all ζ is stack-or-heap),
not the flip.

## Bottom line
The problem with moving to RSP is real and structural: **suspendable boxes (MATCH_DEFER, and the same shape for
ARBNO and every generator) have frames whose lifetime spans γ→β, and a call/ret rsp frame is destroyed at γ.**
The fix is jmp-topology (never ret at γ), which is ZS-2 / ZB-ACT-0 — a transfer change, not a storage swap.
The pattern_bt 5.5M allocs are the concrete, measurable manifestation and the ZS-2 acceptance workload.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

---
## ZS-2 IMPLEMENTATION ATTEMPTED — the RSP conversion is mostly mechanical; ONE entanglement blocks a clean landing

**Lon correction (this session):** co-expressions + generator-procedures are ON HOLD (language crippled there
until the unified GC heap) — so NO heap needed now; and the γ→β generator lifetime WORKS under RSP (jmp /
stable-frame model, as ARB proves; `every write(1 to 5)` is a case that works, NOT the wall I'd feared). So
DEFER's transient frame moves to rsp by the ARB idiom: `sub rsp` at α, keep rsp across γ, restore at ω. No
redesign.

**The conversion (built, then reverted — see BLOCKER):**
1. `zeta_storage.c` IR_MATCH_DEFER: add a 3rd 8-byte field `+16` "saved rsp" (return 1 → return 2).
2. `x86_asm.h`: add `x86_rep_stosb()` = `MEDIUM_BINARY ? x86_Lrec(x86_b2(0xF3,0xAA)) : " rep stosb\n"` (mirrors
   `x86_cqo`), wire `if(!strcmp(mnem,"rep_stosb")) return x86_rep_stosb();` beside `cqo`. Byte-verified vs `as`
   (`f3 aa`). NOTE `shr`/`rep_stosq` are NOT encoders; `rep stosb` (byte count in rcx) avoids needing `shr`.
3. `bb_match_defer.cpp` α (the fn-non-null blob path only): replace
   `mov rdi,FRQ(dscr()); call rt_fn_frame_bytes; mov rdi,rax; call rt_zls_alloc; mov FRQ(dscr()+8),rax`
   with: `call rt_fn_frame_bytes` → `add rax,15; and rax,-16; mov FRQ(dscr()+16),rsp; sub rsp,rax;
   mov FRQ(dscr()+8),rsp; mov rcx,rax; mov rdi,rsp; xor eax,eax; rep_stosb; mov rax,FRQ(dscr()+8)`. (rt_zls_alloc
   zeroed via ZC_INIT_ZERO, so the frame MUST still be zeroed — hence rep_stosb.)
4. Both `rt_zls_release` sites (α-fail ~line 54, β-fail ~line 121): replace
   `mov rdi,FRQ(dscr()+8); align_enter; call rt_zls_release; align_leave` with `mov rsp,FRQ(dscr()+16)`.

**⛔ THE BLOCKER (why it was reverted, not landed — found by auditing all exits):** `bb_match_defer.cpp` has
TWO regimes sharing the box:
- **Blob path** (fn non-null): allocates the frame, `call rcx` (the compiled DT_P blob). This is what the rsp
  sub/restore is for.
- **Callout pump** (fn NULL → `jz L0`, lines 65-126): `rt_defer_open/step/close` — a DIFFERENT mechanism that
  does NOT use the blob frame and NEVER sub'd rsp.

Both regimes fall through to the SAME β/ω tail. The β-fail restore `mov rsp, FRQ(dscr()+16)` fires on BOTH —
but on the callout path `dscr()+16` was never written, so it restores rsp to GARBAGE → crash. The original
`rt_zls_release(FRQ(dscr()+8))` was safe on both because the `dscr()` fn-slot (0 on the callout/exhausted path)
gates the β re-enter (`test rcx; jz ω`, line 115-117) and release of a 0/again-0 slot was harmless.

**THE FIX (next session, small):** guard the rsp-restore on "took the blob path." The `dscr()` slot already IS
that indicator (non-zero fn ⇒ blob path ⇒ frame on rsp; zero ⇒ callout/exhausted ⇒ no frame). So at each of the
two release sites, restore rsp ONLY when the frame was allocated. Cleanest: keep the frame-base slot `dscr()+8`
as the guard — `mov rcx,FRQ(dscr()+8); test rcx,rcx; jz <skip>; mov rsp,FRQ(dscr()+16); <skip>:` — OR (simpler)
init `FRQ(dscr()+16)=rsp` at α on the callout path too (a no-op restore), so the unconditional restore is
always valid. The second is one extra `mov FRQ(dscr()+16),rsp` on the L0 entry and removes all branching. Then
verify: pattern_bt `result: 500000` + ZLS1 allocs 5.5M→0; full crosscheck watermark-identical (m3 304/2, m4
303/2/1); the recursive-DEFER T2 case (`"(12,(34)"`) — the acceptance test — either fixed or classified.

**Status this session:** conversion designed + built + audited to the blocker, then REVERTED to the proven
baseline `a1be6083` (tree byte-identical, rebuilds green). Not landed because a knowingly-half-correct frame
edit is worse than a clean baseline + this exact plan. The rep_stosb encoder + the ARB-idiom α/ω edits are
correct and ready; only the two release sites need the one-line callout-path guard above.
