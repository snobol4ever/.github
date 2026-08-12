# GOAL-SN4-HOME-RBX — RBX = GC heap-top; allocation + GC coverage (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER (Lon s30):** SNOBOL4 addressing is RSP + RBP + **RBX GC-heap-top relative**. Formalize rbx as the allocation frontier (today's DESCR mint pointer), make emitted code allocate inline against it, and make the GC actually see every register-resident and arena-resident root. rbx is callee-saved — the C boundary is free, same property as rbp.

## RUNGS
- [ ] **X-0 · THE CONTRACT, WRITTEN.** Read cold: `REGISTER-LAYOUT.md`, `DESIGN-SN4-REGISTER-PLANES.md`, `gc_heap.c`, the DESCR mint path. Write in THIS file: rbx = frontier invariant, safepoint ports, C-crossing rule, who may move rbx (ONE authority), overflow → island growth path. Zero code.
- [ ] **X-1 · RC-8a — THE GC-SCAN GAP (BLOCKING, inherited from RTCC s16).** `rtcc_gc_register` pins the pointer, scans nothing (`rt_gc_root_pin_add` only; every other block does `rt_gc_root_range_add` too). Add: RTCC block slots + **r12 pending-arena records** (they hold δ/target refs — the s30b obligation (ii)) + rbx frontier semantics to the scan. Latent at HEAD, LIVE the instant the arg tier is claimed.
- [ ] **X-2 · FUNC-11 — INSTRUMENT THE ALLOCATION ITSELF.** ⛔ STANDING INSTRUCTION (three seats, three falsified threshold constants): NO more black-box sweeps. Counter in the runtime path (or core-file technique) → convict the include-scoped capacity for runtime-created variables → fix. Then own the `-INCLUDE` coverage hole (crosscheck has ZERO live `-INCLUDE`; promote the `rtx11_dynvar` probe family with BOARD).
- [ ] **X-3 · INLINE BUMP-ALLOC ARMS.** Hot mint paths go register-only against rbx (M-SLEN precedent: zero C calls), killswitched per family, both media, per-family kill-switch bisectable.
- [ ] **X-4 · ZHP EXHAUSTION CLASS RE-CHECK.** The s29 rc=134 arm (`[ZHP] heap exhausted`) is plausibly LOWER Defect B's mechanism — verify AFTER HOME-LOWER L-2 lands; do not inherit the plausibility as fact.

## GATES (every rung)
RC-8a coverage gate (self-arming, lands WARN→FAIL on tier claim) · probe + bench BY SET vs P0 floors · positive control on every census (a gate that cannot fail for the right reason is not a gate) · FINDING + cursor move.

## ⭐ LIVE CURSOR — UNOPENED (minted s30). X-0/X-1/X-2 are P1-concurrent; X-3 is P2.
