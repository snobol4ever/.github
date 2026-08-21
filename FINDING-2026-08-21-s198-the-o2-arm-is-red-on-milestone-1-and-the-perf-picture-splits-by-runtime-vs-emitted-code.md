# FINDING s198 — THE -O2 ARM IS RED ON MILESTONE 1, AND SCRIP's PERF SPLITS CLEANLY BY RUNTIME-vs-EMITTED CODE
**HQ (Claude Fable 5), 2026-08-21 s198, Lon-directed ("build -O2 and compare performance to SPITBOL"). Tree at SCRIP `1f6cea4d` (content byte-identical to the M1 landing). ⛔ RT_OPT IS THE ONLY VARIABLE ANYWHERE IN THIS FINDING.**

## ⛔⛔⛔ (1) HEADLINE — `-O2` BREAKS THE MILESTONE 1 FIXED POINT, AND THE DEFECT IS IN THE RUNTIME LIBRARY ALONE
`RT_OPT="-O2 …" make pristine`, same source tree: `beauty.sno < beauty.sno` → md5 **`1c75f97d…`**, NOT the gold `6f1671c0…`. Ladder **m3 3/10 · m4 3/10, first red rung 10, BOTH modes** (at `-O0`, same tree, same hour: **10/10 · 10/10**). Stderr carries `[GZ-10] rt_call_proc_descr: procedure '' has no stackless slab` — an EMPTY procedure name.
⭐ **LOCALIZED BY ABLATION TO ONE BINARY.** Rebuilding **only `libscrip_rt.so` at -O2** while leaving the `scrip` compiler binary at `-O0` reproduces the defect EXACTLY (same wrong md5, same first-red rung 10, reproducible twice). **⇒ the emitter/compiler is EXONERATED; the whole defect lives in the C runtime library.** ⛔ A first attempt at this ablation was **VACUOUS and said so**: `make libscrip_rt` with a changed `RT_OPT` rebuilds NOTHING (make tracks timestamps, not flags) and "passed" while compiling zero files — caught by counting `-O2` lines in the build log (0). The real ablation requires `rm -rf out/rt_pic` first.
⛔ **THIS SHARPENS O0-DEV-O2-BENCH FROM A COST RULE INTO A CORRECTNESS RULE.** RULES.md justifies the `-O0` default by BUILD TIME (~1m40 vs ~9m30) and names two `-O2`-only latents. The measurement here is stronger: **at `-O2` the engine is not correctness-equivalent on the fleet's own milestone program.** Any `-O2` benchmark quoted on a pattern/EVAL-heavy program is quoted on an engine that may be computing the wrong answer.

## ⭐ (2) THE ZSM TRACER BRACKETS IT TO ONE PORT EVENT (Lon's instrument call, s198 in-chat)
`SCRIP_ZSM=1 SCRIP_ZSM_CENSUS=1` on the rung-10 witness (`head -10 beauty.sno` as stdin), both arms, normalized (see §5):
- **3,126 port events agree EXACTLY** — same kind, same op, same node, same state.
- **Event 3,127 is the first structural divergence.** Both fire `ORIGIN op=114 (IR_STATEMENT_END)`; **-O0 on node @112, -O2 on node @113.** From there the arms are executing different statements.
- **-O2 loses 206 events (3,335 → 3,129).** The missing block is one repeating triple — `IR_STATEMENT_END(@112)` · `α IR_MATCH_BEGIN(@111) SUSPENDED` · `γ IR_MATCH_BEGIN(@111) LIVE` — **≈68 iterations that -O0 runs and -O2 skips entirely.** ⇒ **-O2 exits beauty's scan loop on the FIRST pass**: a suspended MATCH_BEGIN reports a different verdict, and the loop's continuation goes to @113 instead of re-entering @112.
- Consistent with the visible face: -O2 emits **278 bytes** — 7 correct comment lines, then `Parse Error` + a truncated `START` echo — the `mainErr1` shape, at beauty's first `-INCLUDE` lines, with `rt_call_proc_descr` holding an EMPTY name.
**FIRST STEP FOR THE CURE:** the suspended-MATCH_BEGIN verdict at node @111 under `-O2`, and the empty-name `rt_call_proc_descr` call beside it — read for UB the optimizer is entitled to exploit (uninitialised read, strict-aliasing-adjacent punning, or a lifetime escape), NOT for a "-O2 bug".

## ⭐⭐ (3) SCRIP vs SPITBOL — THE MEASUREMENT LON ASKED FOR
**Instrument:** `test_bench_snobol4_timed.sh` (fixed 500 ms budget, iterations counted, correctness-gated per row, `SCRIP_NOHUGE=1`, GC-free window). **Oracle arm corrected to `-bf`** (`SBLFLAGS="-s16m -f"`) per the s189 ruling — this script is one of the ~19 that still hardcode `-b`; row `bench-timed-oracle-flag` minted.

**(a) BEAUTY SELF-HOST — the milestone program itself.** Interleaved min-of-7, every run's md5 verified against the fixed point (**7/7 correct for all three engines**), `RT_OPT=-O0` (the only arm where SCRIP is correct here):
| engine | min | vs sbl |
|---|---|---|
| **sbl -bf** | **36 ms** | 1.00x |
| scrip m4 (run only) | 358 ms | **0.10x — 10x SLOWER** |
| scrip m3 (compile+run) | 2,568 ms | **0.01x — 71x SLOWER** |
m4 image build, once: `--compile` **1,812 ms** + gcc link 274 ms. ⇒ **SPITBOL compiles AND runs beauty in 36 ms; SCRIP needs ~1.8 s just to emit it.** m3's 2,568 ms is dominated by compilation, not execution.

**(b) MICROBENCHMARK FAMILY (15 programs, 15/15 correctness ok in BOTH arms), m3:sbl throughput —**
| SCRIP WINS | -O2 | -O0 | | SCRIP LOSES | -O2 | -O0 |
|---|---|---|---|---|---|---|
| var_access | **6.71x** | 6.99x | | string_manip | 0.33x | 0.28x |
| func_call | **5.87x** | 6.04x | | roman | 0.42x | 0.26x |
| string_concat | **5.95x** | 3.34x | | indirect_dispatch | 0.50x | 0.41x |
| op_dispatch | **5.58x** | 5.75x | | mixed_workload | 0.52x | 0.42x |
| arith_loop | **5.05x** | 5.37x | | table_access | 0.56x | 0.49x |
| fibonacci | **4.83x** | 4.62x | | eval_fixed | 0.72x | 0.56x |
| | | | | array_sum · pattern_bt · string_pattern | 0.91–0.94x | 0.70–0.91x |
**m4:m3 = 0.95–1.08x on every row — the modes are performance-equal, as the m3≡m4 invariant requires.**

**(c) DEMO / REAL-WORKLOAD FAMILY (15 programs, HEAP=4096 so the window is GC-free).** m3:sbl — claws5-match **1.58x**, claws5-match-fence **1.58x**, treebank-match-fence 0.99x, treebank-match 0.83x, calculator-1 0.45x, calculator-2-match **0.35x**, claws5 (unmatched) **0.22x**. ⛔ **5 of 15 rows are RED IN BOTH ARMS and are therefore STANDING defects, NOT -O2 fallout** (attribution measured, not assumed): `json`/`json-match`/`json-match-fence` CRASH, `porter` CRASH/BUILD-ERR, `calculator-2` DISAGREE. ⛔ `json-match-fence` at HEAP=4096 printed a nonsense **74.27G/s** for m4 — a broken row emitting a rate, not a throughput; never quote it.

## ⭐⭐⭐ (4) THE ARCHITECTURAL READING — THE LOSSES AND THE WINS SEPARATE BY BINARY
`RT_OPT` governs **only the C runtime library**, never SCRIP's emitted code. So the `-O2 → -O0` delta measures **how much of each row runs in C**:
- **Rows SCRIP wins 5–7x** (arith_loop, func_call, op_dispatch, var_access, fibonacci): `-O2` moves them **≤4%** — statistically nothing (min-det 2.4–14%). They run almost entirely in emitted x86. **This is SCRIP's engine, and it is genuinely 5–7x faster than SPITBOL.**
- **Rows SCRIP loses** (string_concat 1.89x, roman 1.57x, string_pattern 1.29x, eval_fixed 1.29x, mixed_workload 1.25x, pattern_bt 1.24x, table_access 1.17x): these are the rows `-O2` *helps*, several well past their min-detectable — **because they are spending their time in the C runtime, which is exactly where SCRIP is behind.**
⇒ **The road to "ten times faster" runs through the RUNTIME LIBRARY, not the code generator** — and beauty is the extreme case: 1.8 s of compile against SPITBOL's 36 ms total.

## (5) INSTRUMENT NOTES (each defect found by testing the instrument, per s194 discipline)
- ZSM `node=` is a **raw address** — it shifts with ASLR, and a naive cross-run diff reports 3,026 false rows. Normalizer: strip `rsp=`/`rbp=`/`rsp0=`, map each node to its **order of first appearance**, collapse whitespace (`node=%-8lu` pads differently for 4- vs 5-digit addresses — that alone broke the control).
- ZSM `depth=` is **NOT comparable across optimization levels** (-O0 10352 vs -O2 6320 at the same event): -O2 uses smaller C frames. Diff on **structure only** (kind/op/node/state). The depth field's divergence at event 2,939 is an ARTIFACT and was nearly reported as the bug.
- **Control first:** the `-O0` trace self-diffs to **0 rows over 3,382 events / 121 distinct BBs**, and ZSM is **transparent** on this witness (traced md5 == untraced md5). Only then is a cross-arm diff evidence.
