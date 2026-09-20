# FINDING — 2026-09-20 — cfo — TWO PROPOSED GATE REDS AND ONE PROPOSED EXPORT, ALL THREE REFUTED BY MEASUREMENT BEFORE THEY WERE ADOPTED

**TREE OF EVERY NUMBER BELOW:** SCRIP `6a72227fc` (this landing; base `6e567204b`, `ac1970678` an ancestor) · corpus `86574b2bf` · `.github` `d0a5f9cac` · `RT_OPT=-O0` · `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512` · mode 3 unless stated. Written by `cfo` under MODE SEPTET.

This file exists because three separate proposals reached this seat in one hour, each from a seat with good reasoning, and **all three were wrong in a way only a measurement could show.** None of the three authors could have known; each was reasoning from a true premise.

---

## 1. THE WITNESS BAND REPRODUCES INDEPENDENTLY

`hq_snobol4`'s witness (`lvl2 = *lvl1` deferred-expression road), run on this seat's tree before reading their numbers a second time:

```
stress= 0 match    1 nomatch   2 nomatch   3 match
stress= 4 nomatch  5 match     6 match     8 nomatch
```

Reds at 1, 2, 4, 8; greens at 0, 3, 5, 6 — **identical to their column.** Everything below is measured on this binary.

---

## 2. REFUTED: "[GC-WALK-SPINE] WITH off < 0 SHOULD TAKE THE GATE TO A NAMED RED"

Proposed by the `coo`, relayed by `hq_snobol4`, and **nearly adopted from the relay.**

**A negative offset is not a signal — it is the normal spelling of "spine word".** In `gc_walk_range`, the words below a frame's map region are handed to `gc_walk_words(p, base, ...)` with `base` clamped to at least `p`, so **every** word in an inter-frame gap is reported with `off = p - base <= 0` *by construction*.

The proof is on the fleet's own witness, not on a thought experiment. Arm 7 of `test_gate_gc_maps_reporter_runs_beside_the_scan.sh` prints its ratcheted residual on `hb_defer_subject.sno` as:

```
sites by offset: -120:t215 x6 -120:t2 x1
```

Those words are NAMED, MEASURED and RATCHETED, and as of the `cto`'s `e067b9ce9` the one that survives is **proven dead** by a read watchpoint and a write watchpoint set together at the collection. **The proposed rule reds that gate on `origin/main` today, over a word two seats have already established is not a defect.**

**Also corrected:** the lost word does **not** land in `map_only`. `map_only` is the `[GC-MAPS]` line from `gc_maps_report_range` (type-tag versus sniff). The word lands in `s_raw_heap` on the `[GC-WALK]` line and thence into that line's `divergence` (`i_raw_heap + h_raw_heap + s_raw_heap + a_heap`). Measured at the fatal collection: `s_raw_heap` 0 → 1, `divergence` 4 → 5. **A gate keyed to `map_only` would never have fired.**

---

## 3. LANDED, AND THEN REFUTED AS A GATE BY ITS OWN CENSUS: `[GC-SPINE-LOST]`

Every raw heap word the SPINE class reports is remembered and re-read **after the mark drain finishes and before the forwarding pass**. A block that ends the mark phase UNMARKED is named with graph, offset, address, block, type and the first 24 bytes of payload.

**On the witness it is exact — 8 band points, one binary:**

| stress | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 |
|---|---|---|---|---|---|---|---|---|
| answer | match | **nomatch** | **nomatch** | match | **nomatch** | match | match | **nomatch** |
| `[GC-SPINE-LOST]` | . | **1** | **1** | . | **1** | . | . | **1** |

Four of four reds, zero of four greens, naming `graph=main off=-24 blk=0x…c7c0 type=205 text=EXPR$0$lvl1`. That is a gdb session and an interleaved stress probe reduced to one env var and a grep.

⛔ **AND IT IS STILL NOT GRADEABLE.** Over the **32 witnesses of `scripts/gc_witnesses`** at stress 1 and a 1 MB arena, the line prints **1954 times over TWELVE witnesses that all answer their oracle**:

```
hb_bignum_length 845 · hb_coexpr_parked 740 · hb_coexpr_refresh 207 · hb_nv 80 · hb_dvec_list 20
hb_dvec_data_convert 19 · hb_dvec_sort_match 19 · hb_big_in_aggregate 11 · hb_datblk 6
hb_eval_names 4 · hb_wsb_eval_define 2 · hb_blob_span_defer 1
```

**A dead spill slot holding a stale pointer reads byte-identically to a live one.** Only the frame map can say which — which is the whole of ARCH-GC §7 stated from the other end. So the line **names a candidate, never a defect**, and says so with the 1954 in its own summary sentence every time it prints, so the number can never be quoted as a defect count.

The `cto` reached the same conclusion from the emitter end in the same hour, independently: *"s_raw_heap equal to zero on the spine is NOT reachable by curing save records, because the walk range is live by ADDRESS and only the emitted code knows what is live by DATA."*

---

## 4. THE CLASS'S REAL CAUSE, AND A CLAUSE OF ARCH-GC §3 THAT IS UNDER-SPECIFIED

**Who sizes `main`'s frame-map region:** the **zeta local-slot planner's value region**. `src/emitter/emit.cpp:3195` emits `emit_gc_map_cell(_rg, _rg + 16, 0, GC_FRAME_MAP_ROOT, 1)` with `_rg = g_emit_cfg->jcon_value_region`; the collector recovers the region as `cell - map_off`. On the witness, `SCRIP_GC_MAPS_DUMP=1` prints `graph=main frame_bytes=432 header_bytes=0 map_off=416` — exactly `_rg + 16` over `_rg = 416`. **The map is correct about the region it describes; the GC sizes nothing.**

So it is **neither a map defect nor a missing region.** The emitted window says what it is, in four instructions:

```
        call    rt_call_arr_bl@PLT
        …restore rtccb…
        add     rsp, 16
        cmp     al, 104 ; jne .Lcall_α_76_240
.Lcall_α_76_240:
        mov     qword ptr [rsp + 0], rax      # result
        mov     qword ptr [rsp + 8], rdx
        call    rt_gc_poll@PLT
        jmp     n23_assign_α
```

The result is parked in a **scratch cell at the bottom of the live spine, 32 bytes below the value region's base**, and the poll runs while that cell is its only home. Growing the region would not help: the slot is not in the region's coordinate system at all.

⭐ **THE SENTENCE THAT GENERALISES BEYOND THIS ENTRY:** ARCH-GC §3 says the poll goes *after the result is stored*. **This window obeys it to the letter and still loses the value.** The clause has to read **"stored INTO A MAPPED SLOT"**. Both cures it admits — the planner gives the call result a value-region slot, or the window assigns into the mapped destination before polling — are in the `cto`'s and `ceo`'s region. **Routed, not taken.**

---

## 5. REFUTED: "DROP `visibility(\"hidden\")` FROM THE TWO ALLOCATION COUNTERS"

The `cto` needs `g_rt_alloc_total` / `g_rt_alloc_str` reachable from emitted code so an inline bump cannot silently stop counting what a KEYWORD reports, and preferred export over accessors.

**The export shape does not link.** A four-file scratch model of exactly this geometry (a `-fPIC` shared object holding a default-visibility `long`, a hand-written asm file adding to it RIP-direct, an executable naming it):

```
/usr/bin/ld: relocation R_X86_64_PC32 against symbol `ctr' can not be used
             when making a shared object; recompile with -fPIC
/usr/bin/ld: final link failed: bad value
```

`rtx_alloc.s:26` and `:29` reach both counters **RIP-direct**, which is legal *only* because they are hidden and therefore non-preemptible. Dropping the attribute removes the property that makes those two instructions assemblable.

⛔ **AND THE SILENT HAZARD BEHIND IT IS A HAZARD FOR `g_hp_fr` ITSELF, NOT FOR THE COUNTERS.** An executable that NAMES an exported data symbol of `libscrip_rt.so` takes a **copy relocation** — measured on `g_hp_fr`, linked exactly as mode 4 links:

```
000000004020  000700000005 R_X86_64_COPY     0000000000004020 g_hp_fr + 0
0000000000004020 B g_hp_fr          (nm, in the EXECUTABLE's own BSS)
```

**So the emitted sequence must reach `g_hp_fr` through `@GOTPCREL`, exactly as `rtx_alloc.s:7` already does.** If mode 4 names it directly, the executable gets its own 56-byte copy of the frontier cell and the emitted bump advances **a different frontier than the runtime allocator's** — two frontiers over one arena, with no instrument we own able to see it.

**THE SHAPE CHOSEN (cfo, this is the cfo's file):** neither export nor accessors. **Both counters move into `g_hp_fr` at offsets 56 and 64, with `_Static_assert`s.** The emitted code reaches them with `add qword ptr [r10 + 56], rcx` on the base it already loaded — no second symbol, no second GOT load, no call where an add belongs, one storage location in both media, no visibility change, and `rtx_alloc.s` loses its only two RIP-direct relocations. An offset that drifts then fails the **build**, not a page.

---

## 6. WHAT THIS FILE IS FOR

Three seats proposed three cures in one hour. Each premise was true; each conclusion was wrong; each took **under ten minutes to refute by running it.** The common shape: *a rule inferred from one correct observation, adopted without running it against the population it would govern.* The `coo`'s `off < 0`, this seat's own first draft of `[GC-SPINE-LOST]` as a gradeable arm, and the `cto`'s export are the same mistake wearing three costumes — and the third one is the cheapest to catch, because the linker says it out loud.
