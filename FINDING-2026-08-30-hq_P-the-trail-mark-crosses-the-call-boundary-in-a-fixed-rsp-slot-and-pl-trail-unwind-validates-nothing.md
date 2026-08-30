# FINDING: the causal chain is closed — the **trail mark** crosses the call/return boundary in a **fixed `[rsp+32]` slot**, arrives wild, and `pl_trail_unwind` validates **nothing**, walking the trail array off its front

**Seat:** hq_P (TRIO) · **Date:** 2026-08-30 · **Row:** `calling-convention-depth-tracked` · **Source edits: NONE** · Follows `FINDING-2026-08-30-hq_P-pl-trail-unwind-writes-dead-cstack-...` (same session, `.github` `3b349119`)

## THIS IS THE ROW'S OWN INVARIANT, INSTANTIATED AND MEASURED

The row's GOAL names the invariant: *"a fixed rsp-relative offset trusted across a call/return boundary with NOTHING tracking accumulated depth"*, and lists among its witnesses *"the SCRIP_ZD=0 f_gamma **fixed-[rsp+32]** witness."* That witness is no longer a name. It is the trail mark, and here is the whole chain.

**1. The mark is produced and parked at a fixed rsp-relative slot** (emitted, `l__/2`):
```
        call  rt_pl_dop_trail_mark@PLT
.L..._101:
        mov   qword ptr [rsp + 32], rax      <-- the mark, at a FIXED offset
```
**2. A different box reads it back from that same fixed slot and hands it to the runtime:**
```
n28_call_prolog_α:  mov  rax, qword ptr [rsp + 32]    <-- same slot
                    mov  qword ptr [rsp + 80], rax
                    lea  rdi, [rsp + 80]
                    call rt_pl_dop_trail_unwind@PLT   (and the rt_pl_dop_unwind_nothrow twin at n23)
```
**3. It arrives WILD.** Measured with a gdb probe on every unwind call:
- `sendmore`: **9,368 consecutive calls with sane marks** — `(mark,top)` = `(50,56)`, `(49,50)`, … — then call **9,369**, the fatal one, passes **`mark = -76336`** with `top = 73`.
- `tak`: dies at the same line with **`mark = -220658952`**, reached through the *other* entry point, `dop_unwind_nothrow` (`by_name_dispatch.c:1412`). Frame #2 of that stack is `0x0000000000000000 in ?? ()` — the `rip = 0` seen in earlier sessions.

⭐ **9,368 good then 1 bad is the row's thesis in one number:** the convention is *"never enforced, only usually satisfied."*

**4. `pl_trail_unwind` trusts the mark absolutely** (`pl_cell.h:77–82`):
```c
static inline void pl_trail_unwind(pl_trail_t *t, int mark) {
    pl_trail_ent_t *ents = (pl_trail_ent_t *)t->area.base;
    while (t->top > mark) { t->top--;
        if (!plc_dead_cstack(ents[t->top].addr)) *ents[t->top].addr = ents[t->top].old; } }
```
There is **no bound check of any kind.** With `mark = -76336` the loop drives `top` from 73 down through `0`, `-1`, `-2`, … indexing `ents[-1]`, `ents[-2]` — **reading pointers from before the array and writing 16 bytes through each.** That is one mechanism producing every flavor previously catalogued: `sendmore`'s *"Invalid read … not stack'd, malloc'd or (recently) free'd"*, the dead-stack writes, and the **`top = -1` I measured in 9 of 21 kernels** (they are caught mid-underflow).

**5. The one guard that could have bounded the damage is switched off** in every Prolog zframe program — the prior finding.

## THE PREMISE BEHIND THE GUARD IS NOT MERELY FALSE, IT IS INVERTED

Walking the live trail at the fatal stop in all 21 van Roy kernels (gdb, classifying each entry's `addr` against `/proc/self/maps`):

```
ACROSS 21 KERNELS:  stack-resident = 1951    HEAP-RESIDENT = 0    other = 504
```

The bypass commit `77925561` justifies disabling the guard with *"Prolog zframe graphs **guarantee all trail entries are PLJ-heap-resident**."* **Zero of 2,455 live trail entries are heap-resident.** The guarantee is not approximately wrong; it is the exact opposite of what the trail contains. ⛔ **This kills design option (a)** (*enforce the guarantee so the guard becomes unnecessary*) as a small enforcement job — nothing is heap-resident today, so (a) is a wholesale change of where Prolog variables live, not a tightening.

## ⛔ WHAT IS MEASURED VS WHAT IS INFERRED — the row's own discipline, applied to my own result

**MEASURED:** the emitted store/load pair at the one fixed slot; the wild mark values and their call ordinals; the absence of any validation in `pl_trail_unwind`; the 1951/0/504 trail composition; `top = -1` in 9 kernels; two distinct runtime entry points (`:1412`, `:1484`) both reached from emitted `n<NNN>_call_prolog_bx`.

⚠️ **INFERRED, NOT WITNESSED:** *that a second activation at the same depth is what overwrites `[rsp+32]`.* The emitted shape (one fixed offset, no depth term) and the wild values are consistent with it and I know no other candidate — but **I did not watch the clobbering write happen.** Do not promote this to fact without a witness; five predicates on this row have already died at exactly this step, and the last two died specifically because they were not run against the passing set.

## THE CURE DIRECTION, AND ONE CONTAINMENT DECISION THAT NEEDS A RULING

⭐ **The real cure is this row's mandate: the mark must not live in a depth-indexed slot.** It is per-*activation* state stored at a per-*depth* address. That is hq_C's structural finding (a per-node scalar with nowhere to put a second value) reaching the runtime through the one value that indexes memory.

⚠️ **SEPARATELY — and this is a decision, not a fix I am taking:** `pl_trail_unwind` is the **single consumer** of every mark, from ~130 call sites. Its own contract `0 <= mark <= t->top` is therefore checkable in **ONE place**, which is the opposite of site patching. Doing so would convert unbounded out-of-bounds read+write into a contained, diagnosable failure.
⛔ **But it must REFUSE LOUDLY, never clamp silently** — a silent clamp turns today's honest crash into tomorrow's wrong answer, and this project has a standing refuse-not-repair rule for exactly that. It also interacts with the optbypass watermark gate and would change crash behaviour across every Prolog program, so it is a ruling for the design cut, **not a change I made this session.**

## REPRODUCTION

```bash
# mark probe: breakpoint on dop_trail_unwind, record (args[0].i, g_pl_trail.top) per call
gdb -q -batch -x marks.py -ex run ./sendmore     # 9368 sane, then mark=-76336 top=73
gdb -q -batch -ex 'break __stack_chk_fail' -ex run -ex 'bt 6' ./tak   # mark=-220658952 via dop_unwind_nothrow
# trail composition: walk (pl_trail_t *)&g_pl_trail entries, classify addr against /proc/PID/maps
```
⚠️ `g_pl_trail` has a conflicting `extern char g_pl_trail[]` declaration (`bb_define.cpp:17`) that makes gdb read it as `char[]`; cast it — `*(pl_trail_t *)&g_pl_trail` — or the walk silently fails.
⚠️ A breakpoint on `dop_trail_unwind` alone MISSES `tak` entirely (0 hits): the second entry point `dop_unwind_nothrow` is a different function. Probe both, or conclude nothing from a zero.

Measured at SCRIP `4435bb29` / corpus `54afdd070`, `-O0`, m4, box load ~2.3/16.
