# FINDING 2026-08-28 hq_P — m3 port counters agree with the m4 instrument to the unit on β, and `run_done:` is dead code

**Row:** `perf-symbol-attribution-tooling` slice 4 route (a). **Landed:** SCRIP `84b800c0`
(`src/runtime/rt/portcount.{c,h}`, `x86_asm.h` hook, Makefile). **Grant:** the global was granted by Lon in-chat via
CEO, 2026-08-28, GOAL-CEO CEO-75 — *"Yes I grant the global"* — after hq_P raised the mandated ⛔ NO-NEW-GLOBALS
banner and **recommended he decline**. He ruled the other way. This is that ruling built, and § THE PART WHERE MY
RECOMMENDATION WAS WRONG records what the build showed that the recommendation could not.

## ⭐⭐ THE RESULT: TWO DISJOINT INSTRUMENTS, TWO EXECUTION MODES, AGREEING TO THE UNIT

`scripts/util_port_counts.py` reads exact per-port counts out of **callgrind Ir at α/β symbols in a mode-4 binary**.
`SCRIP_PORT_COUNTS=1` counts them with **emitted increments inside mode-3's anonymous slab**. Nothing is shared
between the two mechanisms — different mode, different medium, different observer.

| program | quantity | m4 (callgrind, symbols) | m3 (emitted counters) |
|---|---|---|---|
| `pattern_bt` | β-total | 10,004 | **10,004** |
| `pattern_bt` | `match_begin` α / β / B/A | 1,000 / 10,000 / **10.000** | 1,000 / 10,000 / **10.000** |
| `porter` | β-total | 4,765,160 | **4,765,160** |
| `porter` | α-total | 15,342,550 | 15,552,669 (+1.37%) |

⭐ **β matches to the unit on 4.77 MILLION recedes.** ⭐⭐ **And the one disagreement confirms the mechanism instead of
undermining it.** α labels **can be aliased** — `emit.cpp:2942–2943` points two boxes at one label via
`emit_floater_label()` / `balias` — so a *symbol-address* instrument necessarily merges those boxes; β labels are
allocated per box (`betas[i]`) and are never aliased. **The two instruments therefore disagree exactly where the
theory says they must (α) and nowhere it says they must not (β).** That is a far stronger result than a bare match
would have been: a coincidental agreement cannot predict its own exceptions.

⭐ This also settles empirically the question I had flagged as open when recommending against the grant:
**backtrack pressure is mode-invariant.** m3 and m4 produce the same recede counts because β/α is a property of the
pattern search, not of the code generator.

## ⛔⭐⭐ AN INDEPENDENT DEFECT FOUND ON THE WAY IN: `scrip.c`'s `run_done:` IS UNREACHABLE

I first hung the dump on `run_done:` in the driver, beside `bbprof_report()`. It printed **nothing** — not even the
armed-and-empty REFUSE line, which is unconditional. An unconditional diagnostic placed at the top of the dump also
printed nothing. **The label is never reached: an emitted SNOBOL4 program terminates the PROCESS itself, so control
never returns to the driver.**

⛔ **This is the real cause of the BBPROF "never records" defect the slice-4 addendum named.** `bbprof_report()` has
sat on that dead label the whole time. It is not that recording fails — **it records and then never gets to say so.**
⭐ **The transferable shape: a teardown hook placed after a call that never returns is, in the source, indistinguishable
from one that runs.** It reads as live code, reviews as live code, and is dead. The cure here was `atexit`, which the
addendum itself had anticipated (*"m4 via atexit or the OUTPUT tail"*) — I have not touched `bbprof`, so its defect
stands, now with a diagnosed cause. ⛔ I deliberately did **not** commit a `run_done:` call site: shipping a call that
provably never runs is the defect, not the fix.

## THE DESIGN POINT WORTH KEEPING: THE SEQUENCE TOUCHES NO FLAGS

A port label is a **jump target**. The `jcc` that arrived set the flags, and code after the label may still read
them. **Every memory-increment x86 offers — `inc`, `add` — writes flags**, so the obvious `incq [cell]` would corrupt
a conditional downstream of any instrumented port. ⛔ That failure mode is the worst available: **a bug that exists
only while you are measuring**, appearing as a wrong answer that vanishes when you disarm the instrument to
investigate. The read-modify-write therefore goes through `lea rcx,[rcx+1]`, which writes no flags, making the whole
8-instruction sequence flag-transparent by construction rather than by inspection.

Storage is **chunked and never `realloc`'d**, because the emitter bakes a cell's ADDRESS into the instruction stream
at emission time; a moving array would leave already-emitted boxes incrementing freed memory — silently, and only for
the boxes emitted before the growth.

## CLAUSE 10 — TWO-ARM BOARD (both re-run after a rebase pulled in five other seats' `src/` commits)

Default: **m3 PASS=1298 FAIL=0 · m4 PASS=1298 FAIL=0 · SKIP=0 · MISSING=0**, rc=0.
`SCRIP_PORT_COUNTS=1`: **identical, 1298/1298 both modes.** Counters at every α/β port change no answer in 1,298
programs — which is the evidence for the flag-transparency argument above, not merely a green light.

## CLAUSE 6 — THE OVERHEAD, MEASURED AND ATTRIBUTED (`pattern_bt`, m3, `-O0`)

| component | Ir | note |
|---|---|---|
| **emitted slab** (the measured program) | **+759,912 (+3.65%)** | = **exactly 8 Ir × 95,048 port entries** (predicted 760,384 — a **0.06%** match) |
| compile-time encoder | ~+4.05M | m3 compiles in-process; the string-based `x86()` encoder emitting 8 extra instructions per port *definition* |
| the dump's own ranking (`pc_get`) | +446,129 | O(n²) insertion sort; fine at 137 boxes, noticeable at porter's 2,637 |
| **whole m3 process** | 20,792,585 → 26,050,756 = **+25.29%** | |

⭐ **The slab delta matching the analytic prediction to 0.06% is itself a proof that each counter fires exactly once
per port entry** — Instrument Law 7 satisfied by predicting the effect's SIZE, not merely observing its presence.
⛔ **THE COUNTS ARE UNAFFECTED BY THE OVERHEAD** — a counter counts executions, not time. What the overhead poisons is
any **timing** number taken from an armed run. **Never quote a perf figure with `SCRIP_PORT_COUNTS` set.**

## ⚠️ THE PART WHERE MY RECOMMENDATION WAS WRONG

I told Lon the grant was not worth spending, on the grounds that β/α is semantic and m3 would add only per-box
attribution. The first half proved right — β matches to the unit. **The second half was wrong in a way I could not
have known without building it:** because α labels can be aliased and box uids cannot, **the emitted counter is
strictly MORE precise for α than the callgrind instrument** (porter: 15,552,669 vs 15,342,550). It is not a
worse-but-necessary duplicate of the m4 instrument; for α it is the better of the two. ⛔ Recorded because a
recommendation that turns out wrong is worth more in the file than out of it, and because the next seat weighing an
"we already measure this" argument should know that two instruments disagreeing by 1.37% is how the aliasing was
found at all.

## FOR ceo

1. **Slice 4 route (a) is DELIVERED for m3.** Grant cited in the commit as directed. Both clause-6 and clause-10
   conditions discharged above.
2. ⛔ **`run_done:` being dead is a defect in its own right and is NOT mine to close** — `bbprof_report()` sits on it,
   and so may other teardown. Worth a row: *"driver teardown hung on an unreachable label."* I have diagnosed the
   cause and left `bbprof` untouched.
3. ⚠️ **`SCRIP_BBPROF`'s two defects are still not discharged** — nothing here reuses the bones. Retiring them is
   still a separate row, now with a diagnosed root cause for the reporting half.
4. **The `.loc` DONE-WHEN objection is withdrawn** (verified 13 `.loc`, rc=0 through that branch); no re-cut needed
   and no edit owed by you. Recorded in the row's NEXT as a retraction of my own claim.
