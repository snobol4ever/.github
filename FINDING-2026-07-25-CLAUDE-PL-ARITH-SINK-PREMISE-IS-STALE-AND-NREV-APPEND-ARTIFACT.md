# FINDING 2026-07-25 (s147) — THE SINK-6/SINK-7 PREMISE IS ALREADY DEAD CODE; nrev's `append/3` WAS INFLATING GNU 3x

**Session shape:** orientation + measurement only. **NO code change landed** (one was written, measured at
1.00x, and REVERTED). Two durable results: a falsified suspect that would have cost a future session a whole
rung, and a corpus benchmark corrected from a 3x-wrong ratio. RT `-O0` throughout, no `-O2` (no Lon directive).

---

## 1. HONEST BASELINE (rail = `scripts/bench_prolog_vanroy.sh`, 6-bench subset, RT `-O0`)

Oracles installed at exactly the versions this goal file names: gprolog **1.4.5**, swipl **9.0.4**.
Per-iteration ms, N auto-ranged per engine, median of 5, startup floors subtracted.

| bench | GNU_it | SWI_it | m3_it | m4_it | m4/GNU | m4/SWI |
|---|---|---|---|---|---|---|
| crypt | 0.6094 | 1.4961 | 3.4844 | 3.5547 | 5.83 | 2.38 |
| deriv | 0.0028 | 0.0074 | 0.0227 | 0.0220 | 7.86 | 2.97 |
| fib   | 2.1953 | 2.8359 | 4.9531 | 5.0156 | 2.28 | 1.77 |
| qsort | 0.0316 | 0.0383 | 0.2202 | 0.2078 | 6.58 | 5.43 |
| tak   | 8.5625 | 9.2344 | 16.3125 | 15.3750 | 1.80 | 1.66 |
| nrev *(corrected, §3)* | 0.0219 | 0.0172 | 0.1477 | 0.1462 | 6.68 | 8.50 |

**GEOMEAN m4/GNU = 4.50 · m4/SWI = 3.14.** NOT parity and not close — do not round this up.
Note the shape: **fib and tak are the CLOSEST to parity (1.80–2.28x) precisely because arithmetic is NOT
their bottleneck** — the call spine is. That is corroborating evidence for the s145 profile, not a new claim.

---

## 2. ⚠⚠ THE FALSIFICATION — `dop_ax`'s strcmp CHAIN IS COLD; SINK-6/SINK-7's STATED PREMISE IS STALE

**The suspect (looks damning by source-reading).** `X is A+B` with two ints appeared to cost ~14 `strcmp`
PLT calls before reaching a one-instruction result:
`dop_ax` binary chain = 10 failed strcmps (`fpow,min,max,gcd,rem,xor,shl,shr,band,bor`) → falls through to
`pl_arith2` = 3 more (`idiv,div,mod`) → `pl_is_op_code` → `rt_num_arith`, whose int×int head is just
`INTVAL(a.i + b.i)`. `pl_num_cmp` has the same shape for comparisons (up to 6 strcmps).
The SINK-6 rung text names exactly this: *"note the per-call `strcmp` op dispatch the sink deletes."*

**The change.** Integer opcodes passed from the wrappers (which know their op statically), exact int fast path
inserted before the strcmp chain; comparison semantics preserved EXACTLY (kept the double conversion — did NOT
naively switch to integer compare, per the documented 2^53 divergence trap in the SINK-7 rung text). 14 call
sites patched, built clean, all 6 benches byte-correct.

**The measurement — A/B WITH THE RUNTIME PERFECTLY ISOLATED.** Because the change is runtime-only, ONE
identical `.s` was linked against two `.so`s (base vs patched), so codegen is bit-identical by construction —
a cleaner isolation than the two-compiled-binaries recipe. Best-of-7, output md5 equal on both arms:

| bench | base | patched | ratio |
|---|---|---|---|
| fib   | 1233ms | 1211ms | 1.018x |
| tak   | 996ms  | 1007ms | 0.989x |
| deriv | 362ms  | 363ms  | 0.997x |

**~1.00x = NOISE. REVERTED.**

**ROOT CAUSE — READ THE EXPORTED WRAPPER, NOT THE STATIC LEAF.** The emitted box calls
`rt_pl_dop_ax_add/sub/mul` (`by_name_dispatch.c:1593–1607`), and those **already** carry an int×int fast path
using `__builtin_add_overflow`/`sub`/`mul` that returns **before `dop_ax` is ever entered**. Likewise
`dop_cmp_fast` (:1611) already does the int/real compare inline before falling back to `dop_cmp`.
**The strcmp chain is unreachable on the hot path.** I optimized a cold path.

### ⛔ CONSEQUENCE FOR THE LADDER — RE-SCOPE SINK-6 AND SINK-7 BEFORE STARTING THEM
Both rungs' READ-FIRST text sells them on deleting a per-call strcmp dispatch **that is already gone**. The
real remaining cost of an int `is/2` or comparison is the CALL ITSELF (marshal + PLT + DESCR_t return), not
the dispatch inside it. **Expected win from SINK-6/SINK-7 is therefore MUCH smaller than the rung text
implies** — they are call-overhead rungs, not dispatch rungs. Re-measure the premise before spending a
session on either. (Do NOT "fix" the strcmp chain again: it is cold, and this finding is the receipt.)

### THE METHODOLOGY RULE THIS EARNS (sibling of s146's family-switch lesson)
s146 learned *a family kill-switch cannot isolate a rung*. This is the same disease one level up:
**BEFORE optimizing any runtime leaf, PROVE the emitted `.s` reaches the code you are editing.** Cheap proof:
`scrip --compile` the bench, `grep -oE 'call\s+\w+' x.s | sort | uniq -c | sort -rn`, then follow the named
symbol to its DEFINITION and read what it does BEFORE delegating. A `static dop_*` body and the exported
`rt_pl_dop_*` wrapper of the same name are DIFFERENT FUNCTIONS, and the wrapper usually already fast-paths.
Source-reading identifies suspects; only measurement convicts.

---

## 3. CORPUS BUG FIXED — `nrev.pl` REDEFINED `append/3`, MEASURING GNU's NATIVE C BUILTIN

s145 already discovered this and said "rename to `app/3`", but the rename was **never applied to
`corpus/benchmarks/prolog/bench/nrev.pl`**, so the rail kept reporting the inflated number.

**Verified directly, not taken on trust** — gprolog's own error text:
`error: .../nrev.pl:10: native code procedure append/3 cannot be redefined (ignored)`

**Measured effect of the rename:** GNU per-iter **0.0072 → 0.0219 ms** (3.0x — that is gprolog's C append
being replaced by an interpreted one). The reported ratio moves **19.94x → 6.68x GNU**. The old file was not
comparing engines at all on that row; it was comparing SCRIP against a C builtin.

**Landed:** `append/3` → `app/3`, plus an in-file header block stating the reason and *"Do NOT restore the
name append/3 here"* (the s145 lesson was buried in a FINDING and was therefore lost — same defect class as
the RULES.md stale-orientation rule names). Three-engine agreement re-verified against `nrev.expected`
(GNU/SWI/m3 all match); `nrev.s` regenerated, `as` accepts. **Any nrev ratio quoted from before this commit is
inflated ~3x and must not be compared against numbers taken after it.**

---

## 4. NEXT (unchanged in direction, now with corroboration)

**REGAIN-1 slice C — THE SPINE — remains THE rung.** s145's profile put the proc-call spine at ~36% and
`lexprep2`/`rt_frame_bind_args` at ~20% (args staged into `g_call_args` then copied AGAIN into the callee
frame = double copy over ~10M calls). This session's independent evidence agrees: the two benches where
arithmetic is densest (fib, tak) are the two CLOSEST to GNU, so the gap is being paid on the call edge, not in
the data-plane leaves. Needs the driver-minted proc-entry `bb_label_t` table + one in-band `E`/`F` record;
READ BB-CODEGEN DESIGN SET (PLAN step 6) first. NOT started here — deliberately not begun on a budget too
small to land it, rather than leaving a half-cut rung.

**Also still open from s146:** re-measure the landed SINK rungs with per-rung switches (`SCRIP_NO_SINK<N>`);
the s143 family number (1.47x) and the sum of the individual rungs have no reason to agree yet.

**Container note:** no `perf` and no `gdb` in this sandbox, so the s141 gdb-sampling profile method could not
be re-run; A/B wall-clock with an isolated `.so` was used instead. A future perf session should confirm the
tools exist BEFORE planning a sampling profile.

**BANKED (carried, none resolved):** NO-LCO deep-recursion segfault + cumulative exhaustion; nested-`\+`
binding leak; `retractall/1` gaps; compiled-path silent-fail on undefined predicates.
