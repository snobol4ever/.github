# FINDING 2026-09-13 hq_P — SCRIP's Prolog has NO wall clock at any spelling, so the Prolog speed axis produced rival numbers and an empty SCRIP column that nothing reported

Trees: SCRIP `202d8bfff` → `2447b75a0` · corpus `7bedb92d0` → `603cec954` · .github `1e8df4cc`
Row: `bench-kernels-are-not-pristine-and-carry-no-refs-ceo-567-conversion` (rank 0, hq_P)
Measured by execution on this box, 2026-09-13.

## The claim that sent the work up, and how it was narrower than the truth

CEO-669 named the defect as an ARITY mismatch: *"SCRIP's wall_us/wall_ms are registered at arity 0
while Prolog calls them at arity 1, so the Prolog speed axis has been unmeasurable since the harness
was designed."* The direction is right and the consequence is right. The mechanism is worse, and the
difference changes where the cure goes.

There is no Prolog-reachable clock in SCRIP **at any spelling**. Probed by execution, every form the
three engines use:

| probe | result |
|---|---|
| `wall_us(T)` | `existence_error(procedure, wall_us/1)` |
| `wall_ms(T)` | `existence_error(procedure, wall_ms/1)` |
| `statistics(walltime,[T\|_])` | `existence_error(procedure, statistics/2)` |
| `real_time(T)` | `existence_error(procedure, real_time/1)` |
| `get_time(T)` | `existence_error(procedure, get_time/1)` |
| `X is cputime` | `type_error(evaluable, cputime/0)` |
| `X is realtime` | `type_error(evaluable, realtime/0)` |

The `nargs == 0` pair at `src/runtime/by_name_dispatch.c:2842` is **SNOBOL4's by-name dispatch**, not a
Prolog predicate and not a Prolog evaluable functor. It is unreachable from Prolog at any arity.
⛔ **So registering a `/1` twin at that site would not reach Prolog either** — which is what the
arity framing invites, and it would leave the axis exactly as unmeasurable while looking cured.

## Why it stayed invisible — the part worth keeping

`corpus/benchmarks/prolog/bench/` shipped **two conventions in one directory**: 13 pristine
result-signature kernels, and 10 with a `wall_us`/`wall_ms` bracket baked into `main/0`.

The **rival** arms consult `prelude_gplc.pl` / `prelude_swipl.pl`, which define `wall_us/1` and
`wall_ms/1`. So gprolog and swipl ran all 23 and kept publishing real numbers. SCRIP — the engine
actually under measurement — raised `existence_error(wall_us/1)` on ten of them, **printed no answer,
and exited 0**.

⭐ **The board was full, the rival columns were real, and the SCRIP column was empty for a reason
nothing reported.** A sweep counted a raised-and-silent run as a run. This is the
"non-empty is not alive" class arriving through the one door nobody watches: the instrument was
correct for two of three engines, and the third failed in a way that produced no red anywhere.

## What the numbers actually were

Control arm, `test_bench_prolog_modes.sh`, same harness and same box, before and after the conversion:

```diff
- BEFORE  green(m3&m4)=11  broken=11  +1 NO-REF   total 23
+ AFTER   green(m3&m4)=21  broken=2               total 23
```

Ref coverage: the ruling's *"prolog 0 of 141"* counts the `.ref` **name**. Re-verified against both
oracles first: **all 22 existing `.expected` files in `bench/` already agreed with gprolog AND swipl**,
so this directory's ref coverage was 22 of 23, not 0 of 23. The one genuine gap
(`witness_depth_nrev8`) now has a ref cut from the oracle (both agree: `[1,2,3,4,5,6,7,8]`).
⚠️ `vanroy/` (21) and `src/` (94) are still 0, and `vanroy/` bakes `main :- l__(64).` into each source
— the iteration count living inside the artifact under measurement. That half of CEO-567 is not cured.

## The two reds that remain, both named, neither a benchmark defect

- **`queensn` — SIGSEGV under scrip.** PRE-EXISTING: reproduced unchanged on the pre-conversion source
  from `git show HEAD:`. The conversion neither caused nor hid it.
- **`tak` — `ERROR 246 stack overflow`.** A REAL red the `existence_error` had been **masking**: the
  kernel never reached the engine before. ⭐ Making a thing measurable is how you find out it was
  broken; this red is a deliverable of the row, not a regression in it.

Both belong to the Prolog runtime lane, not to speed. Filed, not cured here.

## Cured, and what it cost

One shape for all 23, no change to any kernel's computation:

```prolog
% *BENCH kernel=<name>                    one comment line, inert to every engine
bench_work(Res) :- <the computation>.     the work, and only the work
main :- bench_work(Res), write(Res), nl.  what makes the file a standalone program
```

`scripts/bench_prolog_wrap.sh` (new) generates the timed/counted form around that — three angles,
refusing rc=2 rather than emitting a wrapper that cannot measure.
`scripts/test_gate_bench_prolog_kernels_pristine.sh` (new, BLOCKING in `test-sequential` and in
`preflight`) keeps the second convention from reappearing; negative-tested four ways.

⛔ **One design trap found while building it, worth carrying:** `--mode=time` was first written as a
recursive counter, and gprolog died at *"global stack overflow (reached: 32765 Kb)"* on `nrev` before
the 1000 ms budget was spent — **the deadline arm was measuring how fast the engine could exhaust its
own stack.** `between/3` + cut is constant space on all three engines and yields the count for free.

## The ask

`scripts/test_gate_pl_wall_us_arity1.sh` already exists and is **RED** (`FAIL m3`, `FAIL m4`, arity-0
intact). It is the DONE-WHEN for the other half: a Prolog-reachable `wall_us/1` + `wall_ms/1`, which is
a **Prolog builtin registration** — another concern's node, so it is an ASK with this measurement
attached, never a landing from this seat. Until it lands, SCRIP's Prolog arm has **no self-measured
work number at all**, and only the process wrapper (angle 3) can produce a Prolog number — a TOTAL,
carrying startup, which may never share a column with a rival's self-measured work.
