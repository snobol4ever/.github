# FINDING 2026-09-13 hq_V — a heap block whose address is baked as an imm64 into mode-3 machine code can never be reached by a registered slot, so GC-5 rung 2 cannot be completed as stated

**Claim.** The rung-2 cure as the baton states it — *"those four types slide like every other block, every reference into them is a registered slot, and hb_pinned plus rt_pinned_alloc are DELETED"* — is unachievable for one class of reference, and no amount of root-walking closes it. In mode 3 the emitter writes the **absolute address of a heap block as a 64-bit immediate inside the instruction stream it is assembling**. A slot is a memory location the collector can rewrite; an operand embedded in emitted code is not a location the collector knows, and registering it would mean the collector rewriting live machine code. Those blocks therefore cannot slide. They must LEAVE the collected heap, not become movable.

**Measured, 2026-09-13, SCRIP e87efd6b1 plus the rung-2 slide experiment (the pinned branch of the forwarding loop deleted, everything else unchanged).**

| arm | witness | result |
|---|---|---|
| slide, gc gate: aggregates collectable | `every i := 1 to 4000000 do L := [i, i+1, i+2]` | rc=139 SIGSEGV, RSS 604160 KB |
| slide, gc gate: interiors marked, `dat` m3 | SNOBOL4 `DATA('NODE(VAL,NXT)')` live across 60000 loops, `SCRIP_GC_STRESS=500` | SIGSEGV, core dumped |
| slide, same witness, **m4** | same program, `--compile` then gcc | **PASS**, byte-identical to `sbl -bf` |
| slide + udef chain rooted, churn witness | same 4M-list witness | rc=0, `done 3` |
| slide + udef chain rooted, `dat` m3 | same DATA witness | still SIGSEGV |

**The two backtraces name two different holders, and only one of them is curable.**

1. `_udef_lookup` → `strcasecmp(t->name, name)` at `src/runtime/core/core.c:2909`, reached from `DATCON_fn` ← `rt_make_list`. The holder is `static DATBLK_t *_udef_types`, a C static chain of `HB_WS` blocks whose `name`, `fields` vector and `fields[i]` strings are `HB_WSS` blocks. Nothing walked it. **This one is a real missing root and it is cured** — `core_gc_roots` now visits the chain exactly as rung 1 cured the name-value table beside it, and the churn witness goes rc=139 → rc=0.

2. `APPLY_fn(name=0x7fff4dc08dd0 "")` at `core.c:3668`, reached from `rt_call_arr_bl` ← emitted code (frame `0x00007fff6dc01281`, no symbol). The function-name string is interned by the LOWERER through `lp_strdup` (`src/lower/lower_common.c:45-48`, which is `rt_pinned_strdup`), and `src/templates/bb/bb_call.cpp:450` materialises it as
   `s += x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t)fn, fl.c_str());`
   In mode 4 `x86_load_ro` (`src/templates/x86/x86_asm.h`) emits `lea dst, [rip + label]` against a `.rodata` string — a fresh copy outside the heap, which is why **every m4 arm passes**. In mode 3, `MEDIUM_BINARY` is set and the same call emits `REX.W B8+r` — **`movabs dst, imm64` carrying the raw heap pointer**. The block moved; the immediate did not; `APPLY_fn` read a name that is now `""`.

**Why this is the general case and not one call site.** `lp_strdup` is the lowerer's string interner: every IR-side string reaches the runtime this way, and IR nodes live in compiler memory the collector never scans. `rt_pinned_alloc` and `rt_pinned_strdup` have **336 call sites** (314 in `src/runtime`: by_name_dispatch 193, core 27, unification 21, pattern_match 17, gc_heap 13, keywords 10). They are not one population. They are at least two, and the division is not by block type but by LIFETIME AND HOLDER:

| class | what it is | holder | can it slide? |
|---|---|---|---|
| program-lifetime | lowerer-interned names, field-name tables, DATBLK type descriptors, file-handle aliases | emitted-code immediates and compiler-side malloc | **no** — no slot exists to register |
| run-time data | DATINST instances, ARBLK data vectors, workspace buffers | DESCR_t fields, aggregate interiors, C statics | yes, once rooted |

**Consequence for the row.** The deletion of `hb_pinned` is reachable — the four types can stop being a special case in the forwarding loop — but only after the program-lifetime class is EVICTED from the collected heap into `A_PROG` (`rt_arena.h` already declares the flavor), so that the blocks the emitter bakes are not GC blocks at all. Under that shape Lon's *"we do not allow pinning in our heap since we slide"* is satisfied literally: nothing in the heap is pinned, because what cannot move is not in the heap. Registering slots for the run-time class alone will not get there, and a landing that deletes `hb_pinned` without the eviction turns every mode-3 program that reaches a by-name call into a SIGSEGV. Asked to the ceo (row owner) 2026-09-13.

**Fail-once for the cure that did land.** With the slide experiment in place the churn witness dies rc=139 and passes rc=0 with the `_udef_types` chain rooted; that is the arm that proves the root walk measures something. Under the CURRENT pinned policy no witness I could mint shows the gap observably — an unmarked pinned block is left behind by the forwarding loop and my 60000-iteration DATA witness never reclaimed it — so the root walk lands as proven-under-slide and inert-under-pin, and that is stated rather than dressed up as a cure of a visible red.
