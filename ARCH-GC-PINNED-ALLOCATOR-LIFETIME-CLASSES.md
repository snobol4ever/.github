# ARCH — the pinned allocator is three populations, and two of the three already have an arena flavor waiting for them

**Author** hq_V (CONCERN 4, GC heap storage), 2026-09-13, on SCRIP `089a028ea`. **Status** — the census is the durable part; the cut it implies is an ASK to the ceo (owner of `icon-gc-rung-2-…`), not a ruling. Companion to FINDING-2026-09-13-hq_V-a-heap-block-whose-address-is-baked-as-an-immediate-into-mode-3-machine-code-can-never-be-reached-by-a-registered-slot.md.

## The claim

`rt_pinned_alloc` / `rt_pinned_strdup` / `rt_pinned_realloc` are not one facility. They are **three different lifetimes wearing one name**, and the reason the block types `HB_WS HB_WSS HB_DINST HB_ARR` are pinned is that ONE of the three genuinely cannot move. Treating the name as a population — "delete the 336 call sites" — mixes a design change, a mechanical normalisation, and a genuine hazard into a single undifferentiated number. `rt_arena.h` already declares `A_PROG` and `A_TRANS`; two of the three classes are asking for exactly those, and the pinned allocator has been standing in for both.

| class | what it holds | who holds it | can it slide? | where it belongs |
|---|---|---|---|---|
| **A — program lifetime** | lowerer-interned names, `FNCBLK`/`DATBLK` registries, grammar registry, function aliases, interned atoms, the stable ASCII table, file-handle aliases | **emitted-code immediates** and compiler-side `malloc` the collector never scans | **NO — no slot exists to register** | `A_PROG` arena, outside the collected heap |
| **B — run-time value** | result strings and aggregates that immediately become a `DESCR_t` | a descriptor, an aggregate interior — already traced | yes, today, with no new machinery | the ordinary movable path: `rt_str_alloc`, `rt_agg_alloc` |
| **C — run-time scratch** | sort vectors, `bagof` group tables, the `sprintf` growth buffer, per-call name vectors | **a C local, possibly a callee-saved register**, across allocations that can collect | only where the local is spilled — a register copy is stale and nothing can find it | `A_TRANS` arena, released at the call's end |

Class A is the one proven impossible by the finding: `bb_call.cpp:450` hands a `lp_strdup` string to `x86_load_ro`, which under `MEDIUM_BINARY` emits `movabs reg, imm64` carrying the raw heap address into the instruction stream it is assembling. Mode 4 emits `.rodata` plus a rip-relative `lea`, which is why every m4 arm of the slide experiment passes where m3 dies.

Class C is the one that is quietly dangerous and that **no gate we own would catch**, because a spilled local is fixed by the conservative stack scan and a register-resident one is not — so the same source line is correct or corrupt depending on what the C compiler decided about register pressure that day. Moving class C to a movable allocator without moving it out of the heap would buy a Heisenbug, not a cure.

## The census, and what it failed to resolve

Measured 2026-09-13 by grouping every `rt_pinned_*` call site under its enclosing function definition, then **reading a representative of each group** — not by pattern-matching the call text.

| class | sites | functions |
|---|---:|---:|
| A — program lifetime | 81 | 20 |
| B — run-time value | 56 | 13 |
| C — run-time scratch | 49 | 8 |
| **unresolved: two giant mixed dispatchers** | **153** | 2 |
| **unresolved: the small-function tail** | **111** | 80 |
| **total C call sites** | **450** | 123 |

⛔ **186 of 450 sites are resolved. 264 are NOT, and that is 59% of the population.** The two unresolved dispatchers are `by_name_dispatch.c:script_try_call_builtin_by_name` (87) and `try_call_builtin_by_name_bl_s` (66); both are demonstrably MIXED — the same function allocates a `char *` that becomes a `STRVAL` (class B) and a `size_t *` scratch vector held only in a local (class C) — so they cannot be classified at function granularity and were not guessed at. The 111-site tail is 80 functions of one to three sites each that were counted but not read. The earlier figure of **336** in the row's own standing evidence counts only `rt_pinned_alloc` and `rt_pinned_alloc_tag`; adding `rt_pinned_strdup` and `rt_pinned_realloc` — which the DONE-WHEN's grep also catches — gives 450, and 442 of those are in `src/runtime`, `src/driver`, `src/lower`, `src/parsers`.

## What follows for GC-5 rung 2

1. **Class B is landable with no ruling and no new machinery**: it is a normalisation onto the allocator the collector already traces. It shrinks the population without touching the design.
2. **Class A requires the eviction** and crosses the lowerer and the emitter, so it is the ceo's to cut and possibly other seats' to execute.
3. **Class C requires `A_TRANS`, not a movable allocator** — and its absence of a failing witness is a property of register allocation, not evidence of safety.
4. **`hb_pinned` can only be deleted once A and C are out of the heap.** Deleting it before that turns every mode-3 program reaching a by-name call into a SIGSEGV — measured, not predicted: that is exactly what the slide experiment did.
5. The row's DONE-WHEN greps for the NAMES in `src/runtime`. Renaming without relocating would satisfy the grep and leave the defect, so **the grep is a population check and not a proof**; whatever lands must carry the churn and aggregate-interior gates as its actual evidence.
