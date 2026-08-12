
---

## ADDENDUM (same session) — THE FULL BLAST RADIUS, ALL THREE CORPORA, ON THE FIXED BUILD

The `demo` and `benchmarks/snobol4` numbers in s32/s33 were all pre-fix and are hereby superseded. `benchmarks/snobol4` had never been measured at all.

| corpus | TOTAL | AGREE | DIVERGE | m3 SEGV/HANG | m4 SEGV/HANG | BUILDFAIL | PURE m4 crash |
|---|---|---|---|---|---|---|---|
| crosscheck/patterns | 122 | 111 (was 68) | 11 (was 54) | 28 / 6 | 39 (was 82) / 5 | 0 | **10** (was 52) |
| programs/snobol4/demo | 24 | 19 (was 17) | 5 (was 7) | 2 / 0 | 2 (was 4) / 0 | **4** (was 4) | **1** (was 3) |
| benchmarks/snobol4 | 23 | **22** | 1 | 3 / 1 | 2 / 1 | 0 | **0** |
| **TOTAL** | **169** | **152** | **17** | | | **4** | **11** |

**⭐ THE BUILDFAIL CLASS IS CONFIRMED INDEPENDENT AND IS UNMOVED BY THIS REPAIR.** `BUILDFAIL=4` in `demo` before and after, `0` in both other corpora. Named: **`claws5`, `expression`, `json`, `porter`** — `--compile`+`gcc` yields no binary at all (census records `rc4=-1`). s32 raised this as an unbilled class; it is now confirmed **orthogonal to r9** and still unowned. Note the census counts these separately from SEGV, so `demo`'s genuine m4 SEGV is **`treebank-array` alone**.

**⭐⭐⭐ THE RESIDUAL m4-ONLY CRASH CLASS IS 11 PROGRAMS AND IT CLUSTERS — ON FENCE-WITH-FUNCTION AND ON CAPTURE-ACROSS-ALTERNATION.** Named, `crosscheck/patterns` (all rc4=139):
`063_pat_fence_fn_optional` · `064_pat_fence_fn_capture` · `064_replace_multi_arm` · `065_pat_fence_fn_decimal` · `066_pat_fence_fn_nested` · `121_pat_calc_op_dispatch` · `141_pat_eval_double_fn_arbno` · `154_pat_construction_time_hoist` · `156_pat_cap_alt_abandon_pop` · `157_pat_cap_arb_alt_keep`; plus `treebank-array` (demo).

**Four of the ten are `pat_fence_fn_*`.** Two more are capture-across-alternation (`156`, `157`). One is deferred-eval × ARBNO (`141`). ⇒ **the residual is no longer infrastructure — it is sitting squarely on this goal's own subject matter.** FENCE1 is a licensed frame construct and s28 RULING (3) says FENCE1 earns *"for WHACK on GAMMA reasons"*: the commit must restore a watermark whose distance from rsp **is P's growth, the unknown being measured**. A `*FN` inside the fence makes that growth non-constant, which is the EARN predicate firing. **This class is a strong candidate for the `owed` column observed at runtime, not a separate infrastructure bug** — but that is a HYPOTHESIS from a name cluster, NOT a measurement. MONITOR-FIRST before anyone bills it to EARN.

**⛔ m3 IS NOT EXONERATED, AND ONE PROGRAM DIVERGES THE OTHER WAY.** `benchmarks/snobol4:cap_imm_nret2` is **`rc3=139, rc4=0`** — m3 SIGSEGVs where m4 is clean. It is the whole of that corpus's DIVERGE. A mode-4 repair cannot touch it; MODE34-IDENTICAL is a two-way contract and this is the m3 side of it.
