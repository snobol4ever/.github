# FINDING 2026-08-08 — THE ICON WATERMARK IS NOT A NUMBER: 217/218/219 FROM ONE BINARY, AND ONE OF THE TWO FLAKY TESTS IS A REAL SEGV

**Session:** s219 (Claude Sonnet 4.6) · **Goal:** `GOAL-ICN-ZETA-CELLS.md` (ZK-5) · **SCRIP HEAD:** `6796f13c`
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

## THE OBSERVATION

`scripts/test_icon_all_rungs.sh` run THREE TIMES against ONE UNCHANGED BINARY, same container, no edits between runs:

| run | PASS | FAIL | XFAIL | TOTAL |
|-----|------|------|-------|-------|
| a   | 218  | 45   | 30    | 293   |
| b   | 217  | 46   | 30    | 293   |
| c   | 219  | 44   | 30    | 293   |

`diff` of the per-test verdict lists names EXACTLY TWO oscillating tests, and only those two:
- `rung09_loops_repeat_counter`
- `rung37_subscript_genproc`

Everything else is stable across all three runs.

## WHY THIS MATTERS MORE THAN A ±1

The s217 cursor recorded baseline **217**; the s218 cursor recorded baseline **218** and read the delta as
"**+1 vs the s217 217, 0 regressions**". That reading was NOISE — both sessions sampled the same two-test
oscillation once each and differenced the samples. No work moved that number in either direction.

Consequences that are live right now:
1. **A single sample cannot detect a ±1 regression on this suite.** Any rung claiming "no regression" from one
   run of 218 is asserting something the instrument cannot support. Both arms are affected (the CELLS=1 arm
   184/79/30 was ALSO a single sample; it happened to reproduce, which is evidence but not proof).
2. **ZK-8 plans a "suite floor RATCHET (baked count, descending-failure, never a zero-assert)".** A ratchet
   baked on an unstable floor will fire spuriously on the low sample and silently raise the bar on the high
   one. These two tests must be fixed or explicitly quarantined BEFORE the ratchet is baked, or the gate
   will be a coin flip.
3. The honest way to state the watermark today is a RANGE plus a named exclusion set, not an integer.

## THE TWO CAUSES ARE DIFFERENT — DO NOT TREAT THEM AS ONE CLASS

### rung09_loops_repeat_counter — A REAL SEGV, PASS/FAIL DECIDED BY A STDIO FLUSH RACE

Source (`corpus/programs/icon/rung09_loops_repeat_counter.icn`):
```icon
procedure count(n)
  local i;
  i := n;
  until (i := i - 1) < 0 do write(i);
end
procedure main()
  count(3);
end
```
Expected: `2` `1` `0`.

Run in ISOLATION on the **BASELINE arm** (no `SCRIP_ICN_CELLS`, default path), six consecutive runs:
**rc=139 (SIGSEGV) EVERY TIME — 6/6.** The correct `2 1 0` is emitted first every time. Then, on 5 of 6 runs,
the process additionally emits one large garbage integer followed by a long descending run of values in the
`1.407e14` range — i.e. a **stack address (0x7ffd…) being decremented and printed**, one per loop lap, until
the crash. On 1 of 6 runs the crash landed before that tail was flushed, so stdout contained exactly `2 1 0`
and the harness scored it **PASS**.

**So the test's verdict is decided by whether the garbage tail wins the race to the pipe before SIGSEGV.**
The underlying defect is 100% reproducible; only its OBSERVABILITY is stochastic.

Reading of the symptom (NOT yet monitor-confirmed — see NEXT STEP): the loop terminates correctly for the
three real laps, then `i` is re-read from a slot that no longer holds the counter but holds a stack address,
so `(i := i - 1) < 0` never goes true and the loop walks the address space downward. The shape — correct
result first, garbage after the bounded expression should have ended, on a procedure with a `local` and an
`until` control clause — puts the suspicion on the bound-terminal / local-slot interaction, but **this
finding does not claim a root cause.** ⛔ Per RULES.md MONITOR-FIRST, the cause is not to be settled by
reading code: it needs `test_monitor_2way_sync_step_bin.sh` on this file, then gdb with a spin counter at the
first divergent event.

⚠ This is on the **baseline/default arm** — it is NOT caused by the cells ladder and NOT caused by ZK-5.
`SCRIP_ICN_CELLS` is unset for these runs. It is a pre-existing defect that the ZETA-CELLS watermark has been
silently absorbing as a flaky test.

### rung37_subscript_genproc — CLEAN IN ISOLATION; SUITE-ONLY FLAKINESS

Four consecutive isolated runs: **rc=0, output correct and byte-identical every time**
(`a2 a2 a4 a3 a1 l=a2 l=a4 l=a3 l=a1`). No crash, no nondeterminism.

Therefore its suite oscillation is NOT a correctness defect in the emitted code — it is environmental,
most plausibly the harness timeout under container load (the suite runs hundreds of compile+run cycles;
this test drives a generator procedure through three separate subscript forms). Treat it as an
INSTRUMENT problem, not a codegen problem. Fixing it likely means raising or per-test tuning the timeout,
not touching the emitter.

## WHAT THIS SESSION DID NOT DO

- Did not root-cause the rung09 SEGV (monitor-first hunt not run; out of session budget).
- Did not change either test's status or quarantine them.
- Did not re-baseline any cursor number to a range — the s219 cursor records the range and points here.

## RECOMMENDED NEXT STEPS (in order)

1. **rung09 monitor hunt.** `bash scripts/test_monitor_2way_sync_step_bin.sh corpus/programs/icon/rung09_loops_repeat_counter.icn`
   → first divergent trace event → gdb breakpoint with `ignore <bp> <N-1>` at the bracketed C site
   (`CSN_NO_SEGV_HANDLER=1`). The theorem applies: the bug is between the first divergent event and the last
   agreeing one. Expect the answer to be a slot-lifetime question in the `until`-bound/local interaction.
2. **rung37 timeout tuning** in the harness; re-run ×5 to confirm the oscillation stops.
3. **Only then** bake ZK-8's ratchet — and bake it against a suite that has been run ≥3 times with an
   identical verdict list, not against one sample.
4. Until 1–3 land, every cursor that quotes a watermark should quote it as **217–219 (two known-flaky:
   rung09_loops_repeat_counter, rung37_subscript_genproc)** so the next walker cannot mistake noise for a
   regression.

## METHOD NOTE (reusable)

The oscillation was invisible to the usual practice of running the suite once and reading the summary line.
It surfaced only because the suite was run repeatedly and the **per-test verdict lists were diffed**, not the
totals. That diff — not the count — is the instrument that names the unstable set. Recommend it as the
standard move whenever a watermark disagrees with a prior session's by a small amount: **diff the verdict
lists before believing the delta.**

## HONEST LIMITS

(a) Three samples establish that the set is unstable and names its members; they do not establish the full
distribution — a fourth cause could hide in a test that happened to agree three times. (b) The rung09
mechanism above is a READING of the printed values, not a monitor-confirmed root cause, and is labelled as
such deliberately. (c) The rung37 timeout hypothesis is inference from "clean in isolation, flaky under
load"; it was not confirmed by instrumenting the harness.
