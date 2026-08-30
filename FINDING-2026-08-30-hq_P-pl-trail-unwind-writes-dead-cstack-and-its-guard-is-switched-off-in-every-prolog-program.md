# FINDING: the Prolog crash family is ONE source line — `pl_trail_unwind` (`pl_cell.h:81`) — and the guard written to prevent it is **unconditionally switched off in every Prolog zframe program**

**Seat:** hq_P (TRIO) · **Date:** 2026-08-30 · **Row:** `calling-convention-depth-tracked` · **Instrument:** valgrind memcheck + an LD_PRELOAD control arm · **Source edits: NONE** (measurement only; no cure committed)

## WHAT WAS OPEN, AND WHAT IS NOW CLOSED

My own `## NEXT` block asked for exactly two things. Both are answered.

- **"Find what writes past `dop_call_nothrow`'s frame — the localization is solid, the writer is not found."**
  ✅ **The writer is `pl_trail_unwind`, `src/parsers/prolog/pl_cell.h:81`:**
  `if (!plc_dead_cstack(ents[t->top].addr)) *ents[t->top].addr = ents[t->top].old;`
  It restores a trailed binding by writing a 16-byte `pl_cell_t` through a pointer the trail recorded — **and the trail stores raw C-stack addresses.** When the owning frame is gone, the write lands in dead stack.
- **"Check whether `g_plw_unwind_floor` is ever left STALE."** ✅ Worse than stale: **it is never set at all** in the affected programs. See below.

## THE LOCALIZATION IS NOW ONE LINE ACROSS THE POPULATION — 18/21

Every one of the 21 van Roy kernels, compiled m4 and run under memcheck, default arm:

```
18 / 21 kernels report an invalid access, and in ALL 18 the FIRST one is:
    pl_trail_unwind (pl_cell.h:81)
      <- dop_trail_unwind        (by_name_dispatch.c:1484)
      <- dop_call_nothrow        (by_name_dispatch.c:1513)
      <- rt_pl_dop_trail_unwind  (by_name_dispatch.c:1589)
      <- n<NNN>_call_prolog_bx   (emitted)
```
The 3 that report NONE (`meta_qsort`, `queens`, `queens_8`) are **not clean** — see the memcheck limit below.

**Two flavors at the one line**, and the difference matters:
- **dead-stack write** — `tak`, and hq_B's 8-line witness: *"Address 0x1ffefef3b0 is on thread 1's stack ... 1680 bytes below stack pointer"* (two writes, 1680 and 1672 below rsp — the two halves of one `pl_cell_t`).
- **wild read** — `sendmore`: *"Address 0x59c92fe8 is not stack'd, malloc'd or (recently) free'd."* The trail **entry itself** is garbage, so this is not only a dead target: `t->top`/`mark`/`area.base` can be corrupt too. A cure aimed only at "don't write to dead frames" does not cover this flavor.

## THE GUARD EXISTS, AND IT IS TURNED OFF EXACTLY WHERE IT IS NEEDED

`plc_dead_cstack()` (`pl_cell.h:64–75`) exists precisely to suppress flavor 1. It is dead code in every Prolog zframe program:

- `src/driver/scrip.c:1469` emits `call rt_plw_floor_bypass_on@PLT` into the **emitted main's preamble** (m4).
- `src/driver/scrip.c:1887/1890` sets `g_plw_floor_bypass = 1` directly around `rt_outer_call` (m3).
- With the flag set, `dop_call:1495` and `dop_call_nothrow:1511` **skip the floor assignment**, so `g_plw_unwind_floor` keeps its initializer `0` (`by_name_dispatch.c:1486`).
- `plc_dead_cstack`'s **first line** is `if (!g_plw_unwind_floor) return 0;` — *"not dead"*. Every dead address is reported live, and every write proceeds.

⛔ **THE BYPASS RESTS ON A STATED PREMISE THAT IS FALSE.** Its commit (`77925561`) says, verbatim:
> *"Prolog zframe graphs **guarantee all trail entries are PLJ-heap-resident** — plc_dead_cstack must always return 0 for them."*

Memcheck disproves it directly: a trail entry whose address is **on thread 1's stack**. The guarantee is asserted in a commit message and enforced nowhere.

⭐ **AND THE BYPASS WAS NEVER A CLAIM THAT THE GUARD IS UNNECESSARY.** The same commit's root-cause paragraph says the real problem was that `plc_dead_cstack` does `fopen`/`fgets`/`sscanf` (`char ln[256]`) **on a stack misaligned 8-mod-16 by the JIT frame**, making `sscanf`'s `movaps` SEGV. So a workaround for an **ABI-alignment bug in the guard's implementation** was installed as a permanent disabling of the guard's **function**, justified by a guarantee nobody checks. That is this row's thesis — *site patching produced the disease* — in its purest form.

## CONTROL ARM (m4; no rebuild, no source edit)

`rt_plw_floor_bypass_on` interposed to a no-op via LD_PRELOAD, so the guard runs:

| | default (bypass on) | control (guard on) |
|---|---|---|
| hq_B 8-line witness | `rc=134` smash | ✅ **`rc=0`** |
| its passing sibling (`fib(10,F)` — one goal fewer) | `rc=0` | `rc=0` (undisturbed) |
| 21 van Roy kernels, `rc=0` | **0/21** | **3/21** (fib, nrev, queens_8) |

Also `nreverse` and `qsort` move `134` → `1` (clean exit, no crash); `meta_qsort`, `queens`, `zebra` move `134` → `139`; 13 are unchanged.

⛔ **SO RE-ENABLING THE GUARD IS NOT THE CURE, AND I AM NOT PROPOSING IT AS ONE.** It cures the minimal witness and 3 kernels and leaves 13 untouched. It is a **discriminator**, not a fix: it proves the disabled guard is *a* live cause, not the whole mechanism.

## ⛔ THREE LIMITS, RECORDED SO NOBODY INHERITS THEM AS FACT

1. ⭐ **MEMCHECK SEES ONLY THE BELOW-RSP / UNMAPPED SUBSET OF THESE WRITES.** A trail write landing inside a *live, mapped* frame is perfectly legal to memcheck and is reported not at all — and that is precisely the write that kills `dop_call_nothrow`'s canary at `:1516`. So **"NONE" is not "clean"**: `meta_qsort` reports NONE and still aborts at `__stack_chk_fail`. An instrument that cannot see the fatal write will print a clean bill of health for the program that dies.
2. **The control arm is m4-only.** m3 sets `g_plw_floor_bypass` by direct assignment (`scrip.c:1887/1890`), not through the interposed function, so the LD_PRELOAD arm does not test it. The m3 numbers are unmeasured here.
3. **The 134/139 split is *suggestive*, not settled.** Under valgrind `meta_qsort`'s `139` becomes `134` at the same site — consistent with the split being stack-layout noise on ONE mechanism rather than the second mechanism my baton listed as open. **One kernel is not a proof;** do not close that question on this.

## WHAT THIS MEANS FOR THE ROW'S DESIGN CUT

This is `calling-convention-depth-tracked`'s invariant seen from the runtime end: **the trail holds raw C-stack pointers, and nothing tracks whether the frame behind one is still live.** The single global `g_plw_unwind_floor` is not depth tracking — it is one scalar, per-site compensated, and switched off in the whole affected population. It cannot represent two live depths, which is the same shape hq_C found statically (a per-node scalar with nowhere to put a second value).

Two structural shapes follow, and they are **testable before either is built**:
- **(a) Enforce the guarantee the bypass already assumes** — make zframe binding trail only heap-resident cells. If it held, the guard would be unnecessary rather than disabled. **Cheap falsifiable first step: count stack-resident `pl_trail_push` addresses on one kernel.** Today that count is provably non-zero, so (a) is currently false; the question is whether it can be *made* true.
- **(b) Give each trail entry its own liveness stamp** (depth/epoch recorded at push, compared at unwind) so no implementer consults a global at all — this row's "depth carried structurally, no implementer assumes it".

⛔ **Whichever is chosen, the `sendmore` wild-read flavor must be covered too** — a corrupt trail entry is not fixed by validating the address it points to.

## REPRODUCTION

```bash
# witness pair (hq_B's, FINDING-2026-08-30-hq_B-angle2-blocked-by-one-goal-after-a-binding-call-8-line-witness.md)
#   bench__main :- fib(10,F), true.   -> rc=134      bench__main :- fib(10,F).  -> rc=0
scrip --compile -o w.s w.pl && gcc -no-pie w.s -o w -LSCRIP/out -lscrip_rt -lm -Wl,-rpath,$PWD/SCRIP/out
valgrind --tool=memcheck --num-callers=12 ./w        # names pl_cell.h:81
printf 'void rt_plw_floor_bypass_on(void){}\n' > nb.c && gcc -shared -fPIC nb.c -o nb.so
LD_PRELOAD=./nb.so ./w                               # rc=0 -- the guard, merely allowed to run
```

Measured at SCRIP `4435bb29` / corpus `54afdd070`, `-O0`, m4, box load ~2.4/16.
