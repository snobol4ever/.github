---
name: scrip-memory-model
description: SCRIP's memory model: the three zetas (RSP spine, RBP frame, standing frame), placement decided once by the planner, the plan table, compile-time frame maps and the collector, polls and safe points. REQUIRED by the skill gate before editing src/planner, src/emitter or src/runtime/rt/gc_*.
---

# SCRIP's memory model

One machine under seven syntaxes: every pattern, generator and goal is a four-port Byrd box (α proceed, β recede, γ succeed, ω concede) wired at compile time. The law is RULES.md (THE MEMORY MODEL, THE LIFETIME RULE, NO GLOBAL HOLDS A STACK, NO FRAME MARKERS, THE COLLECTOR GUESSES NOTHING); the design is the ARCH pages of § 4, and a page beats this skill. File maps, verifier lists and receipts in full are in `reference.md` beside this file.

## 1. The law and its verifiers

- **Three zetas:** every operand and local starts on the RSP spine (16-byte DESCR cells at compile-time offsets); it moves to the RBP activation frame only when Lon's two tests force it; the standing frame is the root graph's own storage, never a global.
- **The lifetime rule** (CEO-1354): construct lifetime → stack; outlives its scope → heap; out of stack → a bigger declared `-s`.
- **Placement is decided once, in the planner** (CEO-1895); the emitter reads the plan table and decides nothing. A retry never restores RSP (no RSP reset at any β); a γ pops only a fenced construct's cells (CEO-1843). Edge laws: γ→α `X_i − gpop = E_j`; ω→β `X_i − K_i − wpop = X_j`.
- **No global holds a stack** (CEO-1542/1543): the only stacks outside RSP/RBP are the two r12 islands (SNOBOL4 conditional assignment, Prolog trail and choice points).
- **The maps stay** (CEO-1368/1371): one static frame map per frame, typed visitors, no conservative scan, no pin; only emitted code at the return of an allocating call collects.
- **The verifiers are the oracle of this layer**, each red once before trusted: `SCRIP_ZD_CHECK=1` (edge laws), `SCRIP_ZD_RTCHECK=1` (depth at every α and β), `SCRIP_GC_CHAIN_CHECK=1..3`, `SCRIP_GC_STRESS=1` with `SCRIP_GC_PLANT_FLIP=1`, `SCRIP_ZSM=1` (the frame census), `util_gen_gc_allocating_table.py --check`. The language oracle still grades every witness in both modes.

## 2. The manuals

`/home/resources/manuals/gc/` (the collector literature; `PROVENANCE.txt` names each), `/home/resources/manuals/byrd-boxes/` (the four-port model, the WAM, Proebsting on Icon), the language folders. ABI facts are measured (`objdump -d` on the linked binary), never remembered.

## 3. The source map

- Planner `SCRIP/src/planner/`: `planner_stage.c` (the entry), `zeta_plan.cpp` (`zd_plan`, `zd_k`), `plan_facts.cpp` (the PLAN_COLUMNS the emitter reads), `frame_layout.c`, `planner_report.cpp` (`--dump-plan`), generated `box_cell_shapes.inc`. Plan-time code uses the `_g` forms.
- Emitter `SCRIP/src/emitter/emit.cpp` (one `switch (nd->op)` binding kinds to templates); `src/ir/` (`IR.h`, `descr.h`, `gc_frame_map.h`, `ct_arena.c`: no malloc).
- Templates `src/templates/bb/`, `xa/`, `x86/` (the one encoder `x86_asm.cpp` behind `x86_ops.h`).
- Runtime: `src/runtime/rt/gc_heap.c` (heap, chain walk, compactor), `rt_slab.c`, `rt_coexpr.c`, `rt_pl_trail.c`; `src/runtime/rtx/` (asm leaves on rtcc); `src/runtime/core/g_runtime*.h` (the one runtime state struct).
- Dumps: `--dump-ir|--dump-bb|--dump-zeta|--dump-plan`; sizes by `-d<kb>k -s<kb>k`; `SCRIP_PL_TRACE=1` the Prolog port tracer.

## 4. The ARCH pages

ARCH-ZETA-ONE-COORDINATE.md (the coordinate, definiteness); ARCH-THREE-ZETAS-EMISSION.md (the cell forms, the plan table); ARCH-ZD-DEPTH-PLANNER.md (K, the admission ladder); ARCH-ZETA-LAYOUT-ONE-SOURCE-OF-TRUTH.md; ARCH-FRAME-LAYOUT-FIXED-CELLS.md; ARCH-GC-COMPILE-TIME-FRAME-MAPS.md (§ 7 frozen, § 13 the chain, § 14 asm collection, § 15 the compactor); ARCH-RT-CALL-PROTOCOL.md; ARCH-X86-ASM-ENCODER.md; ARCH-EXCEPTIONS-ONE-PROTOCOL.md; the Prolog, SNOBOL4 and Icon RTX and frame pages. The full question-to-page table is in `reference.md` § 4.

## 5. How a landing here is graded

Shared code: graded by every language's witnesses. Per landing: the row's DONE-WHEN (a design step `test_design_*_steps.sh --step N`, or a gate); `test_feature_reps.sh <lang> <feature>` for touched features; ALL EIGHT `test_smoke_*.sh` before the push; the collector's witnesses under `SCRIP_GC_STRESS=1` in both modes for a collector landing. One program by hand: `corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>` (in `harness/scripts/`). The coo runs the heavy passes and the emission identity. Measure by instruction count (`util_instr_count.sh`); a clock only inside `util_quiet_slice.sh`.

## 6. Debugging a red here

1. `bash ../harness/scripts/monitor_run.sh <prog> --oracle` (the bug is between the last agreeing and the first diverging event), then asm-diff beside a passing sibling within one mode.
2. The plan before the code: `--dump-plan` diff of PLAN_ROWs; `SCRIP_ZD_CHECK=1`; `SCRIP_ZD_RTCHECK=1` traps the first α or β at the wrong depth.
3. Collector suspicion: `SCRIP_GC_STRESS=1` with the flip plant; `SCRIP_GC_CHAIN_CHECK=2`; bound memory with a cgroup, not a timeout.
4. Templates: `SCRIP_PL_TRACE=1` under gdb; gdb last, with a breakpoint and a hit count. A `-dirty` reading is unread (CEO-2060).

## 7. Rulings a landing here must not break

- The planner decides, the emitter reads (CEO-1895); after lower every variance is an IR fact (CEO-1838/1840).
- Zeta has no modes: no selector chooses a zeta's behaviour.
- A retry never restores RSP; a γ pops only fenced cells; a ball never re-enters a retained frame (CEO-1759/1814/1841/1843).
- The maps stay; the collector guesses nothing; the allocator never collects; a leaf that can allocate returns to a safe point.
- Out of stack is a bigger declared `-s` (CEO-1354/1353); `SCRIP_HEAP_KB` never sets a program's size.
- No new global without Lon's grant that session; `g_runtime` is the one runtime state struct.
- Generated tables are regenerated, never edited or merged (`gc_allocating_table.inc`, `box_cell_shapes.inc`, `rt_entry_table.inc`).
- Every instruction through `x86(...)`, both media; one form per box; no C function enters a box (CEO-1576, CEO-2045).
- Large chunks (CEO-1478..1484); hand-written C on the 200-column rule with no comments; no `-O2`; no fixed limits.
