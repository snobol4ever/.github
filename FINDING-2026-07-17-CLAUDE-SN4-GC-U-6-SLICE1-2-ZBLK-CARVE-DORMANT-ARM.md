# FINDING — GC-U-6 slices 1+2 landed; the ZBLK carve seam is proven but DORMANT in emitted code (s88, 2026-07-17, Claude, Lon attending)

**SCRIP `c18794fd`.** Directive: "Implement RBX topped GC heap using MARK/ADJUST/SLIDE technique found in CSNOBOL4 (SIL implementation) and SPITBOL."

## What landed
1. **Slice 1** — the banked `PATCH-2026-07-17-SN4-GC-U-6-SLICE1-WS-MERGE-PARKED.patch` applied verbatim (applies clean at `5284ea95`): `rt_ws_*` re-pointed onto `rt_gcheap_alloc(HB_WS)`; workspace blocks pinned-immortal in the ONE span; the `rt_arena` slab chain retired.
2. **Slice 2** — `rt_zh_bump_slow` (the rbx-guarded `[RT_WS_TOP]/[RT_WS_LIMIT]` refill, REG-4 slice A) carves its windows FROM the collected span: `rt_gcheap_alloc(HB_ZBLK)` under `ZC_ZH_IN_GCHEAP=1` (`zeta_choices.h`; slab arm intact at 0 — the `ZC_HEAP_STRINGS` A/B precedent). `gc_collect_ex` reset pins `HB_ZBLK` beside `HB_WS`: live rbx windows are slide barriers; the REG-4 v0 tail-residue leak becomes bounded pinned blocks inside the walkable, verified span. Reclamation of dead windows = GC-U-7 root registration.

## Canonical consult (RULES mandate)
`silly/arena.c GC_fn` (v311.sil GC line 1367) re-read this session: GCT mark → GCLAD forward addresses (CPYCL advances live-only; MVSGPT = first-dead frontier) → GCBB/GCLAP adjust → slide, frontier drops to CPYCL. `gc_collect_ex` already mirrors this (GC-1/2/3 rung, CSNOBOL4 cross-audit). Invariant preserved by both slices: pure bump between regenerations; pins are barriers; sub-pin gaps → `HB_FILL`.

## Evidence
- **C probe** (runtime-lib link): window carved IN-STREAM (`win − anchor = 48`), title `type=204 size=1048592 flags=TTL`, walk `blocks=2(alloc'd)=2(walked) verify=OK`, `pinned 2` through a forced regeneration, window intact after. (Post-cycle `flags=0` is the collector's normal end-of-cycle clear — pin state is per-cycle, re-established at each reset.)
- **Gates**: smokes sno 7/7×2 AND `SCRIP_ZETA_PORT=7` 7/7×2 · crosscheck EXACT m3 303/4 · m4 293/13/1 · DIVERGE=10, fail-sets IDENTICAL to baseline after slice 1 AND after slice 2 · icon 12/2+10/4 · prolog 3/2×2 unmoved · spot `.s` (arith_loop) byte-identical vs committed artifact ⇒ regen no-op by evidence · 200-col clean on authored lines (pre-existing >200 debt in gc_heap.c/zeta_heap.c noted, untouched).

## ⚠ THE DORMANT-ARM FACT — do not oversell this rung
No live emitter reaches `rt_zh_bump_slow` today. `ZC_PORT` default = FORTH; under the U5 rsp seal, port-7's FR/FRQ residence plumbing is HZ-1's census slice (its own doc says so). A port-7 `--compile` emits the port bake only — no `0x70000010` seed, no refill call, no `HB_ZBLK` in program runs (block counts identical across ports). **"rbx tops the GC heap" is true by construction of the seam, and unexercised by emitted code.** The activation half (HZ-1: which escapee classes emit the heap α under the sealed-rsp world) needs Lon rulings — it intersects the s69 design-of-record drift already flagged in the goal file.

## ⚠ Slice-1 fallout, expected v1
Stress telemetry post-merge: ~600 `HB_WS` pins dominate (`pinned≈620/625`, `reclaimed 0`); dead churn between pins retitles `HB_FILL`, the fill window (`win=192`) serves reuse, bytes plateau ~42KB over 6 forced regenerations — sound, not the 773KB monotone ratchet, but frontier-drop is defeated until GC-U-7 un-pins the workspace.

## Open
Ruling (C) rc=134 gc/2xx routing — untouched, Lon's. HZ-1 rulings before slice 3. GC-U-7 roots.
