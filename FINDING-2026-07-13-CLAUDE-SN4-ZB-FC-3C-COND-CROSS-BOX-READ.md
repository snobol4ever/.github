# FINDING — ZB-FC-3c: COND is NOT SAVE. The capture's read is a CROSS-BOX rsp read across the whole inner subtree, and the s44 landing plan has no slot for it.

**Session:** s47 · 2026-07-13 · Claude
**Status:** RECON ONLY — zero capture code moved. Watermark re-proven first (m3 302/4, m4 301/3/2, DIVERGE=1/1017, identical failing sets; sno 7/7×2).
**Rung:** `GOAL-SNOBOL4-BB.md` → ZB-FC-3c — CAPTURES (ASSIGN_SAVE/COND)
**Supersedes:** the LANDING PLAN in `FINDING-2026-07-13-CLAUDE-SN4-ZB-FC-3C-CAPTURE-SPINE.md` (s44). F1/F2/F3's *diagnosis* stands; F3's *mapping table* and the 5-step plan do not.

**This is the 9th consecutive session in which the PLAN, not the code, was the defective part.** The pattern is now so reliable it should be treated as a law of this codebase: re-derive before coding, every time, without exception.

---

## What s44 got right, and keep

- **F1 ✅** commit walk is linear left-to-right (`rt_dcap_pump`). Re-verified. Build no ordering machinery.
- **F2 ✅** the pend ring holds `(varname, Σ+saved_delta, len)` — never a pointer into the ζ frame. Still true after s46's rbp-dcap rewrite (entry is now `{varname@0, saved_delta@8, len@16}` at `[rbp]`, still by-value). **No dangling-pointer hazard. 3c is de-risked.**
- **F3 ✅ (diagnosis)** SAVE's 16B grant is a *container* — `{uint32_t *buf; uint32_t gen; uint32_t sp;}`, a heap-backed growable LIFO of integer δs, i.e. **a software stack simulating the stack rsp already is.** Killing it is the right goal, and it removes a live `rt_ws_alloc` site (pays into the TR/GC ledger).
- **F4 ✅** ARBNO is Tier-D and moves rsp per iteration ⇒ a fence is required ⇒ this is not a one-line `fc_geom` grant. Correct, but **the fence is stated in only one of its two directions** (see C3).

## What s44 got wrong

**F3's mapping table row `rt_cap_top` → "read own cell" is false.** COND is a **different IR node** from SAVE. It has no ζ grant of its own; it reaches SAVE's state through an **operand edge**. Under the flat frame that is free. Under the FORTH spine it is not.

---

## C1 — MEASURED: COND addresses SAVE's slot through the FLAT FRAME (r12), and it does so from a different box

Topology, from `lower_snobol4.c:1008-1020` (`TT_CAPT_COND_ASGN`):

```
SAVE = capture ENTRY (returned).  SAVE.α pushes δ;  SAVE.γ → inner entry;  SAVE.β pops;  SAVE.ω → fail
  └── inner pattern subtree   (lowered with γ → COND, fail → SAVE)
COND = capture TAIL.           COND.α reads top-of-stack δ, records the pend;  COND.γ → succ
ir_operand_push(nd, save);   /* [1] SAVE → COND.op_off = SAVE's slot */
```

`emit.cpp:1080-1092` turns that operand edge into the address:

```c
case IR_MATCH_ASSIGN_COND: { IR_t *box = nd->operands[1];
    g_emit.op_off = box ? drive_value_slot(box) : -1; g_emit.op_phase = 1; }   /* SAVE's slot */
case IR_MATCH_ASSIGN_SAVE: {
    g_emit.op_off = drive_value_slot(nd);             g_emit.op_phase = 0; }   /* its own slot */
```

**Live compiler output** (`SCRIP_ZETA_PORT=6 scrip --compile`, subject `S ? LEN(1) ('b' LEN(1)) . V 'd'`) — the two boxes, verbatim:

```
 xchain0_n12_α:                 ; SAVE
 lea rdi, [r12 + 416]           ;   <-- SAVE's slot, FLAT FRAME
 mov esi, r14d
 call rt_cap_push@PLT
 jmp xchain0_n16_α              ;   → inner subtree
 ...
# IR_MATCH_CAPTURE_COND
 xchain0_n13_α:                 ; COND — a DIFFERENT BOX, after the inner subtree has run
 lea rdi, [r12 + 416]           ;   <-- THE SAME OFFSET 416. Cross-box read via the flat frame.
 call rt_cap_top@PLT
```

⇒ **The flat frame is what makes today's cross-box read free.** ZB-FC-3c's whole premise is deleting SAVE's flat slot. **The instant SAVE's δ moves to an rsp cell, COND has nowhere to read it from.** The s44 plan's step 3 ("COND-yield reads the own cell") does not typecheck: COND has no own cell, and never had one.

## C2 — THE ACTUAL SHAPE: COND reads `[rsp + fp(inner)]`, and the mechanism ALREADY EXISTS (ALT's, proven)

By the FORTH law (ARCH-ZETA §10c, ratified by ZB-FC-3b): **cells pop at ω, not at γ** — a box yielding at γ keeps its cell live so β can resume it. Therefore at **COND.α**, the entire inner subtree's cells are **still on the stack**:

```
rsp at SAVE.α entry              = F
rsp after SAVE pushes its cell   = F − 16
rsp at COND.α (inner all live)   = F − 16 − fp(inner)
⇒ SAVE's cell, seen from COND    = [rsp + fp(inner)]          ← a STATIC displacement
```

**This is not a new mechanism. It is exactly ALTERNATE's, already landed.** `bb_match_alternate.cpp:69` reads its own cell across its arms' padded footprint:

```c
IF(afc(), x86("mov", "eax", rspd((int)_.op_fc_fpmax + 4)))     /* rsp-relative, static fpmax */
```

and the footprint is computed at LOWER time by summing `fc_geom` over the subtree's node range (`lower_snobol4.c:1147-1167`) and handed over by a registrar side-table (`fc_alt_register(A, na, fc_fp)` — the PEERS RULE forbids IR_t fields).

⇒ **3c needs the same two things ALT needed, not the one thing s44 listed:**
1. `fc_save_register(save)` — SAVE is eligible for a cell (the s44 plan has this), **and**
2. **`fc_cond_register(cond, fp_inner)` — the DISPLACEMENT, plumbed to COND as an `op_fc_*` field so its read becomes `rspd(fp_inner)`.** *(s44 has no step for this at all.)*

Good news, and it is why this stays mechanical: **both the summing loop and the registrar/`op_fc_*` plumbing exist and are proven by ALT and SEQ.** This is a reuse, not an invention. But it is a second registrar and a new emit field — **budget it, it is not in the s44 plan.**

## C3 — THE FENCE IS TWO-DIRECTIONAL, AND s44 STATES ONLY ONE DIRECTION (this is the ZB-FC-3b bug, exactly)

s44/F4: *"A SAVE inside an ARBNO body must decline."* True — ARBNO moves rsp per iteration, breaking the port invariant under the capture.

**But the displacement in C2 is only static if NOTHING BETWEEN SAVE.α AND COND.α MOVES rsp DYNAMICALLY** — and the inner subtree sits precisely there. So the *other* direction fences too:

> **An ARBNO (or any Tier-D / dynamic-rsp box) INSIDE the capture's inner pattern also breaks 3c** — `fp(inner)` is then not a static number, and COND's `rspd(fp_inner)` reads garbage.

**This is the identical mistake ZB-FC-3b already made once and got caught on**, in its own words: *"My whitelist declined a SEQ that **contains** ARBNO but not one **contained by** it."* The rung is about to repeat it in the mirror. Both directions must decline.

Further, LOWER's own comment at `:1148` warns the same thing for the sum itself: *"a granted nested ALT's yield fp is 16+FPMAX_inner, not the range sum — range-sum is exact ONLY for linear spines."* ⇒ **v1 fence: register the capture only if the inner subtree is fc-LINEAR** (reuse the existing `fc_linear` predicate from the ALT arm loop verbatim — do not re-invent it). A non-linear or ARBNO-bearing inner **declines and keeps the array path** (degrade, never die — the ladder's standing rule).

## C4 — COUPLING: s44's "no ALT edit owed" is CONFIRMED, and it is load-bearing

`lower_snobol4.c:1154` calls `fc_geom(x,&fck)` **before** the zero-cell whitelist at :1156-1159 (which today lists `IR_MATCH_ASSIGN_SAVE/_COND/_IMM`). So the moment SAVE is granted, `fc_geom` catches it at :1154 and **ALT's pad-to-max `fp_i` picks up the +16 automatically**; `fc_alt_fpmax` stays exact with no ALT edit. ✅ Verified in source this session. **COND/IMM must STAY zero-cell in that whitelist** (they get a displacement, not a cell) — if someone "helpfully" grants them one too, every enclosing ALT's fpmax silently inflates.

## C5 — IMM rides along for free

`IR_MATCH_ASSIGN_IMM` (`$`) has the **identical topology** — same `ir_operand_push(nd, save)`, same `rt_cap_top` read (`bb_match_capture.cpp:72`), differing only in `op_phase` 2 vs 1 (`lower_snobol4.c:1022-1043`). Whatever displacement COND gets, IMM takes unchanged. One mechanism, two phases. Do not build it twice.

---

## CORRECTED LANDING PLAN (supersedes s44's 5 steps)

1. **`fc_save_register` + `fc_cond_register(nd, fp_inner)`** in `zeta_storage.c`, beside `fc_seq_register`/`fc_alt_register` (side tables keyed by node ptr — PEERS RULE).
2. **LOWER (`TT_CAPT_COND_ASGN` / `TT_CAPT_IMMED_ASGN`)**: after lowering the inner (`before_i .. g->n`), reuse the ALT arm loop's summing + `fc_linear` predicate **verbatim** to compute `fp_inner` and decide eligibility. Decline if non-linear, if the inner bears an ARBNO, **or if the capture itself sits inside an ARBNO body** (ZB-FC-3b's existing `sno_in_arbno` counter — find it, do not re-invent). Register both nodes only on success.
3. **`fc_geom`**: `IR_MATCH_ASSIGN_SAVE && fc_save_registered(nd)` → `*k = 16`. COND/IMM stay zero-cell (C4).
4. **emit**: plumb `fp_inner` onto COND/IMM as an `op_fc_*` field (the `op_fc_fpmax` precedent).
5. **`bb_match_capture.cpp`**, granted path only: SAVE.α → store δ into its own cell (drop `rt_cap_push`, drop its align window); SAVE.β → **emits nothing** (ω's pop is the release, FORTH law S10b); COND/IMM.α → `mov eax, rspd(fp_inner)` (drop `rt_cap_top`, drop its align window). **Ungranted → today's array path verbatim.**
6. **GATE (the bar, non-negotiable):** crosscheck watermark-exact in **both flavors** (default CSTACK **and** `SCRIP_ZETA_PORT=6`) × **both media**; **155–160 + `166_pat_arbno_cond_assign_commit`** are the named capture tests; sno 7/7×2; icon/prolog/raku unchanged; `.s` regen (codegen touched).
7. **Only after ZB-ITER** lifts the ARBNO fence and every SAVE is granted may `rt_cap_push/pop/top` + `buf` + `gen` be **deleted outright** and the `rt_ws_alloc` site counted into the TR/GC ledger. Until then both paths coexist.

## Standing corrections to the rung text

- **DELETE** F3's table row *"`rt_cap_top` at COND yield → read own cell"* — COND has no own cell (C1).
- **ADD** the displacement registrar + `op_fc_*` field as a first-class step (C2). It is ALT's proven mechanism, but it is *a second registrar*, and the s44 plan does not mention it.
- **WIDEN** the fence to both directions: ARBNO *under* the capture fences it just as ARBNO *over* it does (C3).
- **KEEP** "no ALT edit owed" — verified — and add the warning that COND/IMM must remain zero-cell (C4).
- **NOTE** IMM is the same mechanism at phase 2; build once (C5).
