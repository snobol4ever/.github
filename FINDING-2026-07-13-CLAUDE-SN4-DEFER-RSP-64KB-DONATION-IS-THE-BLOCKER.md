# FINDING — DEFER-to-rsp: ATTEMPTED s50, REVERTED; the 64KB DONATION is the defective part, not the rsp direction (2026-07-13, Claude, under Lon's s50 all-stack ruling — ARCH-ZETA §14)

## What was tried (template-only, three sites in `bb_match_defer.cpp`)
Under `x86_port_cstack()` (default CSTACK=4 + FORTH=6): α's `rt_zls_alloc(65536)` → `sub rsp,65536; mov rax,rsp`; both ω release arms' `rt_zls_release` → `add rsp,65536`. Legacy ports (plain/instrumented/alloc/inline) kept the zls arm. Encoders verified pre-build (`x86_sub("rsp",imm)` is the fc hook's own proven shape, x86_asm.h:1459; register-direct ModRM needs no SIB).

## What happened (measured)
- Oracle probe (suspension + β re-entry + stacked LIFO defers: `*P 'b'` with `P=ARB . V`, `'ab' *Q`, `R = *P *Q`) — **m3 == oracle exactly.** Emitted m4 asm inspected: sub/add pairs correct, statement bracket restores at both match exits.
- **Full crosscheck: TWO NEW REDS, both modes — 139_pat_calc_paren_deep and 150_pat_star_var_fence_alts_no_arbno, both SEGV.** Reverted; watermark re-proven exact (m3 302/4 · m4 301/3/2 · DIVERGE=1/1017, identical sets).

## Root cause (the mechanism, derived from the failures)
139 is recursive `*expr` with combinatorial alternation backtracking. **The known SZ-2c transit violation** (JOIN's alternative-switch bypasses interior boxes' β/ω — GOAL-SNOBOL4-BB Phase 2) means an abandoned alternative's suspended DEFER never runs its `add rsp` — reclaim waits for the statement bracket. On the 1GB zls arena that leak-per-abandoned-alternative was invisible; **at 64KB per activation on an 8MB C stack it overflows MID-MATCH, before the bracket can fire.** 150 (fence alternations over `*VAR`) is the same class.

## The verdict — Lon's ruling STANDS; the plan was the defective part (12th occurrence of the pattern)
DEFER **is** just a new activation and rsp **is** the right home. The blocker is that the template donates a **worst-case 64KB** because `rt_defer_get_pat_fn` returns only the fn, not the frame size — while the proc table KNOWS the real frame_bytes (the probe's own emitted startup: `rt_proc_set_frame_bytes("PAT$0", 128)`). At real size (~128B–few KB), thousands of leaked-until-bracket activations are noise. **The 64KB guess was also pure waste on the zls path** — this fix pays either way.

## The correct landing (next session, mechanical)
1. **FZ-5b inlined-head path first** (`_.bb_child_fn` known at emit time): promote the child's frame_bytes through g_emit (a scalar promotion at the dispatch point, per the g_emit-only FACT RULE) and sub the exact static amount. Zero runtime API change.
2. **Generic path:** companion leaf `rt_defer_get_pat_fbytes` (or have get_pat_fn return bytes via a second register/out-slot per the NCB-1b idiom); dynamic `sub rsp,reg` + save pre-sub rsp in the quad for the release (`mov rsp, saved` — handles dynamic size trivially). ⚠ Check the DEFER zls quad has a third 8B slot or widen the grant IN LOWER (never patch in emit — the standing landmine).
3. ⚠ COORDINATE: NCB-2/SZ-1 rewrite this same template (the standing note). ⚠ SZ-2c's transit fix independently shrinks the leak class to zero.
4. Gate: the s50 probe (kept at /tmp/probe/defer1.sno — re-derive, don't trust) + 139/150/143/145/165 + full crosscheck both modes.

## Free co-finding: ARB is ALREADY on rsp in the default build
The probe's emitted asm shows IR_MATCH_ARB under CSTACK doing `sub rsp,16` + chain-link push at β-extension, popped `lea rsp,[rax+16]` at exhaust — **ARB's per-activation blocks already live on the C stack today.** The s41 census's "Tier D → heap" label for ARB was mislabeling working stack code (§14 records the reclassification). ARB's residual work is fc-cell conversion under FORTH (drop the `[r12+88]` chain-head indirection — at β, rsp IS the cell), not a rescue.
