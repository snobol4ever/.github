# FINDING-2026-08-22-hq_P-hardened-nv-memo-is-17-percent-not-25

> ⛔⛔ **CORRECTED SAME SESSION — the ratio in this file is WRONG. The improvement is not.**
> Every "5.46x" below should read **5.87x**. The SCRIP half (43,478.9 Ir/iter) is correct and measured; the
> error was dividing it by the **stale s256 SPITBOL figure of 7,966** instead of measuring the oracle. Clean
> SPITBOL roman at the same N=20000 is **148,252,805 Ir = 7,412.6/iter**, measured in
> `FINDING-2026-08-22-hq_P-scoreboard-17-kernels-and-scrip-scales-worse.md`. The error **flattered us**.
> ✅ The **-17.1%** claim is unaffected — it is SCRIP-vs-SCRIP against a baseline taken the same way.
> **Rule adopted: never divide a fresh number by an inherited one; both halves of a published ratio are
> measured in the same session by the same method.**

FROM hq_P (HQ-PERFORMANCE), s259. **This RETRACTS a number this seat itself put into circulation.**

## The claim

The `NV_*` vrblk memo (SCRIP `db8f96d6`) is worth **-17.1%** of roman's total instruction count, not the
**-25.2%** figure carried in the s258 handoff. The 25.2% belonged to the **unsound first draft** — the one the
killswitch caught (335/22 vs 355/2, name pointers not stable, inserts can shadow). The shipped version pays a
`strcmp` validation plus a generation counter at all three insertion sites, and that cost is now measured, not
estimated.

## Measurement

| field | value |
|---|---|
| commit | SCRIP `aa583ad8` (tree identical in C to `db8f96d6`; `aa583ad8` touches only `scripts/`) |
| RT_OPT | **`-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`**, full `make pristine` |
| mode | **mode-4 native binary** (`--compile` + `gcc -no-pie`), compile excluded by construction |
| work | FIXED-WORK, `N=20000` on stdin (`harness.inc` fixed-work mode) |
| instrument | `valgrind --tool=callgrind`, PROGRAM TOTALS |
| **output verified** | **`check: 1102`** — checked BEFORE the number was read (a wrong answer is never a fast answer) |

```
TOTAL_Ir      = 869,577,578
Ir_PER_ITER   =      43,478.9
```

| arm | Ir/iter | vs clean SPITBOL (7,966) |
|---|---|---|
| pre-memo baseline (s258, same fixed work) | 52,455 | 6.58x |
| P-0 answer figure (s258) | 50,648 | 6.36x |
| **hardened memo, measured s259** | **43,479** | **5.46x** |
| unsound draft's claim — ⛔ RETRACTED, never shipped | 39,255 | 4.93x |

**-17.11%** against the 52,455 baseline the s258 cursor named as "baseline to beat"; **-14.2%** against the
50,648 P-0 figure. Both are honest readings of the same measured 43,479; the two pre-cure numbers differ by
3.4% for reasons predating this row, so the retraction is stated against both rather than against the
flattering one.

⛔ **Do not re-cite 25.2% or 39,255.** They describe code that was never shipped and that the killswitch
proved unsound.

## What the -O2 arm proves in passing

roman at `-O2` **self-hosts correctly** (`check: 1102`) on a full pristine build. The standing
"NO BEAUTY NUMBER AT -O2" constraint is about **beauty**, and this measurement does not touch it. hq_C has
since localised that defect to **two files of 261** (`rt.c`, `pattern_match.c`); roman's clean answer at `-O2`
is consistent with that localisation but does not by itself confirm it.

## ⭐ THE NEXT RUNG IS ALREADY MEASURED — the same run's attribution

| rank | function | share | bucket |
|---|---|---|---|
| 1 | `core.c:NV_GET_fn` | **21.04%** | variable-name lookup |
| 2 | `roman.bin:0x4012d6` | 13.38% | **our emitted code** |
| 3 | `libc:__strcmp_avx2` | **10.91%** | variable-name lookup |
| 4 | `pattern_match.c:c_rt_defer_close` | 10.47% | defer pipeline |
| 5 | `pattern_match.c:rt_defer_run_all` | 7.59% | defer pipeline |
| 6 | `pattern_match.c:rt_defer_get_pat_dtp` | 5.65% | defer pipeline |
| 7 | `core.c:NV_SET_fn` | 4.58% | variable-name lookup |
| 8 | `pattern_match.c:rt_dfx_push` | 3.23% | defer pipeline |

Rolled up: **variable-name lookup 36.5%** · **defer pipeline 26.9%** · **emitted code 13.4%**. Two buckets are
**63.4% of every instruction roman executes**, and neither is codegen.

⭐ **The memo did NOT dethrone `NV_GET_fn`** — it is still #1 at 21.04%, and `__strcmp_avx2` at 10.91% is
substantially the memo's own validation cost. The memo converted a hash into a `strcmp`; the next rung is to
stop doing the lookup at all, not to make it cheaper again.

The defer pipeline is **26.9%**, down from the 29.8% the s258 cursor predicted, still called from
roman's **single** defer site `n44_match_defer` (the bare `T` in `'0,1I,...' T BREAK(',') . T`). Correctness
half is hq_C's call — deferral is what `*expr` MEANS (REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md §7) — and this
seat takes no unilateral action on it.

## Method note, so the number can be reproduced or attacked

Script: throwaway, `scratchpad/roman_o2.sh` — compile mode-4 from roman's own directory (it needs
`-INCLUDE 'harness.inc'`), link against the freshly built `out/libscrip_rt.so`, pipe `20000`, read
PROGRAM TOTALS. Wall clock (`ms: 4252`) is printed by the harness and is **not quotable** — it was taken on a
box that had just finished a 16-way `-O2` build.
