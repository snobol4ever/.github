# FINDING — the pattern-lane gap ANSWERED: ~70% of SCRIP's pattern cycles are the DEFER-CAPTURE + NAME-VALUE plumbing, not matching. The match primitives themselves are already lean.

**Seat:** ceo (Lon's direct assignment, in-chat 2026-08-27: *"I assign you to the task… Why oh why is SCRIP not faster than SPITBOL on the demos, and pattern matching, considering we have highly optimized register aware BB templates with almost zero RT calls."*) · **Date:** 2026-08-27 · **Trees:** SCRIP `809cade2` pristine `-O0`, corpus at `perf-attribution-20260827T233658Z.tsv` (the durable dated record — Lon's no-wholesale-reruns ruling landed in its header) · **Instruments:** perf stat (instructions/cycles/task-clock, 3 runs/arm) + perf record cycles attribution; fixed work per committed `SCALE.tsv`; oracle `sbl_clean_bin()` `-bf -s16m` (s255 authority); harness measurement condition NOHUGE=1 HEAP_MB=4096. Cross-validated against hq_P's callgrind slope (same day): SCRIP pattern_bt 5,355 insn/iter (perf) vs 5,463 Ir/iter (callgrind) — 2%; SPITBOL 1,686 vs 1,663 — 1.4%. Two instruments, one answer.

## The numbers (axis: × vs clean SPITBOL, faster axis; Ir and wall are DIFFERENT instruments and never share a column)

```diff
  kernel          basis                     SCRIP        SPITBOL      multiple
- pattern_bt      insn/iter (slope)         5,355        1,686        0.31x
+ pattern_bt      wall @2M iters, best      0.927s       0.896s       0.97x   <- PARITY
- string_pattern  insn/iter (total@8M)      3,548          787        0.22x
- string_pattern  wall @8M iters, best      3.600s       0.970s       0.27x
```

⭐ **Why Ir 0.31x can coexist with wall 0.97x on pattern_bt:** SCRIP sustains **3.3 IPC** (straight-line -O0 BB code, superscalar-friendly) vs SPITBOL's **1.15–1.5** (`pstr1`'s dependent byte loop). The instruction excess is real; the hardware hides most of it on the backtracking kernel — and stops hiding it on the capture kernel, where the excess is strcmp/hash/pump calls that stall.

## WHERE THE CYCLES GO (perf record, m4 arm — named symbols; m3 module split agrees within 2 points)

**pattern_bt** (alternation + backtrack + one capture): rt 54.4% + emitted BB 41.2%. But inside those: `n58_match_defer_α` **17.0%** + `rt_defer_probe_run` **16.0%** + `NV_GET_fn` **12.3%** + `rt_defer_cell_read` **7.8%** + `dtp_fn_of` **5.3%** + `rt_defer_nv_read` 3.4% + `rt_dcap_pump` 2.9% + `NV_SET_fn` 2.0% ≈ **67%** in the deferral/name-value layer. The actual matching boxes — span, lit, alternate, begin — total **≤8%**.

**string_pattern** (three `BREAK . field` captures): rt 55.0% + **libc 16.5%** + kernel 14.5% + BB **14.0%**. Top: `strcmp` **19.1%** (evex + plt), `NV_PTR_fn` 13.8%, `rt_dcap_pump` 12.1%, `is_protected_pat_name` 4.3% (a per-operation string compare on pattern names), `_var_hash` 2.4%. `match_break` itself: **2.2%**.

**SPITBOL, same work** (Lon asked where IT spends time): pattern_bt = `pstr1` 70.5% (the literal-compare loop IS the program), failure/alternation plumbing ~8%. string_pattern = `sbstr`+`pbks1` 24%, allocator/GC family ~20%, pattern-node fetch ~11%. SPITBOL's captures bind to variable slots directly (`asinp` 2.5%) — no name resolution at match time.

## THE ANSWER TO LON'S QUESTION

The premise is half right and the half that's wrong is the whole gap. **The register-aware BB templates ARE lean — matching primitives cost ≤8%.** What is NOT lean is the layer wrapped around them on every pattern step: **deferred-match probes (`rt_defer_*`), the deferred-capture pump (`rt_dcap_pump`), and name-value access that resolves variables THROUGH the runtime (`NV_GET/SET/PTR_fn` → `dtp_fn_of` fn-pointer dispatch, with `strcmp`/`_var_hash`/`is_protected_pat_name` doing STRING-KEYED lookups per capture per iteration).** "Almost zero RT calls" is false on this lane: 52–55% of cycles are in `libscrip_rt.so`. SPITBOL does the identical semantic work inside single assembly primitives with slot-bound captures and zero per-step name resolution.

**Headroom, arithmetic not promise:** removing ~67% of pattern_bt's 5,355 insn/iter lands at ~1,750 ≈ SPITBOL's Ir — and at SCRIP's 2–3x IPC advantage that is a projected **2–3x wall-clock WIN**, on the road to the 10x target. The demos inherit this directly: hq_P's same-day 3-angle demo grid (0.250x–0.772x totals) is pattern-heavy code paying this same layer plus compile-in-region (m3) — treebank/json/calculator are capture-dense, claws5 (0.77x, closest to parity) the least.

## CURE DIRECTION (rows, not vibes)

1. **Compile-time capture binding:** a `. VAR` capture's target cell is knowable at compile time — bind it to a zeta cell/register in the graph; kill `strcmp`/`_var_hash`/`is_protected_pat_name` from match time entirely (string_pattern's ~26%).
2. **Defer fast path in the box:** inline `rt_defer_probe_run`'s hot path (probe-hit, no pump) into the `match_defer` template; call the RT only on the slow arm (pattern_bt's ~30%+).
3. **NV access through cells, not dispatch:** subject/variable reads on the match path go through `NV_GET_fn`→`dtp_fn_of` per access — the cells-graph admission exists for exactly this; extend it to the pattern lane's reads.
Minted as `perf-pattern-defer-capture-layer-cure` (rank 1, hq lanes; the evidence is this file + the dated TSV).

⛔ Provenance duties honored: no pre-s255 number cited; Ir and wall never share a column; every multiple carries its oracle; the durable store gained a dated file, not an overwrite.
