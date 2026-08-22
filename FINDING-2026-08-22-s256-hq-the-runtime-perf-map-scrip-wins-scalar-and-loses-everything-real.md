# FINDING — s256 HQ: the runtime perf map. SCRIP wins on scalar work and loses 3–8x on everything a real program is made of

**Date:** 2026-08-22 · **Seat:** HQ (`/home/claude`, Claude Opus 5, s256) · **Instruments:** callgrind Ir at identical FIXED WORK (load-immune) + `harness.inc` time mode (noisy, see §4) · **Build:** `make pristine` EXIT=0 at HEAD `2659558e`, **RT_OPT=`-O0`** · **Oracle:** `/home/resources/spitbol-clean/sbl -bf` (the s255 benchmark oracle) · **Mode:** SCRIP mode-4 native binary, **compile excluded by construction** (Lon s256: *"Worry not about compile time. We are zooming on runtime."*)

## 1. The map

Identical fixed work, both engines, deterministic instruction counts:

| kernel | N | SCRIP Ir | SPITBOL Ir | Ir/iter SCRIP | Ir/iter SPITBOL | SCRIP vs SPITBOL |
|---|---|---|---|---|---|---|
| `var_access` | 200,000 | 105,849,602 | 161,515,739 | 529 | 808 | **1.52x faster** |
| `arith_loop` | 200,000 | 79,507,515 | 87,840,211 | 398 | 439 | **1.10x faster** |
| `table_access` | 2,000 | 1,994,260,056 | 719,064,032 | 997,130 | 359,532 | **2.8x slower** |
| `string_manip` | 20,000 | 62,457,691 | 16,841,613 | 3,123 | 842 | **3.7x slower** |
| `roman` | 20,000 | 1,343,411,963 | 159,314,090 | **67,170** | 7,966 | ⛔ **8.4x slower** |

And the flagship, runtime only, mode-4 binary producing the correct fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`, 40,971 bytes):

| | Ir |
|---|---|
| **beauty self-host, SCRIP runtime** | 2,129,544,838 |
| **beauty self-host, SPITBOL clean** | 228,082,817 |
| | ⛔ **9.34x slower** |

⭐ HQ's SPITBOL figure independently reproduces seat2's clean-oracle measurement (228,082,817 vs 228,144,314, **0.03% apart**, different session and method), so the denominator is not in question.

## 2. ⭐ THE SHAPE OF IT, AND IT IS THE WHOLE POINT

**SCRIP is good at exactly the things that do not appear in real programs, and bad at exactly the things that do.**

- **Scalar / register-resident work — SCRIP WINS**, 1.1–1.5x. Variable access and integer arithmetic. This is the BB codegen doing its job, and it is genuinely competitive.
- **Data structures — SCRIP LOSES ~2.8x.** Tables and arrays.
- **String manipulation — SCRIP LOSES 3.7x.**
- **Whole realistic programs — SCRIP LOSES 8.4x.** `roman` is the most program-shaped kernel on the board and it is the worst result on the board.

⛔ **This explains beauty's 9.34x directly, and the agreement is the strongest evidence here:** beauty is a string/pattern/table program, and it lands at 9.34x — right beside `roman`'s 8.4x. Two independent workloads of the same *shape* give the same answer. The scalar wins never show up because beauty barely does scalar work.

⭐ **CONSEQUENCE FOR THE CAMPAIGN: the 10x goal is not blocked on codegen.** The emitted code is already ahead of SPITBOL where it is measured directly. Every remaining multiple is in the **runtime services** the emitted code calls out to — table/array access, string building, pattern machinery. Optimizing box templates further improves the one bucket already winning.

## 3. `roman` is the single most valuable target on the board

**67,170 instructions per iteration against SPITBOL's 7,966.** That is not a tuning gap, it is a structural one, and it sits in a kernel deliberately written to look like a real program. Whatever it is doing 8.4x too much of is very likely the same thing beauty is doing 9.34x too much of. **Profile `roman` first**; it is smaller than beauty, it is fixed-work reproducible, and it almost certainly shares beauty's dominant cost.

## 4. ⛔ A MEASUREMENT WARNING THAT COST HQ A WRONG TABLE, AND WOULD COST ANY SEAT THE SAME

HQ first measured all 15 kernels by **wall clock in time mode** and got 510–615 ms across fifteen completely different workloads. That band is not a result — **`harness.inc` time mode runs a fixed ~500 ms budget (`ZBUD`) and reports `iters`; `ms` is constant BY CONSTRUCTION.** Reading `ms` as a speed number reads the target back. The real spread hides in `iters`: `arith_loop` 39,845,888 vs `table_access` 3,072, a 13,000x range behind fifteen identical-looking times. This is exactly the "plausible false table" `bench-harness-unmeasurable` was raised about.

⛔ **And time-mode `iters` is itself unquotable on a loaded machine.** With 16 seats building concurrently, back-to-back runs of the same kernel swung 2x (`arith_loop` 46,137,344 then 18,874,368), and the derived ratios swung with them — 4.88x then 2.40x for the same kernel against the same oracle. **The first pass suggested SCRIP was 3–5x FASTER on its good kernels; the deterministic Ir measurement says 1.1–1.5x.** The wall-clock table was flattering and wrong.

⭐ **RULE, and it is why both harness modes exist:** on a shared machine, **time mode answers "is it alive", fixed-work + callgrind Ir answers "is it fast."** Every ratio in §1 is fixed-work Ir. No ratio in this FINDING is a timing.

## 5. Both benchmark modes are FINISHED and VERIFIED WORKING (Lon asked; this is the check)

Landed 12:05–12:59 today (`bench-external-cpu-and-elapsed-clock` seat3, `bench-harness-unmeasurable` seat2, `450368d0` fixed-work noise-floor bake). Verified by HQ just now, all four cells of the matrix:

| oracle | TIME mode | FIXED mode |
|---|---|---|
| `spitbol-clean` | ✅ rc=0, 9,961,472 iters / 514 ms | ✅ rc=0, N=1,000,000 / 91 ms |
| `x64/bin/sbl` | ✅ rc=0, 5,505,024 iters / 512 ms | ✅ rc=0, N=1,000,000 / 137 ms |

SCRIP m4 both modes ✅ (`iters: 1000000`, `check: 1000` identical across runs). ⭐ **seat6's reported CALIBRATE hang under `x64/bin/sbl` DOES NOT REPRODUCE on `arith_loop`** — it completes in 512 ms. Row `rung-calibrate-hang` (seat15) should re-scope to find which kernel actually hangs, or close as not-reproducing. ⚠️ Fixed-work is deterministic in WORK (`iters`/`check` identical) but its wall time still varies ~20% run to run (48/39/42 ms) — that is what the noise-floor bake is for.

## 6. Routed

New rows: `perf-roman-8x` · `perf-table-array-runtime` · `perf-string-runtime`. ⛔ `profile-the-compiler-1426x` is **RE-POINTED to runtime** per Lon s256 — the 1,426x compile figure stays a recorded fact, not a campaign. Supersedes the emitted-code-is-0.64% ranking as the perf board's organising fact **for runtime-shaped workloads**; the original ranking remains correct for the compile-dominated beauty-in-mode-3 measurement it was taken on.
