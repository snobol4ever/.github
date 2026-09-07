# FINDING — the by-name generator region was the one Icon activation on the arena; it is now carved on the coroutine's own machine stack

**Seat:** hq_U (HQ-UNIFY) · **Date:** 2026-09-06 · **Tree:** SCRIP `ef9ae0d15` (the landing; measured first on `fb2939930`-dirty, re-proven after rebase onto `ba3ab22ac`)
**Row:** `by-name-dispatched-generator-regions-and-proc-frames-come-from-the-zls-arena-not-the-machine-stack-carve-them-per-the-frame-law` (rank 1, hq_U)
**Law:** RULES.md § BB FRAME-PLACEMENT CRITERION; **Lon 2026-09-06 20:18 CDT** *"No activations on the heap."* and 20:2x *"Generators for Icon have been on the stack with RSP and RBP the whole time so I do not know what has changed so. NO ACTIVATIONS on the HEAP."*

## ⭐ Lon was right, and the measurement says so

A **direct** call to an Icon generator makes **zero** arena allocations. Nothing had moved compiled generators off RSP/RBP. Exactly one path reached for the arena, and only when the generator was reached **by name** (through a procedure value).

## Fail-once measurement, before any cure

Three Icon witnesses, `SCRIP_ZETA_TELEM=1`, both modes. The `[ZLS]` report only prints once `rt_zls_alloc` has been called, so its absence is the zero.

| witness | shape | before | after |
|---|---|---|---|
| `wC_control_direct` | `every x := gen()` — direct call | no `[ZLS]` (zero) | zero |
| `wA_gen_byname` | `p := gen; every x := p()` | **`allocs=1 bytes=224`** | **zero** |
| `wB_proc_byname` | `p := plain; p(41)` | no `[ZLS]` (zero) | zero |

Identical in m3 and m4. All three match the Icon oracle (`/home/resources/icon-master/bin/iconx`) exactly — `1 2 3`, `1 2 3`, `42` — before and after, rc=0.

## The defect

`rt_proc_call_gen_h` (`rt.c:1121`) allocated the by-name generator's ζ region with `rt_zls_alloc(gen_region_ft + 48)`. `rt_zls_alloc` (`zeta_alloc.c:30`) is an **arena** — `A_COEXPR` zblocks, or `rt_ws_alloc` above 64 KB. That region is the generator's own activation storage, so it was activation storage off the machine stack.

⭐ **The sibling paths in the same file already complied.** `rt.c:928`, `1614` and `1874` all carve their by-name proc frames with `alloca` + `rt_frame_prep`. The generator arm was the one that reached for the arena — an outlier in its own file, not a house style.

## The cure

The region is consumed only inside `rt_genp_entry_c`, which runs **on the generator's own coroutine thread** (`scrip_co_ctx_init` → a pthread with a real stack). `rt_genp_spine_enter_n2(fn, region)` passes the region **by value** into the callee's 6-word entry frame — it is not a stack switch — so the body's frames grow below it.

So the region is now carved with `alloca` in `rt_genp_entry_c`, 16-aligned and zeroed, in the frame that encloses the body call. That is the frame law's own shape: carved in the enclosing activation, released by unwinding when the coroutine dies. The arena call and the matching `rt_zls_release` in `rt_genp_destroy` are deleted, and the now-unset `region` field is removed so no reader is misled by a permanently-NULL pointer.

## ⛔ The check that could have made this cure silently wrong

Moving storage between root sets can break GC reachability. Verified before landing, not assumed: `gc_heap.c:549-553` walks every linked coroutine and scans `scrip_co_stack_of(c, &lo, &hi)` as a root — the same conservative sweep that already covered the generator's own frames — while `gc_heap.c:584-586` walks the ZLS frame chain. **Both** root sets are scanned, so the region stays reachable; it merely changes which sweep finds it.

## ⛔ Site B is NOT cured, and here is why

The row names *regions and proc frames*. The second `rt_zls_alloc` caller, `rt.c:1138` (the by-name proc frame), **survives**, deliberately:

- **It cannot take an `alloca`.** The frame escapes via `*hout = fb` and is re-entered later by `rt_proc_resume_frame` / `rt_proc_resume_frame_h` after `rt_proc_call_gen_h` has returned. A stack carve in that C frame would dangle on the first resume. It is a genuine suspend-surviving frame whose enclosing activation is a runtime C function that returns.
- **Its only reach is parked.** Site B is gated on `!p->jmp_entry`, and `jmp_entry` is set to `strncmp(pname, "gram__", 6) != 0` — so it is reachable only by `gram__*` procs, which are built at `lower_raku.c:993`. **Raku is `PARKED-LON-HOLD`.** No open language reaches it.
- **The right cure is caller-side.** Per the criterion, a suspend-surviving frame carves in the **enclosing graph's** RBP activation frame — here the compiled caller that made the by-name call, via the GENP-SPINE s92 `callgen.act` slot the compiled path already reserves (`zeta_storage.c:185,192`). That spans the emitter and `by_name_dispatch.c` and is a follow-on row, not this flip.

**Filed as follow-on:** `by-name-proc-frame-at-rt-1138-needs-the-caller-side-callgen-act-carve-reachable-only-through-parked-raku-grammars`.
