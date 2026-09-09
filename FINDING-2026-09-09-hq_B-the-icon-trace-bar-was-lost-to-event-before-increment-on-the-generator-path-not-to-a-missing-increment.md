# The Icon &trace bar was lost to an event-before-increment on the GENERATOR call path, not to a missing increment

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-09 · **Lane:** Arizona reds M-Z, the &trace class · **Brief:** CEO-452
**Build graded on:** incremental `make` (RULES.md § THE PRISTINE BUILD IS LOOSENED). `RT_OPT` = `-O0`.

## What CEO-452 said, and what is actually true

CEO-452 reads: *"rt_proc_call_prologue_lex never increments &level, so every Icon &trace line lacks its '| ' bars
(tracer's 85 lines all carry it)."*

The **symptom is real** and the **named site is right**. The **stated cause is not**, in two ways, and both matter to
anyone who tries to re-derive this cure:

1. `rt_proc_call_prologue_lex` **does** increment — `rt_k_level++` has been in it since at least SCRIP `51cbcf5db`
   (2026-09-08). It increments *after* emitting the `TRK_CALL` trace event, which is the whole defect.
2. It is **not** "every Icon &trace line". The bar was already correct on the plain-procedure path and was missing
   **only on the generator call path**. Grading the fix against "every line" would have declared a regression where
   there was none.

Measured, before the cure — a two-procedure witness, one plain and one generator, oracle `iconx` v9.5.25a on the left:

```
                      ORACLE                          SCRIP (before)
plain    alpha()      "nm.icn : 3  | alpha()"         "nm.icn : 3  | beta()"     <- bar RIGHT, name wrong
generator gen()       "g0.icn : 3  | gen()"           "g0.icn : 3  gen()"        <- bar MISSING
```

## Why the two paths differ

They do not share a tap. There are two, and only one of them was ordered wrongly:

- **Plain procedure** — the trace tap is *emitted at the callee's own entry* (`emit.cpp` /
  `xa_flat.cpp` -> `rt_trace_call_hook_f`), placed **after** the emitted `rt_k_level` increment. Depth was already
  right, which is exactly why nobody noticed the other path.
- **Generator** — no entry tap is emitted at all. The call line comes from the runtime:
  `rt_proc_call_open_det*` -> `rt_proc_call_prologue_lex`, which emitted the event and *then* incremented.

Icon prints the CALL line at the **callee's** depth (`core.c` prints `*rt_k_level_p - 1` bars). A call from `main`
must therefore print one bar. Emitting before the increment prints zero.

## The cure

`src/runtime/rt/rt.c`, `rt_proc_call_prologue_lex`: the `rt_k_level++` moves **above** the `TRK_CALL`
`rt_trace_event_args` call. Two lines swapped; no new state, no new global, no frame code (CEO-447 freeze respected).

Measured after, all five witnesses (`g0` generator, `nm2` single proc, `nm3` three procs, `nm` nested, `lvl` nested):
**every bar count now matches iconx.** `nm2` matches the oracle byte-for-byte. The residual diffs on `nm3`/`nm`/`lvl`
are the *name* defect below; the diffs on `g0` are the missing suspended/resumed/failed events
(hq_V's `ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed`), which this cure does not claim.

## The reusable lesson

**A defect that is real on one path and absent on another will be written up as universal**, because the seat that
finds it reaches for the shape that reproduces it and stops. "Every Icon &trace line lacks its bars" and "the
generator path lacks its bars" produce the *same* red program, and only the second one survives contact with a
witness that also exercises the plain path. Mint the sibling that is supposed to be GREEN, not only the one that is
red — a cure graded solely against the failing shape cannot tell a fix from a wash.

Same family as this digest's `command -v` and `$?`-after-a-pipe entries: an instrument (here, a single witness)
answering a narrower question than the one being asked, and never saying so.
