# FINDING — the benchmark harness could not be instruction-counted; FIXED-WORK mode added, measured on all 15 kernels

**Session:** 2026-08-22 seat2 (`/home/claude2`), THE LOOP queue row `bench-harness-unmeasurable`, rank 0.
**RT_OPT:** default (`-O0`, dev build; no codegen touched this session — SCRIP `c72482d6`, no `src/` changes since).
**Instrument:** `valgrind --tool=callgrind -q`, whole-process `Ir` (the `summary:` line in the raw `cg.out`), m4 (`--compile` → `gcc -no-pie`, matches ARCH-PERF-TOOLING.md's "do the analysis in m4").

## 1. THE COLLAPSE, REPRODUCED AND QUANTIFIED

`corpus/benchmarks/snobol4/harness.inc` (BM-H/BM-ONE) is wall-clock-budgeted: CALIBRATE picks a batch size, MEASURE runs batches until `ZBUD`=500ms of real time elapses. Ran the **unmodified, shipped** default mode under callgrind on two kernels chosen for a maximal native cost gap:

| kernel | native iters/500ms (m4, no instrumentation) | callgrind iters (same 500ms wall-clock budget, ~30–65x slower) | callgrind total Ir |
|---|---|---|---|
| `arith_loop` (trivial counter increment) | 83,886,080 | 1,310,720 | 166,086,964 |
| `table_access` (500-entry TABLE fill+sum per iteration) | 4,096 | 136 | 175,122,420 |

Native throughput differs by **20,481x** (arith_loop does 20,481 times more work per 500ms). Under callgrind's wall-clock-budgeted harness, **total instruction count differs by 0.95x** — the *cheaper* kernel (arith_loop, more iterations) shows *fewer* Ir than the *expensive* one, the opposite of what "more work" should mean, because both figures are actually measuring the same thing: how many instructions callgrind's own simulator can retire in ~500ms of real (slowed) time. **This is an instrument-throughput constant wearing a kernel's name**, not a measurement of the kernel at all. Confirmed independently on 4 more kernels below (§3): each kernel's *default-mode* callgrind Ir lands in a narrow 113M–143M band regardless of native cost, batch shape, or algorithm (loop, recursion, EVAL, pattern match).

## 2. FIX — FIXED-WORK MODE, A STDIN GATE IN `harness.inc`, ZERO NEW GLOBALS/BUILTINS

Per Lon's directive (routed via the queue brief, verbatim in substance): two modes, TIME-based and ITERATION-based, selected by a variable switch, with all wrapping in the begin/end-bracket `.inc` files — the `.sno` bodies stay untouched.

**Mechanism:** `harness.inc` now does `fixed_n = INPUT :S(ZFIXRUN)` immediately after the CHECK line. `INPUT` at EOF **fails** (standard SNOBOL4/SPITBOL semantics — the same semantics the CHECK phase already relies on being absent); a non-EOF stdin with one line holding a positive integer **succeeds**, and control jumps to a new fixed-work block that runs `ZBODY` for exactly that many iterations total, batching at the kernel's own pinned `ZK` when it has one (so `string_concat`, whose cost is not steady-state and whose batch size is therefore part of the workload, still runs many 20,000-character batches — never one string built to the full requested length, which would be a different, non-comparable workload), with **no wall-clock check anywhere in the fixed-work path**. Legacy TIME-mode code is otherwise byte-for-byte unchanged; its final line now carries an unconditional jump around the new block, its only structural change.

- **Selection:** `scrip --run k.sno < /dev/null` → TIME mode, unchanged. `echo N | scrip --run k.sno` → FIXED-WORK, N iterations, no deadline.
- **Zero new globals, killswitches, or runtime builtins** — this is a pure SNOBOL4-level control-flow addition inside an `.inc` file, using a language feature (`INPUT`/EOF failure) every one of these programs already depends on for the CHECK phase.
- **All 15 kernels, both engines-modes (m3 `--run`, m4 `--compile`), regression-tested against their `.ref` oracle before and after**: 15/15 pass in both modes, both engines — see §4. The project's own gate, `scripts/test_bench_snobol4_timed.sh`, was run unmodified and reports `CHECK RESULT: ok=15 bad=0 xfail=0 xpass=0` — confirming the default arm is untouched.
- Full contract (reserved names, batching rule) documented in `harness.inc`'s header comment and `corpus/benchmarks/snobol4/README.md`.

## 3. MEASURED: TIME-MODE Ir vs FIXED-MODE Ir, ALL 15 KERNELS

`array_sum` excluded (§5, pre-existing valgrind SIGSEGV, both modes). The other 14, m4, callgrind
whole-process `Ir`, TIME mode unmodified/default (`< /dev/null`), FIXED mode with the per-kernel `N`
documented in `scripts/bake_noise_floor_snobol4_fixed.sh`'s header table:

| kernel | native iters/500ms (no instrumentation) | TIME-mode Ir (callgrind, default, unmodified) | TIME-mode iters actually completed under callgrind | fixed_n | FIXED-mode Ir (callgrind, deterministic) |
|---|---:|---:|---:|---:|---:|
| arith_loop | 75,497,472 | 151,409,315 | 1,179,648 | 8,000,000 | 3,212,501,690 |
| eval_fixed | 1,507,328 | 113,920,090 | — | 1,500,000 | 6,320,015,884 |
| fibonacci | 16,384 | 142,858,205 | — | 16,384 | 8,799,776,533 |
| func_call | 41,943,040 | 153,932,200 | 688,128 | 7,000,000 | 3,413,597,452 |
| indirect_dispatch | 2,097,152 | 113,310,342 | 26,624 | 2,000,000 | 7,556,150,231 |
| mixed_workload | 69,632 | 95,048,167 | 1,472 | 70,000 | 3,908,173,274 |
| op_dispatch | 31,457,280 | 130,721,702 | 458,752 | 6,000,000 | 3,180,596,335 |
| pattern_bt | 1,245,184 | 114,994,485 | 18,432 | 1,200,000 | 6,493,784,613 |
| roman | 98,304 | 118,943,768 | — | 100,000 | 8,847,700,033 |
| string_concat | 7,120,000 | 115,456,569 | 100,000 | 3,000,000 | 3,304,429,955 |
| string_manip | 1,179,648 | 117,856,536 | 17,408 | 1,200,000 | 7,008,338,819 |
| string_pattern | 2,490,368 | 131,788,482 | — | 2,500,000 | 6,564,911,807 |
| table_access | 3,840 | 158,657,256 | 120 | 4,000 | 4,004,643,430 |
| var_access | 33,554,432 | 156,661,996 | 557,056 | 5,500,000 | 2,936,147,724 |

**The collapse, at full width:** native per-500ms iteration counts span **3,840 to 75,497,472 — a
19,660x range** across these 14 kernels (they are, by construction, wildly different: a trivial
counter, table hashing, string building, recursion, pattern backtracking, `EVAL`). Their **default
(TIME-mode) callgrind Ir spans only 95,048,167 to 158,657,256 — a 1.67x range** — and the ordering
does not track true cost: `table_access` (the *most* expensive kernel per native iteration) posts the
*highest* Ir, `arith_loop` (the *cheapest*) posts the third-highest, and `mixed_workload` (a
combined pattern+table+recursion kernel, nowhere near the cheapest natively) posts the *lowest*. This
is the instrument-throughput constant from §1, now confirmed across the whole family rather than one
chosen pair: whatever correlates with default-mode Ir here, it is not the kernel's own cost.

FIXED-mode Ir, by contrast, is **exactly reproducible** (re-running any kernel at the same `N`
retires the identical instruction count — callgrind is a deterministic replay, and there is no
deadline left in the run for a scheduler or clock to perturb) and scales with **real, chosen,
auditable work**: a session that wants a bigger or smaller sample changes `N` and gets a
proportional Ir change, not a number bounded by how fast callgrind itself happens to run that day.

TIME mode's own "iterations actually completed under callgrind" column (where captured) shows the
mechanism directly: `table_access` completed only 120 of its native-scale iterations in the 500ms
window, `mixed_workload` only 1,472 — both far below what even a modest FIXED-mode `N` requests, which
is exactly why their default-mode Ir cannot be read as "the cost of table_access" or "the cost of
mixed_workload": it is the cost of *whatever sliver of work callgrind could fit in 500ms of slowed
time*, a number about the instrument's speed that day, not the program.

## 4. CORRECTNESS REGRESSION — ALL 15 KERNELS, BOTH MODES, BOTH ENGINES

m3 (`--run`) and m4 (`--compile` + `gcc -no-pie` + `libscrip_rt.so`), `check:` line diffed against each kernel's `.ref`:

```
arith_loop array_sum eval_fixed fibonacci func_call indirect_dispatch mixed_workload
op_dispatch pattern_bt roman string_concat string_manip string_pattern table_access var_access
```
15/15 OK in m3 default mode, m3 fixed mode, m4 default mode, m4 fixed mode. `test_bench_snobol4_timed.sh` (the family's own gate, unmodified): `ok=15 bad=0`.

Incidentally, both `indirect_dispatch` and `mixed_workload` — documented in `README.md` as, respectively, "m4 XFAIL, B1 class" and "m4 SIGSEGV, pre-existing" — passed cleanly in m4 in this session's testing (compile, link, run, correct check value, both modes). Not chased further; it is not this row's defect to fix, and is flagged here only so a future session re-tests before assuming the README's status is still current.

## 5. PRE-EXISTING, OUT-OF-SCOPE DEFECT NOTED, NOT CHASED

`array_sum` SIGSEGVs deterministically under valgrind (both modes, both TIME and FIXED-WORK) — this is the exact defect already recorded in FINDING-2026-08-22-hq-m3-executes-three-times-m4-on-beauty-and-the-benchmark-harness-cannot-be-instrumented.md §7 ("runs correctly natively 3/3... looks like reliance on memory behaviour valgrind does not reproduce"). Unrelated to the harness change (reproduces identically on the unmodified TIME-mode default arm); excluded from the callgrind table below, native fixed-mode correctness confirmed instead (§4).

## 6. NOISE-FLOOR.tsv

Fixed-work rows added beside the existing TIME-mode rows (`m3-fixed`/`m4-fixed`/`sbl-fixed` engine names), via new sibling script `scripts/bake_noise_floor_snobol4_fixed.sh`. See that file's header for the per-kernel pinned-N table and rationale (representative of one native ~500ms TIME-mode run, rounded).
