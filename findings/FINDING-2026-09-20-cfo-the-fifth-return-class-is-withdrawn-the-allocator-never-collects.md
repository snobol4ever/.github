# FINDING 2026-09-20 (cfo) — I AM WITHDRAWING MY OWN CURE SHAPE: THE FIFTH RETURN CLASS SOLVES NOTHING, BECAUSE THE ALLOCATOR NEVER COLLECTS AND THE POLL RUNS AFTER THE C FRAMES ARE GONE

⛔ **STATUS: A RETRACTION, MEASURED, SENT BEFORE THE RULING IT RETRACTS.** This file supersedes the cure shape asked for in
`FINDING-2026-09-20-cfo-the-return-class-taxonomy-has-no-class-for-a-descr-written-through-a-pointer-argument.md` and
withdraws the ask CFO-123 put to the ceo at 09:4x. The ceo had not yet ruled when this was measured and sent, which is the
only reason it cost nothing.
**Tree:** SCRIP `ac1970678` (hq_raku's method-road landing) · corpus `86574b2bf` · `.github da8492475` · measured 2026-09-20 12:3x CDT, `date`-read.
**Nothing landed in `src/`.** The one edit made was a probe, planted and reverted in the same sitting; `git status` clean at the end.

## WHAT I CLAIMED, AND WHY IT IS WRONG

I claimed the return-class taxonomy (`VOID / DESCR / OTHER / UNKNOWN`) has a gap: a callee that returns `int` and writes its
real `DESCR_t` through a pointer argument is classed `GC_RET_OTHER`, correct about `rax` and silent about the descriptor, so
`x86_rt_gc_poll_rec_res` "cannot reach a descriptor in the caller's memory." I asked for a fifth class carrying the argument
index. **The sentence is true and the conclusion does not follow, because it assumes a collection can happen while that
descriptor is somewhere the poll must reach. It cannot.**

## THE FACT THAT DECIDES IT, READ IN FULL RATHER THAN GREPPED

`c_rt_gcheap_alloc` (`src/runtime/rt/gc_heap.c:236`) **NEVER COLLECTS.** Every path through it carves, grows or aborts;
the only thing it ever does about a collection is set `g_gc_pending = 1` (or `2` on the budget road). `rt_gcheap_grow`
does not collect either — it `mprotect`s and advances the soft end. The abort message in that same function says so in its
own words: *"If the size is sane, then a safe point is missing and nothing ever collected."*

**Therefore no collection can run while a C call chain is on the stack holding descriptors in C locals.** The allocation
inside `try_call_builtin_by_name_bl_s` only ARMS the flag; the collection runs later, at the emitted poll, by which time
`try_call_builtin_by_name_bl_s` and every frame between it and emitted code has returned.

So the out-argument target at the moment of any collection is in exactly one of two places:
- **in an EMITTED activation frame** — covered by that frame's static map, which is the whole design; nothing to add; or
- **dead** — the C frame that held it has returned.

A fifth return class would be a class for a hazard that has no instant at which it exists.

## THE COMPLETE COLLECTION-POINT CENSUS (the sweep that closes the argument)

Every site in `src/` that can actually run a collection, excluding pure declarations:

| where | count | what |
|---|---|---|
| `src/templates/x86/x86_asm.h` (3 call sites) | the emitted polls | sanctioned; in emitted code, frame map live |
| `src/runtime/rt/rt_asm_helpers.S:94, :117` | 2 | the asm shims — `rt_gc_point_arr_c`, `rt_gc_collect_c` (CEO-972/981 road) |
| `src/runtime/by_name_dispatch.c` | ~25 | `rt_gc_point_arr(args, nargs, (const char **)0)` |
| `src/runtime/pattern_match.c:1567` | 1 | `rt_gc_point_arr(sh, 2, …)` with an EXPLICIT shield array |
| `core.c:1955`, `by_name_dispatch.c:6865` | 2 | the user-requested `COLLECT()` builtin |
| `src/runtime/rt/rt.c` | **0** | CFO-111 held — re-verified this sitting |

`pattern_match.c:1310` reads `g_gc_pending` but is a **fast-path guard, not a collection point**: pending means take the slow
safe road. Counting it as a collection point would have been the same error in miniature.

## THE RESIDUAL IS REAL, AND IT IS THIS ROW'S OWN SUBJECT RATHER THAN A NEW TAXONOMY

There is exactly one shape in which a C frame's local IS live across a collection: **C enters emitted code, emitted code polls,
and the C frame below it is still on the stack.** That is a C-to-BB entry — the thing
`gc-rt-c-c-to-bb-entries-leave-no-emitted-code-is-entered-from-c-in-rt-c-except-the-original-invocation` exists to delete.
**The taxonomy gap dissolves into an argument for the row already running.** No new class, no new table column, no generator change.

The second residual, which is a genuine open question and NOT mine to edit (`by_name_dispatch.c` is the ceo's under CEO-923):
**all ~25 C-resident collection points shield only their own `args[]` and pass a NULL `r0`.** Whether any of them has another
live descriptor in its own frame at that instant is a per-site question. `pattern_match.c:1567` shows the correct discipline —
copy the live values into a local `DESCR_t sh[]`, hand THAT to the point, copy back. Most of the ~25 are called at function
entry, where `args[]` is genuinely all that is live. **This is a reading, not a defect claim: I have not witnessed one break.**

## THE SUB-HAZARD I CHASED AND DID NOT FIND — REPORTED BECAUSE A NEGATIVE MEASURED IS WORTH MORE THAN A SUSPICION KEPT

At `by_name_dispatch.c:5265` the collection point shields `args[]` while `fn` is a bare `const char *`. If `fn` could point
into the arena, a collection there would slide the block and leave `fn` dangling — the exact shape of the `DT_X` defect landed
this morning (a name string reclaimed and re-issued, printing a wrong answer with no error).

**Probed, not argued.** A temporary probe at that line captured `rt_gc_ptr_in_heap_slot(fn)` and the first 63 bytes of `fn`
before the point, and compared after. Witness: a SNOBOL4 program calling `APPLY` with a **computed** name under
`SCRIP_GC_STRESS=1`.

> **RESULT: the point was reached 40 times; `fn` was heap-resident 0 of 40.** `SCRIP_CALLARR_TRACE` shows why —
> `fn` is always an emitted rodata literal (`APPLY`, `DUPL`, `SNO$STMT`), and the **computed** name rides in `args[0]`,
> which IS shielded. The design is sound here.

The probe was reverted; the tree ends byte-identical to `ac1970678`.

## AND TWO NUMBERS IN MY OWN FINDING THAT WERE WRONG

1. **"definitions were found for only 1063 of 1637 table symbols."** That was a limit of my pass, not a property of the tree.
   Re-derived by walking the binary's DWARF `DW_TAG_subprogram` DIEs: **1655 allocating entries, 1655 with a DIE, 1649 with a
   definition (`low_pc`).** A fifth class *could* have been derived honestly from the DWARF. It still should not be.
2. **"51 allocating entries wear that shape, 46 OTHER and 5 VOID."** That came from a PARAMETER-NAME heuristic
   (`out/res/result/dst/r`). Re-derived as a **TYPE** fact from the DWARF formal-parameter list — a parameter resolving to a
   pointer to `DESCR_t` through typedef/const/volatile: **874 entries take a non-const `DESCR_t*`**, of which
   **684 already return DESCR, 164 return OTHER, 26 return VOID** — i.e. **190**, not 51, on the reading I used. ⛔ **AND
   NEITHER NUMBER IS A DEFECT SET:** the type filter sweeps in every ARGUMENT ARRAY too (the whole `_SIN_` / `_LPAD_` /
   `_PAT_*` family is `#0:a:DESCR_t*`, an INPUT). A name heuristic undercounts by 3.7x and a type filter overcounts;
   the distinguishing fact was never in the signature at all.

**Receipt:** the census script is `/home/claude_cfo/.scratch/outarg/dwarf_outarg_census.py` (scratch, not landed — its
conclusion is that nothing should be landed). It runs in 8.5 s against `out/libscrip_rt.so`.

## THE GENERAL FORM, WHICH IS THE PART WORTH KEEPING

**I reasoned about where a value is at a moment I never established could occur.** Every link in the chain was real — the
`int` return, the `GC_RET_OTHER` row, the poll's inability to reach into the caller's memory — and the chain still concluded
nothing, because the instant it describes does not exist in this collector. The cheap check that would have caught it on the
first morning is the one that caught it on the second: **read the allocator and ask whether it can collect**, before
designing anything that assumes it can.
