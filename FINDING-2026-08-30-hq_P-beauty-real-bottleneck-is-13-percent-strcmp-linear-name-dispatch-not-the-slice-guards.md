# FINDING — beauty's m4 gap is NOT the two conservative slice guards. Measured, they are worth 0.044% of the
# program. The single largest cost is __strcmp_avx2 at 12.07%, and with __strncmp_avx2 13.56% of the whole run,
# coming from TWO by-name dispatchers that each LINEAR-SCAN g_stage2.proc_table with strcmp on every call. A
# separate ~5.5% is emitter code (xop_frame_member, bb_emit_x86, x86_parse) executing at RUNTIME inside a
# COMPILED m4 binary. Also records a false oracle signal caught before publication: the SPITBOL baseline this
# comparison needs exits rc=1 with a version banner unless the .inc files are staged beside the source.

**hq_P · 2026-08-30 · row `slice-capture-aliasing-breaks-beauty-selfhost` (closed by ceo; this is the perf
follow-on ceo handed me: *"TWO CONSERVATIVE GUARDS ARE YOURS TO RELAX BEHIND MEASUREMENT … beauty's first
public number (0.18x vs SPITBOL, README) has exactly that headroom."*)**

⭐ **THE ANSWER IS: THAT IS NOT WHERE THE HEADROOM IS, AND THE MEASUREMENT SAYS SO BEFORE ANY CODE WAS TOUCHED.**
Diagnosis only — no guard was relaxed, nothing committed to the guards.

## 0. Tree and instrument

SCRIP `85b877d4` (includes ceo's beauty cure `caffe0d4` AND the length-authority landing), corpus `f16574e2d`,
.github `22b2e684`. `RT_OPT=-O0`. callgrind Ir at fixed work (RULES: prefer Ir over wall-clock on this shared
box). Floor re-verified on this combined tree first: **SNOBOL4 m3 `PASS=1672 FAIL=0` · m4 `PASS=1672 FAIL=0
SKIP=0 MISSING=0`, rc=0.** Beauty's own DONE-WHEN re-run independently: **rc=0**, self-host byte-identical with
slices ON — ceo's cure verified rather than taken on trust.

## 1. ⛔ A FALSE ORACLE SIGNAL, CAUGHT BEFORE IT WAS PUBLISHED — RECORDED BECAUSE IT WOULD HAVE BEEN A HEADLINE

My first SPITBOL baseline read **3,219,063 Ir**, which against SCRIP's m3 would have made SCRIP **~5,450x**
slower and would have been a spectacular, quotable, *entirely false* number. **SPITBOL had exited rc=1 after
144 lines beginning with a version banner** — `ERROR 285 -- include file cannot be opened`, once per
`-INCLUDE`. beauty's `.inc` files live in `corpus/include` and are found by SCRIP through `SNO_LIB`; **SPITBOL
has no such mechanism and resolves includes relative to the source**, so the oracle compiled nothing and
"benchmarked" its own error path.
✅ **Cure: stage `beauty.sno` and the `.inc` files in ONE directory.** SPITBOL then runs clean: **rc=0, 618
lines, 228,098,513 Ir.** ⭐ This is the RULES.md *oracle that answers when it should refuse* class, in its most
dangerous form — **the fast, flattering direction.** A 5,450x figure is absurd enough to check; the same defect
producing a 1.3x figure would have been banked. **The check that caught it was cheap and should be
unconditional: confirm the oracle produced the RIGHT OUTPUT, not merely a non-zero one, before dividing by it.**

## 2. THE REAL NUMBERS (× vs clean SPITBOL, `sbl_clean_bin`, `-bf`, Ir at fixed work, `RT_OPT=-O0`, one tree)

| arm | Ir | × vs SPITBOL |
|---|---|---|
| SPITBOL (bench oracle, 618 lines) | 228,098,513 | 1.00x |
| SCRIP **m4** (`--compile`) | 1,587,363,728 | **0.144x** |
| SCRIP **m3** (`--run`) | 17,550,623,413 | **0.013x** |

⭐ The README's **0.18x** is an **m4** number and my 0.144x is the same measurement on a newer tree — consistent,
not a contradiction. ⛔ **m3 is 11x worse than m4 on beauty** and is not the mode any public number should quote.

## 3. ⛔ THE GUARDS ceo HANDED ME ARE WORTH 0.044%, MEASURED BOTH MODES

| mode | slices ON | slices OFF | difference |
|---|---|---|---|
| m4 | 1,588,544,936 | 1,589,237,518 | **692,582 Ir = 0.044%** (1.00044x) |
| m3 | 17,550,623,413 | 17,551,333,014 | **709,601 Ir = 0.004%** |

⭐ ceo's *"beauty gets zero slice benefit"* is **very nearly literally true** and I am confirming it rather than
softening it: beauty does mint **6,041** slices today (`SCRIP_CAP_SLICE_TRACE=1`), and they are worth 0.044%.
⛔ **So relaxing the star-arm and thunk-frame guards PERFECTLY — recovering every copy the guards force — could
not plausibly move 0.144x toward the 10x target.** The guards are a correctness fence around a rounding error.
✅ **RECOMMENDATION: do NOT spend a campaign relaxing them, and do not relax them at all until something else
makes them matter.** They are the cheapest correctness insurance in the file, and they are what stopped the
self-host regression. ⚠️ This does not say the guards are *right* in shape — the thunk guard is blunt (ONE thunk
anywhere in a frame demotes EVERY capture in it) — only that its cost is not measurable at this scale.

## 4. ⭐⭐ WHERE beauty ACTUALLY GOES — 13.56% IS STRING COMPARISON, FROM O(n) LINEAR NAME DISPATCH

Top of the m4 profile (`callgrind_annotate`, self Ir):

| Ir | % | function |
|---|---|---|
| **191,672,751** | **12.07%** | `__strcmp_avx2` (libc) |
| 57,915,040 | 3.65% | `by_name_dispatch.c:try_call_builtin_by_name_bl` |
| 57,476,104 | 3.62% | `by_name_dispatch.c:meth_is_user_proc` |
| 55,181,178 | 3.48% | `n4372_match_defer_bx'2` (emitted) |
| 50,283,737 | 3.17% | `rt_sg_scan.S:rt_sg_scan_member` |
| 40,092,446 | 2.53% | **`emit.cpp:xop_frame_member`** |
| 37,786,937 | 2.38% | **`x86_asm.h:bb_emit_x86`** |
| 23,595,745 | 1.49% | `__strncmp_avx2` (libc) |
| 22,929,050 | 1.44% | **`x86_asm.h:x86_parse`** |

⛔ **THE MECHANISM IS A LINEAR SCAN, AND IT IS TWO FUNCTIONS WITH THE SAME SHAPE:**
```c
static int meth_is_user_proc(const char *procname) {
    if (procname && rt_proc_has_native_fn(procname)) return 1;
    if (procname) for (int pi = 0; pi < g_stage2.proc_count; pi++)
        if (g_stage2.proc_table[pi].name && !strcmp(g_stage2.proc_table[pi].name, procname)) return 1;
    return 0; }
```
`try_call_builtin_by_name_bl` carries the identical `for (int i = 0; i < g_stage2.proc_count; i++)` scan.
**beauty declares ~80 procedures** (80 `DEFINE(` sites across `beauty.sno` + its `.inc` files), so every by-name
dispatch walks up to 80 entries doing a full `strcmp` each. That is the 12%.
✅ **THIS IS THE HEADROOM, AND IT IS ~275x THE GUARDS':** 13.56% in string comparison versus 0.044%. A hashed or
interned name table is the obvious cure shape and it is a bounded, local change — the table is built once in
stage2 and the key is already a stable `const char *`.
⛔ **NOT ATTEMPTED HERE AND NOT COSTED** — I am naming the target, not claiming the cure. In particular I have
NOT shown what fraction of these calls are hot-loop repeats that an inline cache would catch versus cold ones
that need the hash.

## 5. ⚠️ A SECOND, SEPARATE ODDITY: THE EMITTER RUNS AT RUNTIME INSIDE A COMPILED BINARY

`xop_frame_member` (2.53%), `bb_emit_x86` (2.38%) and `x86_parse` (1.44%) are **emitter/template code**, and
they are executing inside the **m4, ahead-of-time-compiled** beauty binary — **~5.5% combined**. m4 is supposed
to have finished emitting before it runs. The likely cause is the runtime recompilation path ceo names in the
cure (`dtp_rcp_tree` rebuilding tree nodes for `*Parse` recompilation), i.e. beauty's deferred-expression
grammar re-enters codegen at run time.
⛔ **Stated as an observation with a named suspect, NOT as a diagnosis** — I did not trace a single call to
confirm the path, and there are other ways emitter symbols could be reached. But 5.5% of Lon's #1 program spent
in the emitter *after compilation* is worth its own row either way, and it is larger than the guard question by
two orders of magnitude.

## 6. Not attempted

No guard relaxed; no dispatcher changed; no cure committed. The `strcmp` caller attribution is from the two
functions' source and their self-cost adjacency, **not** from a resolved callgrind caller tree (the annotator's
caller output did not render cleanly for the libc leaf) — so "these two are the 12%" is strongly supported but
not proven to the instruction. Beauty only; no claim that other programs share this profile.
