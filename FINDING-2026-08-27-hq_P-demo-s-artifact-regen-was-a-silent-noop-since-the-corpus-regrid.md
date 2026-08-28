# The demo .s artifact regen has been regenerating NOTHING since the s272 corpus re-grid — and reporting success

**Seat:** hq_P · **Date:** 2026-08-27/28 · **Cure:** SCRIP `dcbabbf9` · **Artifacts restored:** corpus `4d78ee0f7`

## The claim

`scripts/util_regen_demo_s_artifacts.sh` `cd`s to `corpus/demo` and tests `[ -f "$f.sno" ]` for each
of its 21 sanctioned demo names. The s272 re-grid moved demos from `corpus/demo/<name>.sno` to
`corpus/demo/snobol4/<family>/<name>.sno`. Since that move **every one of the 21 names failed that
test, took the `continue`, and the script printed `No changes — demo artifacts already current.`**

It reported SUCCESS while doing NOTHING.

## Why this is worse than a broken script

The handoff rule in CLAUDE.md and RULES.md — *"if the session touched codegen, regenerate the .s
artifacts"* — has been **a no-op for every seat since the re-grid**. The committed demo `.s` files
froze while the compiler moved underneath them. That is exactly the `hello.s` fossil this script's
own header was written to prevent, reintroduced by a path change rather than by a list going stale.

⛔ And the freeze was invisible in both directions: the seat runs the script, sees a green line, and
records "artifacts regenerated" in a handoff that is not true.

**Measured at the time of the fix:** a fresh `--compile` of `calculator-1-match` differed from its
committed `.s` by **1,749 diff lines** — and none of it was this session's cure. It was another
seat's label-prefix change (`.LPAT$0_α_2_0` vs `.Lx2_0`), i.e. the artifacts had been wrong for
somebody else's commit too, for days, and no instrument could say so.

## The class — third instance this month

⭐ **A lookup or a guard keyed on a PATH is not keyed on the thing; it is keyed on a coincidence that
a reorganisation can end.** The same re-grid killed `util_oracle_flag_sweep.sh`'s `*/programs/lon/*`
guard and `test_gate_argnote_sweep.sh`'s `-path '*/programs/lon' -prune` the same way, and CLAUDE.md
already records those as *"a guard keyed on a name is not a guard, it is a coincidence."* This is the
third instance, and the first where the victim was the **handoff** rather than a gate.

## The cure

1. **Resolve by search, not by address** — each sanctioned name is located with `find`, which ties
   the script to the FILE rather than to where the file happened to live in July.
2. **Refuse, never skip-as-success** (RULES.md) — a sanctioned name that resolves to zero files, or
   ambiguously to more than one, now exits **rc=2 naming the member**, instead of being passed over
   quietly on the way to a green summary line. These 21 are the sanctioned set: an unresolvable
   member is a real error (a renamed or deleted demo), not something to shrug at.

## Swept for siblings rather than assumed unique

`util_regen_benchmark_s_artifacts.sh`, `util_regen_prolog_bench_s_artifacts.sh` and
`update_icon_bench_asm.sh` all target `corpus/benchmarks/`, which did **not** move in the re-grid,
and none of them uses a flat-name lookup. **This script was the only victim.** (That also explains
why the benchmark regen kept working all week and nobody suspected its demo twin.)

## Verified

- First run after the fix regenerated **all 21** demo artifacts: 22,902 insertions / 20,551 deletions.
- Second run reports 21 `same` and `No changes` — **idempotent, and that line now means what it says.**
- A fresh `--compile` of `calculator-1-match` is now **byte-identical** to the committed artifact.
- Negative direction proven by construction: the refusal path is the one the 21 names took every day
  since the re-grid; it now exits 2 instead of 0.
