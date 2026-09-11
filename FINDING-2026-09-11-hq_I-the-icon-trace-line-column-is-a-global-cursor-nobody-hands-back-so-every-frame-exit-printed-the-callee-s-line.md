# FINDING 2026-09-11 hq_I — the Icon trace line column is a global cursor nobody hands back, so every frame-exit line printed the callee's line

**Measured on** SCRIP 7a2472bbe (+ this cure) · corpus 3708c8ab9 · incremental `make` · `RT_OPT=-O0` · box 2026-09-11 ~20:2x UTC · measurer hq_I.

## The claim

`g_line` is ONE global `long` (`src/runtime/keywords.c:28`), stamped per statement by
`bb_line_mark` / `bb_stmt_mark` (`src/templates/bb/bb_stmt_mark.cpp:19,30`) through a GOT load into
`rax` — it is a memory global, not a pinned register. Nothing restores it when control comes back
into a frame that did not re-execute a stamp. So the line column of an Icon trace line is not the
line of the frame the message is about; it is whatever frame touched the cursor last.

In `jcon_tests/cxtrace.icn` that was **90 of 253 lines wrong**, and the trace TEXT was correct on
every one of them. Only the number was wrong, which is why it survived: the output looks right.

## The two boundaries

The invariant the trace needs is simply *`g_line` is the current line of the current frame*. It
breaks in two places, and both are cured in `src/runtime/core/core.c` alone.

**1. Frame exit (suspend / return / fail).** `db3 suspended 31` printed 16 — `braid`'s suspend line,
three frames down. Each activation record already holds `line` = the line its frame was *called
from*, which is exactly the caller's current line, so the exiting frame's own record is the thing to
restore from. Doing that walks the chain back one level per exit, which is why the whole deep ladder
(`db3` 33 → `db2` 29 → `dbraid` 25; `dc2` 42 → `dcreate` 38) comes right at once, and why the
main-level `dcreate(61)` and `braid resumed` lines that followed them stopped inheriting 46.

**2. Frame re-entry.** A resumed generator lands *mid-statement*, so no line stamp runs at all:
`ds3 suspended 72` printed `braid`'s 16 even though `ds3 resumed` one line above printed the correct
55. The act record now banks the frame's own line at each suspend, and `rt_trace_resume_hook` hands
it back after printing instead of restoring the stale outer value it had saved.

Trace-only by construction: every call site is already past the `g_trace`/`icn` guards, so an
untraced run's `g_line` — and the run-time error report that reads it — is untouched.

## Numbers

| program | before | after |
|---|---|---|
| jcon_tests/cxtrace (m3 and m4 agree) | 90 | **2** |
| jcon_tests/tracing | 120 | **92** |
| arizona general/tracer | 28 | **22** |
| arizona general/coexpr | 0 | 0 held |
| arizona general/transmit (fed from transmit.dat) | 0 | 0 held |

Gates: `test_gate_icn_generator_exhaustion_traces_failed` PASS 10/10 ·
`test_gate_icn_traceback_corpus_pairs_are_oracle_exact` PASS 6/6 · `test_smoke_icon` m4 PASS=15
FAIL=0. `test_gate_icn_port_trace` reads FAIL 22/24 **both with and without this change** —
re-measured on a stashed clean tree, so it is pre-existing and this cure is neutral on it.

## Two traps this row walked into, both already named in RULES.md and both worth re-reading

**The ceo's census said `cxtrace 250`. It measured 90 before I touched anything.** The suspend/resume
lines the census said did not exist at all were already there. A census number in a dispatch header
has the shelf life of the tree it was cut on; measure the file before you plan against its number.

**A baseline I ran against a path with no `.std` printed `diff=0` and I nearly believed it.**
`diff nosuchfile` errors, `grep -c '^[<>]'` counts zero, and a false green is indistinguishable from
a real one. The arizona refs live in `arizona_tests/general/`, not `arizona_tests/`. This is exactly
CLAUDE.md's *instrument that answers a narrower question than you think you asked*, and the cure is
the same one that file already prescribes: capture first, then test, and assert the ref exists.

## Residual — NOT this class, named rather than folded in

`cxtrace`'s last 2 diff lines: `braid suspended 99` prints 19 where iconx prints 20. Line 19 is
`while v := @a | @b do`, line 20 is the `suspend v` body. A `suspend` that is the body of a while-do
emits no line mark of its own, so the cursor is still sitting on the while condition. That is a
**lowering gap, not a cursor gap** — a missing `IR_LINE_MARK`, and it belongs to whoever holds Icon
lowering, not to this row.
