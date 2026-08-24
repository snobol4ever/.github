# FINDING 2026-08-24 hq_P — icon-n2's activation record has a home: the WORKSPACE ISLAND, which is scanned but never relocated. Allocator built, unit-proven, zero new globals — and `bench_correct` 0/8 turns out to be the SAME defect, so this is one cure with two scoreboards

LINKS: rows `icon-n2-generator-activation-frames` (rank 0) and `icon-bench-correct-zero-of-eight` (weight 15, the largest Icon lever). Predecessors: `FINDING-…-icon-generator-has-no-activation-frame.md` (three corruptions, s271), `FINDING-…-generator-frame-cannot-live-below-the-callers-rsp.md` (two-moment gdb witness, s271), `FINDING-…-icon-n2-allocator-needs-no-new-globals-gcheap-ruled-out.md` (earlier this session). Tree: SCRIP `ab9c087c`+, pristine `-O0`.

## ⭐ FIRST, THE THING THAT CHANGES PRIORITY: TWO ROWS, ONE DEFECT

`icon-bench-correct-zero-of-eight`'s own baton root-causes its 0/8 as *"a procedure containing `suspend` is emitted with NO ACTIVATION FRAME, while its body still addresses frame-relative slots — which land on the caller-pushed {γ, ω} port pair."* That is **verbatim the N-2 defect**. These are not two rows that happen to be adjacent; they are one cure with two scoreboards. The allocator below is the shared substrate:

- N-2's target set: 16 FAIL + 1 BADEXIT on the rung suite, best-case yield 12 → `PASS 246 → 258` against a `≥256` DONE-WHEN.
- `bench_correct`: **0/8 at weight 15**, and Icon META cannot pass ~82 while it sits at zero.

Neither row should be worked without the other's LEDGER open. Cross-referenced in both task files this session.

## THE STORAGE QUESTION IS SETTLED — AND THE ANSWER WAS ALREADY IN THE TREE

Three candidate homes, and the first two are ruled out by measurement, not preference:

| home | verdict | the disqualifying fact |
|---|---|---|
| C stack (below caller rsp) | ⛔ RULED OUT s271 | gdb, two moments, one address: `0x7fffffffde30` held `{0,0}` at yield and `write()`'s own call frame by dereference. Everything below a C stack pointer is scratch. |
| GC arena (`rt_gcheap_alloc`) | ⛔ RULED OUT this session | `gc_heap.c:668` — *"THE PIN ARM IS GONE (Lon s262) … every live block now relocates."* The compactor fixes up only enumerable roots (`:674`); this protocol banks the record address in `FRQ(act+8)` and resume-record word 3, **neither enumerable**. Same staleness class as the stack, different mechanism. |
| ⭐ **workspace island** (`rt_ws_alloc`, `HB_WS`) | ✅ **CORRECT** | The compaction index is built by walking **`g_hp_arena` alone** (`gc_heap.c:610-614`); the island is a separate mapping that never enters that index, so it is **never relocated** — while `gc_heap.c:624` scans it as a root region. **Non-moving AND traced** is exactly the pair required. |

⭐ **The requirement was misstated for sessions as a size/lifetime question. It is a STABILITY question:** the record must live where neither the C stack discipline nor the compactor may move or reuse it while a suspension is outstanding. Once phrased that way the island is the only region in the process that qualifies, and it was already the storage `icn_gen_stk_grow` grows through.

⛔ Co-expressions (`rt_coexpr.{c,h}`) were checked and **rejected on cost, not correctness** — `pthread_t` + two `sem_t` per activation, on a speed goal. Recorded so nobody re-derives it.

## TWO PROPERTIES THAT FELL OUT, ONE OF THEM LOAD-BEARING

**1. ⭐ GC correctness is STRUCTURAL here, not a promise.** `gc_heap.c:624`'s island scan sits inside `if (!pz)`, so the precise-zeta fast path would skip it — which looks like a hazard until you follow the registration. `rt_gc_root_range_add` (`:484`) bumps `g_gc_rrng_n` but **not** `g_gc_rrng_ss`, and `:619` computes `pz = (… && g_gc_rrng_n == g_gc_rrng_ss)`. So **registering a live generator's record automatically forces the conservative arm — the very arm that scans the island — for exactly as long as that generator is suspended.** The record cannot be precise-path-skipped while live. The cost is paid only while a suspension is outstanding, and it self-clears.

**2. ⛔ The island is a BUMP ALLOCATOR WITH NO FREE** (`g_wsi_ws += total`, `gc_heap.c:234`). Without a free list a generator in a loop leaks one record per activation until the island aborts with *"workspace island exhausted"*. This is the detail that would have shipped as a fixed-size time bomb: correct on every small witness, fatal on the first real workload. The free list rides the **existing** `g_icn_gen_stk` array — a retired entry keeps its `frame` and clears its `gen_fb` — so it costs no new global.

## ZERO NEW GLOBALS, AND ZERO NEW FIELDS — Lon asked "what global do you need?" and the answer is none

`icn_gen_state_t`'s `caller_fb` had **zero reads and zero writes** anywhere in `rt.c` (measured before touching it). It is renamed `frame` and carries the record. The struct does not change size; `g_icn_gen_stk_buf` / `g_icn_gen_stk` / `_top` / `_cap` already existed and predate this row. **The NO-NEW-GLOBALS banner ask this row's baton predicted is not needed and has been withdrawn.**

⛔ **This is also why slice (v)'s deletion list is dangerous, not merely premature** — it schedules deleting the very array the allocator is built on. Re-cut and recorded in the task file: KEEP and EXTEND the state stack; delete only the wire shadows (`g_gen_pending_*`), the `rt_gen_get_fb` stub, and the dead `icn_zframe_gen` sites. The row's DONE-WHEN greps for `g_gen_pending_cont`, which stays correct under the re-cut.

## THE RECORD LAYOUT, AND WHY THE PORT PROTOCOL SURVIVES UNCHANGED

```
[base+ 0] caller rbp     [base+ 8] γ     [base+16] ω     [base+24 …] ζ storage
[base- 8] capacity       (the record's own span, for free-list reuse)
```

The re-homed operand accessors `ZOPQ`/`ZRES` (`x86_asm.h:888-895`) address through **`RDQ("rbp", off)`**. So pointing `rbp` at this record instead of at the stack **redirects every ζ reference with no change to a single template**, and `[rbp+8]`/`[rbp+16]` keep meaning γ/ω exactly as the existing α-prologue comment already claims. ⭐ This is the precise sense in which s271's conclusion holds — *the R-4(b) PORT protocol transfers cleanly and its STORAGE cannot*: the port wiring needs no rework at all, only its base register needs a different pointee.

## WHAT LANDED, AND WHAT IT IS PROVEN AGAINST

`rt_icn_gen_frame_alloc(gen_fb, bytes)` / `rt_icn_gen_frame_retire(gen_fb)` in `src/runtime/rt/rt.c`, exported and verified present in the built `.so` by `nm -D`.

⛔ **RETIRE, NOT FREE — deliberately.** A retired record stays allocated and stays registered as a GC root range; only its `gen_fb` binding clears. Un-registering would mean removing from `g_gc_rrng`, which has **no removal API** (`:484` only appends) and would corrupt the `g_gc_rrng_ss` accounting `pz` is computed from. Records are zeroed on **reuse** rather than on retire, so a stale suspension resuming after ω — a bug, but one we would rather see as a zero value than as a wild pointer — reads zeros.

⭐ **Unit-proven in isolation, 10/10**, via the new permanent `scripts/test_icn_genframe_alloc.sh` (+ `scripts/probes/icn_genframe_alloc.c`): non-NULL, 16-byte aligned, capacity covers `bytes+24` rounded up, arrives zeroed, **two live generators get distinct records**, **a retired record IS reused (the no-leak property)**, **a reused record is re-zeroed (no bleed between activations)**, an oversized request does not reuse a too-small free record, and retiring an unknown key is a no-op rather than a crash.

⭐ **It is a TEST, not a GATE, on purpose** — and the script says so in its header. Nothing emitted calls the allocator yet, so no corpus program exercises it and no board would move if it broke. That is precisely the window in which a storage bug gets baked in and then blamed on the codegen that lands on top of it. The storage half is proven *before* anything depends on it.

## ⛔ NOT CLAIMED

The allocator is reachable from **no emitted code**. Zero Icon programs move, in either direction, and the `SCRIP_ICN_GENFRAME2` witnesses still SIGSEGV with the switch on — the α-prologue still carves on the stack (`emit.cpp:2783`, `sub rsp, frame_total`). This finding delivers the storage half and its proof, not the cure.

## NEXT, IN ORDER

1. α: replace `sub rsp, frame_total` with the allocator call; copy the caller-pushed γ/ω into `[base+8]/[base+16]`; point `rbp` at the record.
2. ω: `rt_icn_gen_frame_retire` before the retire sequence.
3. β/γ: unchanged in shape — verify γ-suspend no longer discards the record and β restores `rbp` from `FRQ(act+8)`.
4. Then the witness set, both rows' scoreboards, still behind `SCRIP_ICN_GENFRAME2` default OFF.
