# FINDING — RUNG P-0 ANSWERED: `roman` SPENDS ~44% OF ITS INSTRUCTIONS LOOKING UP VARIABLE NAMES AT RUNTIME

**Seat:** hq_P · **2026-08-22 s258** · **Class:** MEASURED · **RT_OPT=`-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`**, pristine, SCRIP `3f951354`
**Instrument:** callgrind Ir at FIXED WORK (`echo 20000 | ...`), clean oracle `/home/resources/spitbol-clean/sbl -bf`
**⛔ OUTPUT VERIFIED BOTH ENGINES BEFORE ANY NUMBER WAS BELIEVED: `check: 1102` on both.**

## The headline numbers

| | Ir @ N=20,000 | Ir/iter | check |
|---|---|---|---|
| SCRIP `-O2` | 1,049,108,015 | **52,455** | 1102 ✓ |
| SPITBOL clean | 159,314,079 | **7,966** | 1102 ✓ |

**6.58x slower at `-O2`.** The inherited s256 table said 8.4x at `-O0`, so **`-O2` bought only 1.28x** — the gap is
real and is NOT a compiler-flag artifact. (I had flagged the `-O0` trap as a live risk; it is now *excluded*.)
⭐ All three SPITBOL denominators were re-measured from scratch and reproduce the s256 baseline exactly —
`roman` 7,965.7/iter (recorded 7,966), `table_access` 359,532 (exact), `string_manip` 842.1 (recorded 842).

## ⛔ THE PROFILE, AND IT REFUTES THE HYPOTHESIS I ENTERED WITH

| function | Ir | share | calls | **Ir/call** | per iter |
|---|---|---|---|---|---|
| `core.c:_var_bucket_find` | 227,096,499 | **21.65%** | 3,174,837 | **71** | 159 |
| *(emitted BB slab)* | 123,812,841 | 11.80% | — | — | — |
| `core.c:NV_GET_fn` | 109,497,297 | 10.44% | 2,807,623 | **39** | 140 |
| `libc:__strcmp_avx2` | 101,170,836 | 9.64% | 5,009,534 | **20** | **250** |
| `pattern_match.c:c_rt_defer_close` | 91,064,113 | 8.68% | 1,403,811 | 64 | 70 |
| `pattern_match.c:rt_defer_run_all` | 65,979,121 | 6.29% | 1,403,811 | 47 | 70 |
| `pattern_match.c:rt_defer_get_pat_dtp` | 49,133,385 | 4.68% | 1,403,811 | 35 | 70 |
| `core.c:NV_SET_fn` | 29,561,599 | 2.82% | 367,215 | 80 | 18 |
| `pattern_match.c:rt_dfx_push` | 28,076,225 | 2.68% | 1,403,811 | 20 | 70 |

⛔ **THERE IS NO LINEAR SCAN. Every Ir-per-call is 20–80.** These are well-written functions; `_var_bucket_find`
at 71 instructions is a respectable hash lookup. **The defect is the CALL COUNT, not the callee.** To convert one
integer to a roman numeral we perform **159 variable-bucket lookups and 250 `strcmp`s**.

⭐ **THE CLUSTER: `_var_bucket_find` + `NV_GET_fn` + `NV_SET_fn` + `strcmp` ≈ 44% of all instructions — runtime
resolution of variables BY NAME.** SPITBOL's equivalent, `b_vra`, is **3.97%**, because it resolves a variable to a
`vrblk` pointer and dereferences it. That difference is the 6.58x.

⭐ **AND IT MAKES YESTERDAY'S ONLY REAL WIN LEGIBLE.** `byname-bake-cell-address` (`8c1f2d41`) moved beauty 2.26x by
baking **procedure** name resolution at compile time. **The identical defect exists for VARIABLES and the same cure
has never been applied.** That is also why the fleet-day moved beauty and left `roman` at 1.01x: beauty is
procedure-call dense, `roman` is variable dense.

## What this means for Lon's s258 RT plan — WHERE was right, WHAT needs revising

- ✅ **"The main optimizations are ALL in the RUNTIME" — CONFIRMED.** Our own emitted code is **11.80%**. Codegen,
  box fusion, and a peephole all compete for a slice of that ~12%.
- ⚠️ **Hand-ASM + free r10/r11 + drop the RTCC veneer — REAL BUT BOUNDED.** With ~600 runtime calls per iteration the
  per-call boundary cost is genuinely multiplied, so this is worth having; but it makes a 71-instruction function
  perhaps 50. Order-of-magnitude estimate: **10–15%**.
- ⭐ **BAKING VARIABLE CELL ADDRESSES REMOVES THE CALLS ENTIRELY — worth ~40%,** and it is the same cure already
  proven on procedures. **This is the #1 row.**
- ❓ **TABLE/ARRAY is a separate, still-unmeasured third front** (`table_access` 2.8x; note its `TABLE(512)` is
  allocated *inside* the loop, so it measures creation + GC as much as lookup).

## Corrections I owe the record

1. **My own hypothesis was WRONG.** I predicted high Ir-per-call in the pattern engine (~5,600 Ir per pattern op,
   derived by dividing totals by an assumed op count). The pattern-defer cluster is real but is **22.3%** at 35–64
   Ir/call — efficient code called 70 times an iteration. Arithmetic on aggregates produced a plausible, confident,
   wrong answer; the profile produced the right one. **Marked HYPOTHESIS at the time, now DISPROVEN.**
2. **I briefly reported a 21x SCRIP win from wall-clock.** It was invalid: SPITBOL's 1048 ms was measured *under
   callgrind* and SCRIP's 48 ms natively. Native, same fixed work: SCRIP 51 ms, SPITBOL 23 ms. Retracted within the
   minute; no number left this seat on it.

## ⭐ SPITBOL's ARCHITECTURE, settled from its own source (Lon asked)

`sbl.min:3786` — *"a code block is built for each statement compiled"*; `cdjmp equ 0  ptr to routine to execute
statement`, then `cdcod  executable pseudo-code`. The `b_*` family (`b_cds`, `b_vra`, `b_exl`, `b_art`, …) are the
per-block-type threading routines. So SPITBOL is **a compiler that emits INDIRECT THREADED CODE** — Dewar's own
technique (CACM 1975), of which SPITBOL is the original showcase. Not a bytecode interpreter (no opcode-decode
switch), not a native-code compiler, not a hybrid. The dispatch cost is visible in its profile as `call_16` +
`call_160` = **20.9%**. ⭐ **The uncomfortable comparison: SPITBOL pays 21% for threaded dispatch and still beats us
6.58x, because it spends 4% finding variables. We emit real native x86 — 11.8% of the work — then hand 44% back to
string-comparing variable names at runtime.**
