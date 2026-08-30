# FINDING: forcing the SNO$STMT hook unconditionally-on doesn't just cost more — it crashes

**Seat:** seat16 (FLEET-16) · **Date:** 2026-08-29 · **Row:** `core-err-stmt-never-advances`
(postoffice task, not a `.github` GOAL) · **Found while:** attempting NEXT ACTOR step 2 of that
row — "measure `SNO$STMT`-always-on's actual cost" — per its own instruction to check instruction
count as an alternative to wall-clock. Builds on the row's own prior FINDING,
`FINDING-2026-08-29-seat16-core-err-stmt-fixed-but-only-when-stmtkw-tracking-is-compiled-in.md`.

## WHAT I WAS TRYING TO DO
The row's landed fix only tracks `&STNO` (and reports the correct error statement number) when the
compiled source itself references `&STNO`/`&LINE`/etc. — `g_sno_uses_stmtkw` gates whether
`lower_snobol4.c:2351`'s `SNO$STMT` hook is emitted at all. Most programs don't reference those
keywords, so most runtime errors still report statement 0. The row's own NEXT ACTOR guidance
framed the remaining work as a **pure performance question**: measure the cost of making the hook
unconditional, and if it's cheap, remove the gate.

## MEASURED: it's not cheap — it's broken
I patched `lower_snobol4.c:2351` from `if (g_sno_uses_stmtkw)` to `if (1)` (comment marked TEMP,
reverted before finishing — tree is clean, see LEDGER), rebuilt pristine (`RT_OPT=-O0`, confirmed in
the build log), and ran three existing benchmark kernels (`corpus/benchmarks/snobol4/{arith_loop,
fibonacci,array_sum}.sno`, standalone invocation, none reference the stmt-tracking keywords) under
`./scrip <file> < /dev/null`.

**All three produced ZERO output and exited 1**, versus correct output on the unpatched baseline:

| kernel | baseline | patched (`if(1)`) |
|---|---|---|
| arith_loop | `arith_loop(10) = 10` / `arith_loop(1000) = 1000` | *(nothing — crash)* |
| fibonacci | 17 lines of `fib(N) = ...` | *(nothing — crash)* |
| array_sum | 2 lines of sums | *(nothing — crash)* |

All three print the same runtime error, with the row's own already-landed fix correctly reporting a
real (non-zero) statement number — the irony being that the very mechanism this row is trying to make
universal is what's now reporting the crash it caused:
```
** Error 22 in statement 11
   Undefined function called
```
All three kernels share one trait relevant here: **all define and call a user procedure via
`DEFINE(...)`.** I was not able to confirm DEFINE specifically is the trigger (see NOT DONE below) —
only that all three failing witnesses have it in common.

## ROOT CAUSE — NOT FOUND, ONE HYPOTHESIS ELIMINATED
`rt_ab_undef_fn_stub` (`src/runtime/rt/rt.c:483`) is a generic landing pad for any CALL whose target
function-cell resolved to null/unbound (wired from `bb_define.cpp`, `bb_call_proc_staged.cpp`,
`emit.cpp` — it is not `SNO$STMT`-specific). `gdb break rt_ab_undef_fn_stub` confirms this is exactly
where execution lands, but the caller frame is JIT-emitted mode-3 code with no debug info — plain
gdb's `bt` cannot unwind past it (`?? ()`, no symbol table), so **I could not identify which call
site's target cell is actually null.**

**Eliminated:** a second gate on `g_sno_uses_stmtkw` elsewhere that would explain the hook itself
silently failing to resolve. Whole-tree grep (`grep -rlF 'SNO$STMT' src/`) finds exactly the three
sites the prior FINDING already knew about (`lower_snobol4.c`, `by_name_dispatch.c`,
`builtin_ids.h`) — no hidden second condition. Whatever breaks, it is not "the hook fires but nobody
registered its name."

## NOT DONE — this needs the project's own JIT-aware tooling, not plain gdb
- Did not determine whether `DEFINE`/user procedures specifically are the trigger, or whether any
  sufficiently statement-dense program would fail the same way — my own attempts at a DEFINE-free
  minimal repro hit SNOBOL4 syntax errors of my own authorship (column/quoting mistakes, not a
  finding) and I did not spend the budget to fix my test program rather than the real question.
  **A DEFINE-free repro is the single highest-value next step** — it directly separates "procedures
  are special" from "any program past N statements is special."
- Did not diff `--dump-ir`/`--dump-bb` between the working &STNO-referencing case (which exercises
  this exact code path today, successfully) and this failing case — that comparison, per RULES.md's
  own ASM-DIFF-FIRST ordering, is the next step before more gdb, and I did not reach it.
- Collected raw callgrind Ir counts before realizing the patched runs had crashed
  (arith_loop 18.54M patched vs 13.97M baseline; fibonacci 26.70M vs 23.16M; array_sum 29.52M vs
  28.10M) — **recording these only so nobody re-collects them by accident; they are not a valid
  before/after cost comparison** (one side is a crashed partial execution, not a completed run — a
  higher instruction count on the crashing side most likely reflects extra fixed init cost, e.g.
  `&FILE`/`&LASTFILE` tracking setup, not a lower one from crashing "early"). Any real cost
  measurement has to happen on a build where the always-on path actually completes correctly.

## WHY THIS CHANGES THE ROW'S SHAPE
The row's NEXT ACTOR text (still in `## NEXT` as of this morning) says: *"If the cost is negligible:
removing the `g_sno_uses_stmtkw` gate is probably the simplest real fix."* That's no longer true even
conditionally — **there is a correctness defect in the always-on path that has nothing to do with
performance**, and it blocks measuring performance at all, since a crashing "after" isn't a valid
comparison point. This is squarely the kind of shared-hot-lowering-code tradeoff the row already
flagged as not a unilateral call (`hq_C`/Lon territory) — now with an added, unscoped correctness
bug in the mix, which if anything raises the bar for who should own landing this, not lowers it.

## LEDGER
- [seat16·2026-08-29] Patch applied, measured, reverted (`git checkout -- src/lower/lower_snobol4.c`,
  confirmed clean via `git diff --stat`), rebuilt pristine to restore the known-good binary before
  ending this session. **No SCRIP commit from this investigation** — the tree is exactly as it was
  before I started. Task file `## NEXT` rewritten to reflect this; old block demoted to
  `## SUPERSEDED-NEXT` per the baton-one-next-block-gate rule.
