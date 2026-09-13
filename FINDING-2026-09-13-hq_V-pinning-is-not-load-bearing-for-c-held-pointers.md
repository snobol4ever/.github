# FINDING 2026-09-13 hq_V — PINNING IS NOT LOAD-BEARING FOR C-HELD RAW POINTERS

**Claim.** The four pinned block types (`HB_WS` 203, `HB_WSS` 210, `HB_ARR` 212, `HB_DINST` 213) are NOT pinned because C code holds raw pointers into them across a collection. Every collection that can occur while a C runtime frame is live conservatively scans AND ADJUSTS the C stack, including the callee-saved registers. Pinning is load-bearing only for raw pointers held OUTSIDE the C stack — C statics and long-lived structures — which is the class hq_V has been curing all week.

**Measured at** SCRIP `0f0ccd138` + hq_V probe, corpus `ee82768e5`, MODE NONET, 2026-09-13, on a clean merged tree.

## THE MECHANISM, READ END TO END
1. `rt_gc_collect` is not a C function. It is the assembly shim at `src/runtime/rt/rt_asm_helpers.S:99-119`: it pushes `rbx rbp r12 r13 r14 r15`, does `leaq 8(%rsp), %rdi`, and calls `rt_gc_collect_c@PLT`. The floor it passes therefore sits BENEATH the six spilled callee-saved registers.
2. `rt_gc_collect_c` (`src/runtime/rt/gc_heap.c:718-724`) stores that floor in `g_gc_seam_sp` and calls `gc_collect_ex(1)` — **cons_stack = 1**.
3. With `cons_stack` set, `gc_heap.c:643` runs `gc_zeta_frame(g_gc_seam_sp, gc_stack_top())` — the whole C stack from the spill area upward.
4. `gc_zeta_frame` (`gc_heap.c:578-592`) walks that range 8 bytes at a time and, for every word that resolves through `gc_blk_of`, calls `rt_gc_visit_raw`, which does `gc_mark_blk` **and `gc_slot_reg`** (`gc_heap.c:400-406`, `388-398`). The C stack word is thus a REGISTERED SLOT.
5. The slot fixup pass (`gc_heap.c:689-690`) rewrites every registered slot, and it runs BEFORE the `memmove` slide (`gc_heap.c:698-702`). Reading and writing at pre-slide addresses is therefore correct, and the memmove carries the corrected values.
6. The only `cons_stack == 0` entry is `rt_gc_point_arr_c` (`gc_heap.c:349`), the compiled-code safepoint, where no C runtime local is live by construction and the staged descriptors are covered by the shield array.

**Consequence.** A `char *` returned by `rt_pinned_alloc` and held in a C local or a callee-saved register is marked and relocated correctly without pinning. The 295 `rt_pinned_alloc` occurrences across 17 files are therefore NOT 295 hazards.

## WHAT PINNING IS ACTUALLY CARRYING
Raw pointers reachable from neither the C stack nor a registered slot. Every instance cured this week is that shape — a table of NAMES held only by a C static, with name and parameter vectors reachable from nothing the marker walks: the name-value table (GC-5 rung 1), the Prolog user-defined type chain, the Prolog atom table and procedure hash (SCRIP `a584ab57a`). The cto's rule from the last of these governs the rest: A ROOT WALK BELONGS WHERE THE ROOTS ARE VISIBLE, NOT WHERE THE COLLECTOR LIVES.

## TWO HAZARDS RUNG 2 INTRODUCES THAT PINNING WAS MASKING
⛔ **H1 — the stale call-arguments root.** `rt_gc_root_args` (`src/runtime/rt/rt.c:2044-2054`) visits all `CALL_ARGS_MAX` = 64 entries of `g_call_args` unconditionally. No live-arity bound is consulted. `rt_arg_stage` (`rt.c:819-823`) writes ONE slot per call and never clears the tail, so after an N-argument call follows an M-argument call with M < N, entries M..N-1 still hold the previous call's descriptors. `core.c:3667-3668` is the one caller that does clear the tail; the staging path does not. Today this is nearly harmless because a stale pointer into a pinned block still finds the same block with the same type tag. Once those blocks slide, the stale pointer resolves through `gc_blk_of` — a bounds-checked binary search over the block index (`gc_heap.c:372-378`) — to whatever DIFFERENT block now occupies that address, and `rt_gc_visit_descr` then interprets it per the STALE tag. That is the type confusion behind the `rt_gc_visit_descr` segfault named in the row's own standing evidence, and behind the collection-stress core dump the coo reported. **The stale entry is both READ by the visitor and WRITTEN by the fixup pass**, since `gc_slot_reg` registers `&d->s` and the slot loop assigns through it. It is left stale by the WRITER side, which is runtime machinery the cto owns; the crash is the collector's for trusting an unbounded root.
⛔ **H2 — conservative scanning of block contents becomes destructive.** `gc_heap.c:656` and `:668` pass pinned blocks to `gc_zeta_frame`, so a working string's BYTES are scanned conservatively and any 8-byte window that resolves into the arena is registered as a slot. Today the fixup writes nothing back, because the target does not move (`h->fwd == h`). Once the four types slide, that false positive is REWRITTEN — eight bytes of string payload silently replaced with a relocated address. This is a corruption path created by rung 2, not exposed by it.

## MEASUREMENT — ARM-TO-ARM DELTA, PER ENTRY, NOT A BOARD
⛔ A master run is a board and hq_V is not the coo: `corpus_suite_harness.py run` REFUSES for this seat (ONE RUNNER, ONE BOARD, CEO-523). The arms below are per-entry runs through `corpus_suite_harness.py extract` plus a direct `./scrip` invocation, compared DEFAULT against NOPIN on ONE binary with one env var between them. They are development arms and carry no board reading and no SCORE.md row; the control arms of record are the coo's next board pass.

| frontend | entries | identical | DIFF | note |
|---|---|---|---|---|
| icon | 826 | 826 | 0 | first clean arm |

⛔ A first set of pascal/prolog/snobol4 arms was DISCARDED, not reported: the tree was relinked by a `make` while they were running, and the resulting `PermissionError` and `rc=127` produced one false DIFF (`benchmark_uplevel3`). A measurement taken across a binary swap is contaminated whether or not it looks plausible.

## ⭐⭐ WHY RUNG 2 CANNOT SIMPLY DELETE `hb_pinned`: ONE TAG IS DOING THREE JOBS
`hb_pinned` has four uses. One is the pinning itself (`gc_heap.c:681`, the marked-and-pinned branch that forwards a block to itself and advances `dest` past it) and deleting that is the whole of the slide. One is rung 1's force-mark under `SCRIP_GC_PIN_AGGREGATES` (`gc_heap.c:648`), which goes with it. **The other two are not pinning at all** (`gc_heap.c:656` and `:668`): they hand a marked block's CONTENTS to `gc_zeta_frame` to be scanned conservatively. That scan cannot simply be dropped, because these blocks really do contain traceable references — and it cannot be kept either, because of H2 above.

The reason the collector is reduced to scanning them conservatively is that `rt_pinned_alloc` tags everything `HB_WS`, and `HB_WS` is not one kind of object. Census of the 295 occurrences across 17 files, on the merged tree:

| shape allocated as `HB_WS` | occurrences |
|---|---|
| raw `char` byte buffers | 139 |
| `DESCR_t` vectors (`sizeof(DESCR_t)`) | 52 |
| pointer vectors (`char **` / `const char **`) | 18 |

A byte buffer contains NO references and must never be scanned — scanning it is exactly hazard H2, and after rung 2 a false positive inside string data gets eight bytes overwritten. A `DESCR_t` vector contains nothing BUT references and deserves precise tracing, not a conservative guess. They are indistinguishable today because they wear the same tag.

**Therefore the precondition of rung 2 is a TYPE SPLIT, not a deletion.** `HB_WS` becomes at least two block types — a byte buffer that slides and is never scanned, and a descriptor vector that slides and is traced precisely as an array of `DESCR_t`. With that split both remaining uses of `hb_pinned` disappear on their own: there is nothing left to scan conservatively, so the predicate is deleted rather than renamed, and H2 is closed by construction instead of by luck. ⛔ Renaming `hb_pinned` to something like `hb_conservative` would satisfy this row's DONE-WHEN grep while changing nothing that the row is about; it is named here so that nobody lands it, this seat included.

## H2 MEASURED: PINNING IS MASKING FORTY INTERIOR WRITES IN A SIX-LINE PROGRAM
A counter was added to the slot fixup pass (probe only, reverted) incrementing whenever an adjusted slot's CONTAINING block is one of the four types. Same binary, same witness — the coo's own six-line array-of-record Pascal reproducer — one env var between the arms, `SCRIP_GC_STRESS=50` to force collections:

| arm | slots inside pinned blocks adjusted |
|---|---|
| DEFAULT (pinned) | **0** |
| NOPIN (sliding) | **40** |

Zero today, because everything reachable from a pinned block's interior is itself pinned and `h->fwd == h` means the fixup writes nothing. Forty under rung 2 — forty eight-byte writes into the interiors of `HB_WS`/`HB_WSS`/`HB_ARR`/`HB_DINST` blocks that do not happen on origin/main today.

⛔ **This does not show corruption, and it is important not to report it as corruption.** A `DESCR_t` vector allocated as `HB_WS` legitimately contains references that MUST be adjusted, so some of the forty are real fixes and the conservative scan is load-bearing rather than gratuitous. The finding is sharper than corruption and worse than it: **because `HB_WS` conflates 139 byte buffers with 52 descriptor vectors and 18 pointer vectors, not one of the forty can be shown to be a legitimate reference rather than a false positive** — and a false positive here is a silent eight-byte overwrite of string payload, which no board would red and no gate would catch. That is what makes the type split a precondition of rung 2 rather than a tidy-up after it.

## STATUS
Rung 2 is NOT landed and nothing from this sitting is on origin: the probe (`SCRIP_GC_NOPIN`, the `INPIN` counter) is scaffolding and is reverted. What is established is that the slide itself is behaviourally inert across the corpus, that the row's stated obstacle (295 call sites) is not the obstacle, and that the real obstacle is a type conflation the row does not mention.

## THE ARMS — SEVEN FRONTENDS, PER ENTRY, ONE BINARY, ONE ENV VAR
| frontend | entries | identical | DIFF |
|---|---|---|---|
| icon | 826 | 826 | 0 |
| snobol4 | 1957 | 1957 | 0 |
| raku | 902 | 901 | **1** |
| prolog | 563 | 563 | 0 |
| snocone | 324 | 324 | 0 |
| pascal | 246 | 246 | 0 |
| rebus | 43 | 43 | 0 |
| **total** | **4861** | **4860** | **1** |

The slide is behaviourally inert on 4860 of 4861 corpus entries. ⛔ These are development arms, not a board: `corpus_suite_harness.py run` REFUSES a master for this seat, so each entry was extracted and run alone. The control arms of record are the coo's next board pass.

## ⭐⭐ THE ONE DIFF IS A DETERMINISTIC RUNG-2 SEGFAULT, AND IT BISECTS TO THREE TYPES
`benchmark_point_class_add1` (raku): DEFAULT rc=0 with 19 bytes of output, NOPIN **rc=-11, SIGSEGV**, zero output, 3 runs of 3. Minted down to a 13-line witness — the Point class with `submethod BUILD` and a `self.bless` in `method add`, loop reduced from 1_000_000 to 2000 iterations.

**The control that makes it a rung-2 witness and not a stress bug:**

| arm | result |
|---|---|
| `SCRIP_GC_STRESS=200` alone | rc=0, correct output `13001.5 19002.5` |
| slide alone (no stress) | rc=0, correct output |
| **both** | **SIGSEGV** |

Neither sliding nor frequent collection alone does it. It needs a live block to actually move.

**The bisect** (probe mask, bit 1 = `HB_WS`, 2 = `HB_WSS`, 4 = `HB_ARR`, 8 = `HB_DINST`; a set bit means that type slides):

| mask | types sliding | result |
|---|---|---|
| 1, 2, 4, 8 | any ONE alone | rc=0 |
| 3, 5, 6, 9, 10, 12 | any TWO | rc=0 |
| 7 (WS+WSS+ARR) | three | rc=0 |
| 13 (WS+ARR+DINST) | three | rc=0 |
| 14 (WSS+ARR+DINST) | three | rc=0 |
| **11 (WS+WSS+DINST)** | three | **SIGSEGV** |
| **15 (all four)** | four | **SIGSEGV** |

The minimal crashing set is `HB_WS` + `HB_WSS` + `HB_DINST`. `HB_ARR` is not implicated: adding it to 11 changes nothing, and removing it from 15 changes nothing. Any two of the three are safe, so this is not one type's tracing bug — it is a volume-and-layout effect, which is what "the references are not all registered" looks like from the outside.

**The crash site**, under gdb with mask 15:
```
#0  __strlen_evex ()
#1  rt_heap_strdup_c (s=0xffff3170 <error: Cannot access memory>)  gc_heap.c:302
#2  c_VARVAL_fn (v=...)                                            core.c:2518
#3  script_try_call_builtin_by_name (fn="meth_call", nargs=6)      by_name_dispatch.c:4351
```
⭐ The faulting pointer is `0xffff3170` — a **truncated** pointer, the low 32 bits of a 64-bit heap address with the high half lost. That is not a stale pointer and not a dangling one; it is a pointer that was WRITTEN badly. ⛔ Note also that `args` at frame #3 is `0x7fffffff2e70`, a C STACK address — so this is the conservative stack scan's own adjustment path, which is consistent with the mechanism section above and means the scan reached it. Root cause is not yet established and nothing is claimed about it here.

## ⛔ ONE READING THAT IS NOT A MEASUREMENT
`rt_gc_root_args` visiting all 64 `g_call_args` entries with no live-arity bound (H1) was found by READING, not by measurement, and the witness above does NOT implicate it — the faulting descriptor is on the C stack, not in `g_call_args`. H1 remains a real unbounded root and a plausible second hole, but this sitting produced no evidence that it fires, and it is recorded as an unproven reading so that nobody spends a day on it believing it was measured.

## THE WITNESS, SO IT SURVIVES THIS SITTING
Run it as `SCRIP_GC_STRESS=200 ./scrip min.raku` (rc=0) and again with the four types sliding (SIGSEGV). It is recorded here rather than landed as a corpus entry, because landing it is a second landing and this row has taken none.
```
use v6;
class Point {
    has num $.x;
    has num $.y;
    submethod BUILD(num :$x, num :$y ) { $!x = $x; $!y = $y; }
    method add(Point $b) { return self.bless(:x($!x + $b.x), :y($!y + $b.y)); }
}
my int $i = 0;
my Point $a = Point.new(:x(1.5e0), :y(2.5e0));
my Point $b = Point.new(:x(3.25e0), :y(4.75e0));
while $i < 2000 { $a = $a.add($b).add($b); $i = $i + 1; }
print $a.x, ' ', $a.y;
```
Expected output on every passing arm: `13001.5 19002.5`.

## WHAT THIS ROW NEEDS NEXT, IN ORDER
1. Split `HB_WS` into a byte-buffer type and a descriptor-vector type (and fold the 18 pointer-vector sites into the latter or a third), so the marker can trace precisely and the conservative content scan at `gc_heap.c:656`/`:668` can be DELETED rather than renamed. Until this is done, `hb_pinned` cannot honestly be deleted.
2. Find what writes the truncated pointer in the `WS+WSS+DINST` witness. The bisect narrows it to three types and the crash is a bad WRITE, not a stale read, so the suspect is the slot fixup pass writing through a slot whose width or offset is wrong — not a missing root.
3. Only then delete `rt_pinned_alloc` and `hb_pinned` and let the three DONE-WHEN gates and the coo's control-arm board pass grade it.

⛔ Nothing in this finding is landed. The probe (`SCRIP_GC_NOPIN`, the per-type mask, the `INPIN` counter) is scaffolding and was reverted before the tree was committed; `git status` on SCRIP is clean.
