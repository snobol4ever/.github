# FINDING: `pascal-m4-registered-dispatch-segv` is CURED — same commit as the pb30/sieve row (`8ebf6535`), and the task's own "by-value copy" hypothesis was refuted, not confirmed

**Who/when:** seat10, 2026-09-03, FLEET-12, working row `pascal-m4-registered-dispatch-segv` immediately
after closing the sibling row `pascal-m4-intermittent-segv-pb30-sieve`
(`FINDING-2026-09-03-seat10-pascal-m4-intermittent-segv-pb30-sieve-bisected-to-8ebf6535-cured.md`).

## Starting state

The named witness, `corpus/tests/pascal/arrparam.pas`, did **not** reproduce the crash at all on current
`main` — 20/20 clean, matching m3 byte-for-byte. Rather than closing on that alone (the sibling row's own
lesson: a clean re-run proves absence, not a fix), did the same before/after bisection.

## The task file's own hypothesis, tested and refuted

The baton's `## NEXT` (hq_C, 2026-08-27) led with: *"START WITH THE SHAPE... an array passed BY VALUE...
has to be copied into the callee frame; a copy sized or based wrongly is exactly the shape that overruns a
frame"* — i.e. the by-value **copy** was the prime suspect, with the instruction to ablate against a
by-`var` version and a scalar version.

Built all three (`arrparam.pas` unmodified; `arrparam_var.pas` — same program, `a` passed by `var`;
`arrparam_scalar.pas` — a trivial scalar-parameter function, no array at all) at SCRIP `809cade2` (the
commit immediately preceding the `pascal-restore-prezeta` bisection range established by the sibling row —
`81b50c3b`, the parent `pascal-m4-alpha-undefined-link` cure that makes `arrparam.pas` linkable at all, is
its ancestor):

| Program | @`809cade2` (before) | @`c2fa9bff` (ROOT CAUSE #1 alone) | @`8ebf6535` (ROOT CAUSE #1+#2) |
|---|---|---|---|
| `arrparam` (array, by-value) | **10/10 SIGSEGV** | 10/10 SIGSEGV | **10/10 clean** |
| `arrparam_var` (array, by-`var`) | **10/10 SIGSEGV** | 10/10 SIGSEGV | **10/10 clean** |
| `arrparam_scalar` (scalar, no array) | 10/10 clean | **10/10 SIGSEGV (regression)** | **10/10 clean** |

**The by-`var` version crashes exactly as reliably as the by-value version.** A `var` parameter is passed
by reference — no frame copy exists to size or base wrongly. This refutes "a wrongly-sized copy overruns
the frame" as the mechanism: the shared ingredient is an **array-typed parameter**, not the value/reference
passing convention. (Neither variant's crash was investigated down to the exact overrun site — see "What
was NOT done" — so this refines the suspect class, it does not itself name the instruction.)

**`c2fa9bff` (`zd_nops()`: add `IR_BINOP_RELOP_VAL` to the 2-operand clause — the pb30/sieve row's ROOT
CAUSE #1) alone makes things WORSE, not better, for a program with no relop-into-boolean anywhere in its
source.** `arrparam_scalar.pas` has no boolean expression, yet regresses from clean to 10/10 SIGSEGV at
this exact commit, and is clean again at `8ebf6535`. Consistent with `pascal-restore-prezeta`'s own
contemporaneous read of this same interval (its LEDGER: *"M4 122/154 — consistent with the known
intermittent class, no new regression attributable to this fix"* — measured in aggregate, at suite scale,
where one new regression this size would not stand out against 154 entries) — plausible mechanism: fix #1
alone made `zd_nops()` correctly report 2 operands for `IR_BINOP_RELOP_VAL`, so the backward-scan operand
population loop now runs for such nodes, but the **consumer** (`bb_binop_relop_val.cpp`'s ZD arm) still had
the pre-fix#2 branch-and-bail semantics — a newly-populated input feeding a still-wrong consumer, worse
than neither running. Not confirmed by direct instrumentation this session (see below) — offered as the
most parsimonious explanation consistent with both this measurement and the sibling row's.

**`8ebf6535` alone (same commit, same box, the sibling row's exact cure) fixes all three, 10/10 each.**
Current `main`: `arrparam`/`arrparam_var`/`arrparam_scalar` all 10/10, and the row's own literal DONE-WHEN
(single `diff` against m3, no repeat loop needed — this defect was always deterministic, unlike its
sibling) exits 0.

## What was NOT done

Did not instrument `zd_nops()`/`g_zd_arm`/`op_zread[]` directly to confirm the "populated input, still-wrong
consumer" hypothesis for the `c2fa9bff`-only regression — offered as explanation, not proven; the
before/8ebf6535/after table stands on its own regardless of which exact sub-mechanism explains the
`c2fa9bff`-only midpoint. Did not identify why an array-typed parameter (independent of by-value/by-`var`)
specifically routes through `IR_BINOP_RELOP_VAL`/the ZD arm at all — plausible link: array-bound or
index-range checks the callee prologue emits for an array-typed formal parameter may themselves lower to
relop-into-value nodes, which would explain why the parameter's *type* rather than its *passing convention*
is the discriminator, but this is not traced to a specific emitted instruction. Did not test `ff1df778` in
isolation (unneeded, same reasoning as the sibling FINDING). Did not gdb an actual pre-cure crash to name
the corrupted address.

## Row disposition

Closing `pascal-m4-registered-dispatch-segv` — same cure commit as the sibling row
(`pascal-m4-intermittent-segv-pb30-sieve`, `8ebf6535`), DONE-WHEN re-verified passing on current `main`
this session. The task's own GOAL text ("a by-value-array-param frame overrun") should be read as
superseded by this row's own bisection: the shared ingredient is array-typed parameters generally, and the
mechanism is the same `bb_binop_relop_val.cpp` ZD-arm defect the sibling row's FINDING describes in full,
not a distinct frame/copy-sizing bug. `pascal-writeln-enum-iso-conformance-unresolved` (this session's
third assigned row) not touched here.
