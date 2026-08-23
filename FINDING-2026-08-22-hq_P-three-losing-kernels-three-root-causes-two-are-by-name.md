# FINDING-2026-08-22-hq_P-three-losing-kernels-three-root-causes-two-are-by-name

FROM hq_P (HQ-PERFORMANCE), s259. Feeds the existing rank-0 rows `perf-roman-8x`,
`perf-table-array-runtime`, `perf-string-runtime`. **Row factory output: rank the buckets, cure nothing.**

## The claim

The three workloads SCRIP loses on have **three genuinely different root causes** — the "it is all one runtime
problem" framing is too coarse to dispatch from. But **two of the three are the same class**: SCRIP resolving
**at run time, on every operation, something the compiler already knew**.

| kernel | root cause | rooted share | this is |
|---|---|---|---|
| `roman` | one deferred node re-reads a variable **by name** | **~54%** | compile-time knowable |
| `string_manip` | builtins dispatched **by name** | **~59%** | compile-time knowable |
| `table_access` | key stringify + probe + **allocation on read** | **~40%** | genuinely dynamic, but over-served |

## Method

All three: mode-4 native binary, FIXED-WORK, RT_OPT=`-O2`, SCRIP `e88e77db`,
`valgrind --tool=callgrind --separate-callers=2`, **output diffed against the kernel's `.ref` before any
number was read**. ⭐ `--separate-callers=2` is load-bearing and is now this seat's default: plain
`callgrind_annotate` reported roman's hottest caller as the bare address `0x488dfe0` and caused this seat to
publish a wrong two-buckets reading earlier the same session.

| kernel | N | verified | total Ir | Ir/iter |
|---|---|---|---|---|
| `roman` | 2,000 | `check: 1102` | 80,371,439 | 40,186 |
| `table_access` | 100 | `check: 250500` | 90,510,806 | **905,108** |
| `string_manip` | 20,000 | `check: 43` | 42,754,772 | 2,138 |

## `string_manip` — 59% is finding out which builtin was meant

| chain | share |
|---|---|
| `bn_replace` ← `try_call_builtin_by_name` ← `rt_call_arr_impl` | **19.75%** |
| `try_call_builtin_by_name` (+ its `builtin_ids.h` half, 7.66%) | 17.14% |
| `rt_call_arr_impl` ← `rt_call_arr` | 6.48% |
| `rt_call_arr` | 5.11% |
| `__memcmp_avx2_movbe` (two chains) | 5.99% |
| `__strcmp_avx2` ← `rt_call_arr_impl` | 1.96% |
| `__sigsetjmp` ← `_setjmp` ← `rt_call_arr` | 2.16% |
| **by-name dispatch total** | **~58.6%** |

Call counts, per iteration: **`_setjmp` / `__sigsetjmp` / `__sigjmp_save` 2.1 each · `__memcmp_avx2_movbe`
6.3 · `VARVAL_fn` 4.2.** The kernel makes roughly **two builtin calls per iteration**, and each one pays a
`setjmp` plus about three `memcmp`s **to work out which builtin it is**.

⭐ Two separately actionable things, and they are independent:
1. **The name→builtin resolution is compile-time knowable.** `REPLACE` is spelled in the source. Resolving it
   to an id or pointer at lower time removes the `memcmp` family and most of `try_call_builtin_by_name`.
2. ⛔ **A `setjmp` on every builtin call is its own defect** — 2.1 per iteration, 2.16% here, and it will scale
   with *every* builtin-heavy program, not just this one. Worth a row of its own regardless of (1).

Separately, `rt_coerce_num2_d` (`rtx_icnnum.S`) is **10.95%** — numeric coercion, unrelated to dispatch, and
it touches the existing `rtx-icnnum-icnsub-bail-invariant` row this seat already owns.

## `table_access` — 905,108 Ir/iter, and a **read that allocates**

Per-iteration call counts against **600 table writes/iter**:

| function | calls/iter | ratio to writes |
|---|---|---|
| `table_set_descr_keyown` | 600 | 1x |
| `tbl_key_str` | **1,200** | **2x** |
| `table_find_pair` | **1,200** | **2x** |
| `rt_agg_alloc` | **1,801** | **3x** |
| `__strcmp_avx2` | **2,763** | 4.6x |

⛔ **`rt_agg_alloc` runs 3 times per table operation, and one of its two call chains is
`rt_agg_alloc` ← `c_rt_subscript_var` — i.e. a table SUBSCRIPT allocates.** A read that allocates is a defect
independent of how fast the table itself is.

⛔ **`tbl_key_str` and `table_find_pair` each run at exactly 2x the write count**, through two distinct
chains (`c_rt_subscript_var` ← `rt_subscript_var` **and** `rt_subscript_var_container_only`). That shape says
**each subscript is being resolved twice**, once per path. If that is real it is close to a free halving.

`__strcmp_avx2` at 2.3 per `table_find_pair` is **not** a long linear scan — the probe is short. ⭐ So the
table's *lookup* is not obviously the problem; the **stringification, the double resolution, and the
allocation** are. This corrects the natural assumption that a 2.8x table gap means a bad hash.

Emitted code is **22.76%** here — the highest of the three, and consistent with the standing finding that our
codegen is not what loses.

## What this means for dispatch

- ⭐ **`name-lookup-strcmp` (currently rank 4) is under-ranked.** By-name resolution at run time is the
  dominant cost in **two of the three** losing kernels — roman ~54%, string_manip ~59% — and the narrow cure
  already minted for roman (`defer-nv-read-by-pointer-not-name`, rank 0) is one instance of it, not the whole
  class. The class is: *resolve once at compile/lower time, follow a pointer at run time.*
- `table_access` does **not** belong to that class and must not be dispatched as if it did. Its row wants
  three separate questions: why does a subscript allocate, why is each subscript resolved twice, and why is a
  key stringified on the read path.
- ⛔ **No cure is proposed or attempted here.** MEASURE FREELY, CURE NEVER.

## Honest limits

- One measurement per kernel, no repeat runs. Ir is deterministic so repetition adds little, but a *changed
  tree* would need re-measuring.
- `table_access` at N=100 carries proportionally more startup than the others; the shares of the small
  entries are therefore softer than roman's. The large entries are unaffected.
- The "resolved twice" reading of `table_find_pair` at 2x is inferred **from call-count ratios**, not from
  reading the subscript path. ⭐ It is the single most valuable thing to confirm or kill first, and it is
  cheap: read `c_rt_subscript_var` and `rt_subscript_var_container_only` and see whether both run per access.
