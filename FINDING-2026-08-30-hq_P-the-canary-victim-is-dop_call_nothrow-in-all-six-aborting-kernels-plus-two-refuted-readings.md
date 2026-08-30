# FINDING — the smashed frame is `dop_call_nothrow` in **6 of 6** aborting Prolog kernels, always reached from
# the Prolog trail-unwind path. That localization is solid and reproducible. Two mechanisms I read off it are
# NOT: "overlapping live activations" measures **0 in crashers and passers alike**, and the instruction the
# canary watchpoint caught turned out to be an ordinary `push %rbp`. Reporting the localization and both
# refutations; **no mechanism is claimed.**

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`.** Diagnosis only; nothing committed to SCRIP.

## 1. ✅ THE SOLID RESULT — one victim, six kernels

Asking glibc which frame it caught, rather than guessing: `break __stack_chk_fail`, then read the backtrace past
the libc frames.
```
nrev · ham · zebra · meta_qsort · nreverse · queens_8   ->  ALL SIX:
  #8  dop_call_nothrow            by_name_dispatch.c:1516
  #9  rt_pl_dop_trail_unwind / rt_pl_dop_unwind_nothrow   :1589 / :1590
  #10 n<NNN>_call_prolog_bx       (emitted)
```
**6/6, same function, same call shape** — the Prolog **trail unwind** (backtracking) path, entered from emitted
code. `dop_call_nothrow` is also the function that pins `g_plw_unwind_floor = __builtin_frame_address(0)` and
restores it after `body()` — i.e. it publishes a **stack-depth-dependent global**, which is at least the right
neighbourhood for this row.
⭐ **This came free from a signal the program was already emitting.** The 6 aborting kernels print
`*** stack smashing detected ***`; glibc knows whose canary died and will say so. Four guessed predicates cost
far more than this one question did.

## 2. ⛔ REFUTED READING #1 — "two live activations at the same frame address"

A canary watchpoint's last write before the abort resolved to `dop_call_nothrow+9`, which is inside the
function's own **prologue**. I read that as a later invocation building its frame on top of a still-live earlier
one. **It is not.** `+2` is `push %rbp`, so the write is the ordinary prologue push of a stack-valued `rbp` —
landing on an address that had been a canary slot of an invocation that had **already returned**. Ordinary
stack reuse.
✅ Tested rather than argued: instrumenting entry and `ret` of `dop_call_nothrow` and flagging an entry whose
frame address is already live gives **REENTRY-AT-LIVE-FRAME = 0** on crashers **and** passers:
```
CRASHERS  nrev 61 events / 0   ham 259 / 0   zebra 21 / 0
PASSERS   sendmore 51,082 / 0  tak 31,804 / 0        cal REFUSED (0 events — did not run)
```
Entries and exits are balanced. **The frames do not overlap.**

## 3. ⛔ REFUTED READING #2 — the corrupt arguments

`nrev`'s frame #8 shows `body=0x0, args=0x0, nargs=1`, which is impossible on the source path
(`rt_pl_dop_trail_unwind` guards `nargs == 1` and passes `dop_trail_unwind` as `body`, never NULL). I nearly
reported that as a second anomaly.
⛔ **It is not evidence.** The canary is smashed *by definition* in that frame — so gdb is reconstructing
arguments from memory that is known-corrupt. **Once a frame is smashed, everything the debugger says about that
frame is suspect, including the values that make it look interesting.** `ham` and `zebra` show plausible
arguments in the same slot, which is what a corrupted-vs-intact read looks like.

## 4. Where this leaves the row

Five predicates have now been tested and refuted: wall count · wall-dominates-a-fixed-pop · head-bypass edges ·
slot-written-twice-without-a-read · **frame-reentry-at-a-live-address**. ⭐ The last two are mine from this
session and both were refuted **by running them against the passing set**, which is hq_C's rule and is now the
only thing that has reliably worked.
✅ **What is NOT refuted and is worth inheriting:** the localization above (6/6, `dop_call_nothrow`, trail
unwind), the static-impossibility proof (`1b64da5c`), and the SIGSEGV/SIGABRT unification (both are
out-of-bounds stack writes, differing in what the bad write lands on).
⛔ **NO MECHANISM IS CLAIMED and no sixth predicate is offered.** The honest state is: something writes past
`dop_call_nothrow`'s frame on the trail-unwind path, in 6 of 6 aborting kernels, and I have not found what.
⭐ **The next question I would ask is the one that produced §1** — not "what predicate separates the sets" but
**"what is the program already telling me that I have not asked for?"** The canary named the victim in one
command after four predicates named nothing in a day.
