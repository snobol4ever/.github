# FINDING 2026-08-27 seat05 — PZ-4 SIGILL: the GC seam-scan hypothesis is refuted; the crash traces to the global pending-cursor mailbox at a fixed frame offset

Row: `prolog-pz4-gamma-retain-activation-frames`. Continues the SIGILL witness left by this seat's own prior FLEET-8
pass (`FINDING-2026-08-27-seat05-pz4-omega-wire-never-loaded-bcps-spine-gen-arm.md`). No SCRIP/corpus source changed
this pass — pure investigation, on fresh pristine HEAD (SCRIP `c75f086d`, corpus `d5961675d`, 11 commits newer than
the prior pass, none of them touching this mechanism — see below).

## Repro (unchanged)
```
fact(a).
fact(b).
fact(c).
main :- fact(X), write(X), nl, fail ; true.
```
Oracle `swipl` prints `a,b,c`. SCRIP mode-4 (`--compile --target=x86`, as+gcc, linked against `out/libscrip_rt.so`):
SIGILL, `rip` lands on a stack address (`0x7fffffffdf3a`-ish, varies run to run by a few bytes), `rax` a stack
address adjacent to `rip`, `rdx = rax - 8`. Mode-3 (`--run`) SIGSEGVs on the same program (unsymbolized JIT-slab
address, consistent with the existing "same mechanism, m3 has no symbol table" reading in seat07's LEDGER note).

## Hypothesis tested and REFUTED: GC seam-scan corrupting the parked callee-saved registers

The prior pass's own `## NEXT` ended on an unconfirmed hypothesis: that `rt_gc_point_arr_c`'s seam-repair scan
(`gc_zeta_frame`, `gc_heap.c`) might misidentify R15 (=CP in Prolog graphs, per the register contract) or R12 or one
of the other five parked callee-saved registers as a heap pointer and rewrite it, since the scan conservatively
reinterprets every 8/16-byte-aligned window of the parked-register region as candidate `DESCR_t`/raw-pointer data
(`gc_heap.c:559-573`) with no way to know that THIS particular scan region is six raw registers, not a real
zeta/activation frame laid out by the compiler.

**Tested directly, both directions, per RULES.md's two-part-proof rule:** instrumented every call to
`rt_gc_point_arr_c` (function-name breakpoints — `break gc_heap.c:<line>` would not resolve until the runtime `.so`
was loaded; `tbreak main` first, then function-name breakpoints after, works) to dump all six parked registers
(`[floor+0..40]` = r15,r14,r13,r12,rbp,rbx) immediately on entry and again immediately after `rt_gc_point_arr`
(the asm veneer) returns (`break *(rt_gc_point_arr+24)`, the instruction after `call rt_gc_point_arr_c@PLT`).

**Result: 9 GC points fire before the crash on this witness; all 9 are byte-identical PRE vs POST, all six registers,
every time.** R15 in particular is the constant `0x7ffff7ffd000` across all 9 hits (looks like a loader/vdso-region
address, i.e. plausibly never assigned by this program's own codegen before the crash — a second, smaller,
un-investigated observation, not this pass's finding). **The seam-scan repair is not the cause of this crash.**
Recorded here specifically so the next session does not re-spend a pass re-deriving and re-testing the same
hypothesis — the instrument (script below) is cheap to re-run if a *different* witness ever wants re-checking.

Instrumentation script (gdb batch, reusable): `tbreak main` → `run` → set `break rt_gc_point_arr_c` +
`break *(rt_gc_point_arr+24)` (both resolve once the runtime `.so` is loaded) → `commands` on each to print
`floor`'s 6 words and `continue` → final `continue` to the crash. ~15 lines, no source-file path resolution needed
(avoids the `break gc_heap.c:NNN` "No source file named" trap — function-name/computed-address breakpoints resolve
fine against the loaded `.so`; plain `file:line` breakpoints set before `run` do not, even with
`set breakpoint pending on`).

## What the crash actually traces to

Walking forward from the ruled-out hypothesis, via `ASM-DIFF-FIRST` on the emitted `.s` plus gdb on the runtime C:

`n43_call_proc_staged_β` (the backtrack/retry entry for `fact(X)`'s choice point) pops a saved retry continuation
via `rt_pl_cp_pop3()` (`rt.c:1706`) — **a GLOBAL array `g_pl_zf3_stack`, not frame-resident** — getting back a code
address (`cont`) plus a trail-mark pair (`tm_lo`/`tm_hi`). It then calls `rt_pl_zf_resume_set(cont, tm_lo, tm_hi,
tm_off=32, cursor_off=448)` (`rt.c:1721`), which stashes all of it into **five more process-wide globals**
(`g_pl_zf_pending_cursor` and friends). The callee's own prologue helper, `rt_jmp_frame_lexprep2` (`rt.c:1629`),
later consumes those globals into the FRESH activation frame `fb` at **fixed byte offsets**: the trail-mark pair at
`[fb+0]`/`[fb+8]` (doubling as the "have I already suspended" flag every SUSPEND node's α-port checks — see the
comment at `rt.c:1637-1642`) and again at `[fb+32]`/`[fb+40]`, and the real code-address cursor at `[fb+448]`.
Verified live (gdb, `break rt_jmp_frame_lexprep2`): call #3 in this repro carries a real, plausible code address
(`cursor=0x4015a4`, inside the `-no-pie` binary's own low `.text`) — **the stashed VALUE is not obviously wrong**;
the mechanism is a **global mailbox handing off through a fixed offset**, and the crash's stack-address-shaped
`rip`/`rax`/`rdx` are consistent with that offset being read back against the wrong frame depth, or the trail-mark
slot being read where the cursor slot was meant, once "unbounded intervening stack growth" (prints, nested calls)
has happened between the write and the read.

**This is not a new bug class.** It is the same shape seat07's FINDING already named for `disj0`'s γ-port ("reads a
stale fixed-rsp-relative continuation slot after unbounded intervening stack growth") and the same shape this row's
own DONE-WHEN prose and the ceo design-check both point at ("retry/resume state kept at a fixed offset or in a
shared global, with no protection across a γ-suspend↔β-resume window"). What this pass adds: a **second, independent
concrete code path** (`n43_call_proc_staged_β` → `rt_pl_cp_pop3`/`rt_pl_zf_resume_set` → `rt_jmp_frame_lexprep2`,
distinct from `disj0`'s γ-port) hitting the identical mechanism — corroborating evidence that the wall is structural
(the global-mailbox/fixed-offset design itself), not a one-off bug local to `disj0`, matching Lon's own read of this
row: "the structural cure... retained ζ-ACTIVATION frames give the resume state an owner."

Not chased further this pass (flagging, not fixing — out of scope until the structural cure lands): whether
`g_pl_zf_pending_cursor` gets consumed by the SAME frame depth that produced it, or a shallower/deeper one; whether
the crash is specifically the trail-mark slot (`[fb+0]`/`[fb+8]`) being jumped through instead of `[fb+448]`, or a
different offset confusion. The mechanism above is enough to place this squarely inside PZ-4's own problem
statement rather than a peripheral defect worth an independent scoped patch (the same conclusion hq_C already
reached from a different witness — see hq_C's `## NEXT` block in the task file, "do not re-derive the wall").

## Coordination: hq_P on item 2 (`icon-n2-generator-activation-frames`)

Checked before doing anything else this pass (claim file, QUEUE.tsv, hq_P's own task file): item 2 (the shared
RBP-promotion mechanism this row's retain slice needs) is still `## NEXT-ITEM-2 ... IMPLEMENTATION NOT STARTED` as
of hq_P's own s277 pass — items 1/1b (generator ζ addressing) are landed; item 2 itself is not.

hq_P then answered this seat's earlier coordination mail directly (full text in postoffice, `.msg` file
`coord-pz4-needs-n2-item2-promotion`), in substance: item 2 is genuinely blocked on a design guard (a
forward-reference hazard — a host's carve can be silently too small if the callee's frame-byte count isn't recorded
yet when the host graph is emitted) and is further from landing than hoped; **do not wait for it.** hq_P rules that
this row's independent SIGILL work is the better use of a pass and explicitly declines to hand over a shared-glue
row to work in parallel (avoiding exactly the four-witnesses-one-shape risk). hq_P also corrected a premise: measured
live, `main`'s prologue on this tree is `sub rsp,8; push rdi; push rsi` with **zero** rbp references anywhere —
there is no RBP frame on ANY frontend today to carve into; creating one IS item 2, a caller-side change. (This
seat's own gdb session independently landed on the same fact: `tbreak main` → `sub rsp, 8` as the first instruction,
no rbp setup.)

**hq_P's concrete unblocking instruction, for whoever picks this up next:** the DESIGN half of Prolog's
`zframe_graph` integration does not depend on item 2 landing. Build it against the INTERFACE — a
`callee_frame_bytes(name)` accessor over the existing `proc_fb_buf`/`proc_names_buf` registry, plus an RBP
activation frame assumed-carved-by-the-caller — recording retry/resume state as BB LOCALS in that frame (per
`ARCH-PROLOG-DESCR-ZETAS-hq_C.md` §5) instead of the `g_pl_zf_pending_*` global mailbox this FINDING traces above.
Land the Prolog-side-only parts; leave the single call into the promoted frame as the seam item 2 plugs into later.
**Explicitly do not build a temporary Prolog-only promotion behind that seam** — that is the disease the whole
coordination was trying to avoid, and hq_P names a temporary one as the hardest kind to delete.

## Measured floor this pass (pristine `-O0`, SCRIP `c75f086d`, no source changes)
`rung13` PASS=0 FAIL=5 · `rung14` PASS=2 FAIL=3 · `rung15` PASS=2 FAIL=3 (within the already-documented
non-determinism, ADDENDUM to the omega-wire FINDING — PASS varies 1-3/5 run to run, pre-existing, not this pass's
doing) · smoke m2/m3/m4 4/5 each (`clause` fails, pre-existing, untouched). **Unchanged from the last measured
floor** — expected, since this pass made no source edits. Not re-run: SNOBOL4/Icon control arms (no code touched,
nothing to control for).

## Next step (see task `## NEXT` for the live baton)
Read `ARCH-PROLOG-DESCR-ZETAS-hq_C.md` §5, then build the Prolog-side `zframe_graph` BB-locals design per hq_P's
instruction above, seamed (not shortcut) against item 2.
