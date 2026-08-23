# FINDING: NO-PIN ROOTED GC — slot registry, safepoint veneers, PZ resurrected (it had been dead on EVERY run)

**Seat:** hq_C · **Date:** 2026-08-23 (s263) · **Tree:** SCRIP `c61c5610` + `927d0521` + `1257d56c` (on top of hq_P's `96149604` TABLE rewrite) · RT_OPT=-O0

## Lon's rulings executed (verbatim in substance, in-chat s262/s263)
1. *"all references are supposed to be downstream so that everything is easily slidable. And we should never have in our code a place that depends on that pointer not moving."*
2. *"registries hold (block, offset), never a raw interior address."*
3. *"kick ass GC system. No PINs... Can we get ROOTED versus flat scan somehow? ... ensure that any PIN code is physically deleted. We have no need for pinning anything."*

## THE HEADLINE DISCOVERY: PZ (the rooted, pin-free collect) was DEAD ON EVERY RUN
The s131 PZ design gates on "no registered pins/ranges". `rtcc_gc_register()` (constructor, runs in every process) registers the rtccb register-cache block as pin+range — so **every collect in every program has gone legacy-conservative since rtcc became mandatory** (RT-CONSOLIDATION hardwired `g_rtcc_on=1`). Measured before the fix: pure string churn, every regeneration `(LG)`, `reclaimed 0`, heap ratcheted to 512MB. This is the "slow as a dog" cause. After: every regeneration `(PZ) pinned 0 fill 0`, heap retreats 268MB → 2KB — the SPITBOL shape.

## What landed (three commits)
**1. `c61c5610` — (block, offset) slot registry.** g_gc_cells + g_gc_raws replaced by ONE registry of pointer-slot locations: `gc_slot_reg(loc)` stores `(containing block, offset)` when the slot is in-arena, raw address otherwise (dedup key `loc|1` in the visited set). EVERY pointer slot into a relocatable block is registered and repaired by the slide: `d->s`, `d->tbl`, `d->p`(VCELL), `d->ptr`, `d->arr`, `d->u`, `t->buckets[b]`, `e->key`, `vc->tbl`, `vc->cellp`, `a->data`, `u->fields`. Aggregates (AGGV/AGGP/AGGT/AGGB) slide like any block. Cures hq_P's measured gc-slide-interior-fixup defect (table_variety: right answer then `[ZHP] corrupt title` SIGABRT).

**2. `927d0521` — rooted collection at safepoints.**
- Aggregates left the `nforeign` census → tables no longer force the conservative arm.
- Adaptive high-water `g_hp_gcline` (half of free headroom, recomputed per collect) arms the SEAM, so collection happens at safepoints before exhaustion can force a mid-statement conservative collect. Checked in `rt_gc_point_arr`, zero cost on the allocation fast path.
- rtccb registration marked seam-safe (doesn't disqualify PZ); its 32 slots visited as precise repairable roots under PZ.
- **`rt_gc_point_arr` is now an asm safepoint veneer** (rt_asm_helpers.S): pushes rbx/rbp/r12–r15 above the scan floor, calls `rt_gc_point_arr_c(..., floor)`, pops — so the repairing scan fixes the parked copies and the pops restore REPAIRED callee-saved registers. ⛔ 16-byte alignment pad required (movaps in libc faulted without it — measured, whole stress suite red).
- `gc_zeta_frame` (the DESCR-aware REPAIRING span walker) gained validated recognizer arms for DT_T (arena AGGT payload), DT_N-vcell (arena AGGV payload), DT_A / DT_DATA (WS-island pointer), and under PZ walks the suspended stack from the veneer floor to stack top. The mark worklist drives typed visits of any aggregate it marks.

**3. `1257d56c` — pin code physically deleted.** `HBF_PIN`, `rt_gc_pin_ptr`, `gc_cons_scan`, `gc_cons_scan_t`, the rpin registry + API, pin telemetry, and the setjmp register snapshot are GONE. Everything they pinned is now REPAIR-scanned by `gc_zeta_frame`: registered ranges, WS island, statics blanket, coexpr spill/xmit/stacks, WS/PLJ payloads, and the legacy machine-stack walk (floor-based). `rt_gc_collect` got the same callee-saved veneer, so exhaustion collects repair registers too. The zh bump block moved out of the arena to `rt_slab_region` (an object handing out cursor addresses may not live in a compacting heap); `ZC_ZH_IN_GCHEAP` knob deleted.

## Measured (all pristine, HQ-27)
- Blocking set: corpus m3 357/2, m4 356/2+1SKIP (standing reds only: 160_pat_alt_inner_gen_resume, demo_treebank, 132 SKIP) · beauty self-host 34/34 · emit_no_lang + template_medium rc=0.
- **GC stress suite 15/15 × {plain, S25, S7, S1} × {m3, m4} ALL GREEN** — including 204/213/214, red at stress since s131. STRESS=1 forces a PZ collect at essentially every safepoint with tables, arrays, records, patterns, recursion all sliding, zero pins.
- table_variety: check 381880 in every configuration, incl. SCRIP_HEAP_MB=4; `--zeta=zh` churn rc=0.
- Corpus m3 wall time 10s → 2s in the runner (PZ heap retreat; perf is hq_P's lane — number left here as a breadcrumb, not a claim).

## The register story (why the veneers exist)
At a collect, suspended-side pointers live in three places: (a) memory — repaired via registry/scans; (b) caller-saved registers — spilled to rtccb by the rtcc veneer around every C runtime call, repaired there; (c) callee-saved registers — C prologues spill them at unpredictable depths, some BELOW the collector's frames where no scan may write (registered slots must stay frozen until fixup). The safepoint veneers close (c) by parking all six above the floor. First cut without the veneer: r10 loaded "elem-3-e" (string bytes through a stale cell pointer) — rt_assign_var SIGSEGV, gdb-attributed.

## Accepted stance (pre-existing, now uniform)
The repairing scan REWRITES any word whose value equals a live arena block address — the int-alias risk. This was already gc_zeta_frame's stance for zeta/CAS spans since s131; it now applies wherever pinning used to. A 64-bit integer colliding with a live mmap'd arena address does not occur in SNOBOL4 programs; noted, not feared.

## Routed rungs (open, named, none block SNOBOL4)
1. **Coexpr stack windows still carve from the arena** (`ZC_COEXPR_STACK_GCHEAP=1`): a pthread stack cannot be repaired (hardware RSP). They must migrate to `rt_slab_region` like zh did. Latent for Icon coexpr programs only — and already latent the moment the pin-forwarding arm died (s262); SNOBOL4-FIRST forbids running Icon checks, so this waits for Icon's revival.
2. **PLJ (Prolog) blocks relocate now**; plc interior pointers are repaired only where they sit in scanned/registered locations. Verification forbidden under SNOBOL4-FIRST; rung for Prolog's revival.
3. **rrng ranges store absolute (lo,hi)** — sound now that zh ranges are slab-stable, but a future range INTO an arena block would go stale when it slides; ranges should become (block, offset) if one ever returns to the arena.
4. PZ eligibility still excludes: scan-active, coexpr-live, value-trail, ZBLK/PLJ presence, SCRIP_GC_LEGACY=1. Each exclusion falls to the same repairing-scan LG arm — correct, just not the fast path.
