# FINDING — the nested apply-to-generator crash is a 16-byte STACK MISALIGNMENT on the coexpr's own
# thread, first exposed by glibc's SSE-using malloc-arena bootstrap — NOT a `pthread_create`
# thread-descriptor fault as the row's own GOAL text and the interim refusal message both describe

**seat13 · 2026-08-29 · row `icon-n2-apply-nested-coexpr`**

**Not cured — root-caused via gdb, corrects the untested mechanism description in the row's own GOAL
text and ceo's own FINDING §3. Nothing committed except the diagnostic message correction + an
env-gated bypass for the next investigator (both described in §4); the refusal itself is unchanged
default behavior.**

## 0. What the row's own text claims, and why it was never actually tested

The row's GOAL and ceo's `FINDING-...-apply-call-generator-cured-coswitch-rax-clobber-plus-n2-region-
window.md` §3 both describe the mechanism as: *"the second gcheap stack window hands `pthread_create` a
top-of-stack that faults on the thread-descriptor write."* No gdb trace is cited for this in any FINDING
on this row — it reads as a plausible inference from the code shape (a second `pthread_attr_setstack`+
`pthread_create` pair, using the same window-computation code as the first), not a measured fact.

## 1. Reproduced under gdb — the actual fault is somewhere else entirely

Temporarily bypassed the interim refusal (env-gated, `SCRIP_N2_APPLY_NESTED_DIAG=1`, see §4 — default
behavior is unchanged) to let the real crash occur, then ran the row's own DONE-WHEN repro
(`outer`/`inner`, `every write(outer ! [10])`) under gdb:

```
Thread 2 "scrip" received signal SIGSEGV.
0x00007ffff3eaa0f4 in alloc_new_heap (size=2904, top_pad=131072, ...) at ./malloc/arena.c:395
#0  alloc_new_heap
#1  new_heap
#2  _int_new_arena
#3  arena_get2
#5  tcache_init
#7  __libc_calloc
#8  rt_proc_call_gen_h (name="inner", ...) at rt.c:1108        <- g = calloc(1, sizeof *g)
#9  rt_call_value_gen_h  (by_name_dispatch.c:929)
#10 rt_call_apply_gen_h  (by_name_dispatch.c:946)
#12 rt_genp_spine_enter_n2 (rt.c:998)
```

**This is `outer`'s own already-running coexpr thread (Thread 2), executing its first-ever `calloc()`
call** — the one `rt_proc_call_gen_h` makes at line 1108 to allocate the bookkeeping struct for the
generator it's about to spawn (`inner`). `pthread_create` for `inner`'s own thread is never reached —
the crash fires three lines of C earlier, inside glibc's lazy per-thread malloc-arena bootstrap
(`tcache_init` → `arena_get2` → `_int_new_arena` → `new_heap`), which every thread runs exactly once, on
its first heap allocation. The faulting instruction is `movaps %xmm0,-0x40(%rbp)` — an SSE store that
requires 16-byte alignment.

## 2. The stack IS misaligned, confirmed directly, not inferred from the instruction alone

At the crash: `rbp = 0x7fff8bbff768`. `0x768 mod 16 = 8`. **A function's `rbp` after a standard `push
rbp; mov rbp,rsp` prologue must be ≡ 0 (mod 16) under the x86-64 SysV ABI** (a `call` leaves RSP ≡ 8 mod
16; the prologue's `push` restores 16-alignment). `rbp` here is 8 (mod 16), off by exactly one 8-byte
slot — the textbook signature of an odd number of unbalanced 8-byte pushes somewhere upstream on this
thread's own stack, not a page-level or gross allocation failure (the region itself is mapped; `movaps`
faults on *alignment*, not on an unmapped page, and nothing else on this thread's own call chain up to
this point had crashed).

## 3. What this means for where the fix belongs

**The bug is not "the second window is unmapped."** It is that **some coexpr thread's own stack ends up
persistently 8 bytes off the ABI-required 16-byte alignment**, and the *only* reason this has looked like
an N-2-nesting-specific, pthread_create-specific bug is that ordinary Icon-generator control flow
(`suspend`/resume, register-only) never happens to execute an instruction that enforces the alignment
requirement — glibc's malloc bootstrap is the first thing on this thread's own path that does. **Any code
path that calls into SSE-using library code from within a coexpr thread should reproduce this**,
independent of nesting a second generator specifically; nesting is just the first place in this codebase
that happens to call `calloc` from inside a coexpr body. Candidates for the actual off-by-8 source, not
verified this sitting: `rt_coexpr.c`'s `scrip_coswitch` window math (`al`/`lo`/`sz`, all built from
page-aligned quantities so page-level alignment looks sound on inspection, but glibc's own placement of
its `struct pthread` TCB at the top of a caller-supplied stack region is not verified here to preserve
16-byte alignment past that computation); or the N-2 protocol's own "five-word entry stack" push
(`[γ ω REGION L7 depth-seed]` — 5 × 8 = 40 bytes, itself not a multiple of 16, per ceo's own FINDING's
description of `rt_genp_spine_enter_n2`) landing on top of whatever the thread started with. **Not
traced further this sitting** — distinguishing between these needs breaking at the coexpr thread's true
first instruction (`rt_genp_thread_entry`/`scrip_co_trampoline`) for `outer`'s OWN creation and checking
`rsp mod 16` there, before any N-2 protocol code has run, which was attempted but the breakpoint did not
resolve against the running thread in this session's gdb invocation (worth retrying with a
library/file-qualified breakpoint, e.g. `break rt_coexpr.c:scrip_co_trampoline`, or breaking on
`pthread_create`'s return in the parent thread and inspecting the child's initial context directly).

## 4. What's landed, and what is not

**Landed** (SCRIP, purely additive, default behavior byte-for-byte unchanged — verified: full D2 witness
set still ALL-GREEN, `emit_no_lang` gate clean, Icon smoke 14/14 both modes, the nested repro still
refuses with rc=134 by default):
- The refusal message in `rt.c:1105` corrected to describe the verified mechanism (stack misalignment
  inside malloc bootstrap) instead of the untested "pthread_create thread-descriptor" guess, so the next
  reader doesn't have to re-discover this.
- `SCRIP_N2_APPLY_NESTED_DIAG=1` env-gated bypass of the refusal, **diagnostic only, not a fix** — lets
  the real crash occur under gdb without re-deriving the bypass. Off by default; setting it in anything
  but a debugger reproduces a real, uncaught SIGSEGV.

**Not landed:** an actual fix. This needs the §3 root-cause split (which of the two candidate mechanisms,
or a third, actually produces the off-by-8) done with a resolved breakpoint at the coexpr thread's true
entry, which is real remaining work, not a quick follow-on.

## 5. Disposition

Mailed hq_C (parent row `icon-n2-generator-activation-frames`'s authority) and ceo (whose FINDING this
corrects) — not blocking on a reply. This row's own DONE-WHEN is unchanged (still correctly failing,
since no cure landed): the D2 witness set is green and the nested case still refuses loudly, matching the
row's own required interim state.
