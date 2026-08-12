# GOAL-SN4-HOME-WIRES — r10/r11 wires, two glue kinds, shim deletion (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** rΓ=r10 · rΩ=r11 product-wide (Lon s12 verbatim: *"remove the stupid PROC shim around patterns and use proper PASS-THRU glue using R10 and R11"*), exactly TWO glue kinds (ONE-SHOT · PASS-THRU; FRAMED IS NOT A GLUE KIND — s29), RBP never written by glue. **Mechanism authority = LADDER WREG + LADDER PT inside `GOAL-RBP-EARN.md` (absorbed by reference, corrections here supersede).** RTCC's wire half (veneer preservation) is owned HERE per the s14 arbitration: safe config = RTCC-ON **and** wire capture/restore, neither alone.

## RUNGS
- [ ] **W-0 · CLAIM SWEEP, HONEST.** r10/r11 usage census across templates + emit.cpp + **RTX hand asm + raw-byte encoders** (grep is insufficient — objdump the emitted slab too). With BOARD: claim gate becomes data-driven {rbx r9 r10 r11 r12 …} + `--strict` (today: r9-only, informational — a hole MECH documented).
- [ ] **W-1 · ZCTX SCRATCH ERADICATION.** All six ZCTX sequences use r10/r11 as scratch (s37 measured) — re-allocate BEFORE any flip; live-on-arrival landmine otherwise.
- [ ] **W-2 · PUSH/POP GUARD UNIFICATION (MECH s37(B), the sole D12/D13 regression pair).** push guard `flat_jmp_entry` (emit.cpp:2373) vs pop guard `!_wire_stub && flat_jmp_entry && flat_pat` (:2806): any graph outside the intersection pushes and never pops = POP DEBT. ⛔ ONE predicate, both media — never a compensating pop on one exit (two-calculators disease). If the CLASS-O/`_wire_stub` design call is still ambiguous after the census, route both arms to Lon.
- [ ] **W-3 · WREG MECHANISM, DORMANT.** Site glue `lea r10,[rip+site_γ]` · `lea r11,[rip+site_ω]` · `jmp <first interior box>`; exits `jmp r10`/`jmp r11`. Killswitched; default emission byte-identical to HEAD. r10/r11 are caller-saved ⇒ saves are TEMPLATE-EMITTED per-activation on the spine, never an implicit choke (s18 RSP-SAFETY + the stack-arg witness).
- [ ] **W-4 · ARENA WIRE-PAIR SLOT (+16B) — THIS SEAT OWNS THE LAYOUT.** Blob-interior pending records capture {r10,r11} at push, restore at β, or it is `g_blob_ctx`'s single-cell defect in register clothing (the LAW). RBP/EARN-5 consumes this layout — one authority.
- [ ] **W-5 · ⛔ THE FLIP — REQUIRES EARN-1 + EARN-3 LANDED (EARN-10 ordering).** PROC-shim deletion (PT-1..3), CLASS-D exit ceremony dies with it. The old WREG residual (19 SEGV + 7 HANG) was MISSING FRAMES, not glue defects — EXPECTED cured by EARN; measure by set, never assume.
- [ ] **W-6 · RTCC RE-ENTRANT PRESERVATION + DEFAULT-ON REVALIDATION.** The veneer round-trips wires on leaf crossings only; fix the re-entrant case; then RTCC default-ON must hold the P0 floors with NO `SCRIP_RTCC=0` escape (kills the m4-130 class). Belt-and-suspenders: `-Wl,-z,now` for the r11 lazy-binding clobber.

## GATES (every rung)
claim gate `--strict` green · probe + crosscheck BY SET vs P0 floors both modes, RTCC ON and OFF until W-6 seals · killswitch md5 discipline · FINDING + cursor move.

## ⭐ LIVE CURSOR — UNOPENED (minted s30; s32 fire-and-forget). W-0..W-4 runnable NOW. ⛔ W-5 REQUIRES (predicate — CHECK, never wait): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND an EARN-3 anchor landing on origin (RBP cursor line `UNBLOCKS: WIRES W-5`); FALSE ⇒ skip to W-6's RTCC half or pull from the master POOL.
