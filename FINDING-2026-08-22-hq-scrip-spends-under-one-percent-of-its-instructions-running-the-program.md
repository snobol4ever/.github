# FINDING — SCRIP spends 0.64% of its instructions running the program

**Session:** 2026-08-22 HQ (`/home/claude`, Claude Opus 5), background discovery agent under HQ LAW 13 as amended.
**Instrument:** valgrind callgrind, `--dump-instr=yes`. **RT_OPT=-O0**, mode 3. Oracle `x64/bin/sbl -bf`. Workload: beauty self-host, both arms reproducing the fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`, 40971 bytes).
**Why callgrind and not perf:** instruction counts are deterministic and immune to the layout bias that forced the s250 retraction, and to the s253 CPU-vs-wall clock mismatch. Nothing here is a timing.

## The headline

| | SCRIP | SPITBOL | ratio |
|---|---|---|---|
| Total Ir | 27,780,439,752 | 806,084,475 | **34.5x** |
| Compile + init only (`< /dev/null`) | 12,995,512,724 | 9,113,074 | **1,426x** |
| Runtime delta (the 40971-byte input) | 14,784,927,028 | 796,971,401 | 18.6x |

**Where the 27.8 G goes:** runtime by-name target resolution **48.64%** · in-process compile **46.77%** · other 2.03% · pattern engine 0.74% · table/array 0.73% · **the emitted code itself 0.64%** · memory/GC 0.23% · string ops 0.20%.

## The one defect that owns 43.8% of all instructions

`emit.cpp:1366 bb_ab_slot_for` is a **linear scan** — `for(i<n) strncmp(g_ab_fn_names[i], fname, 63)` over a 1024-slot table. `rt.c:853 rt_dyn_alpha_fn` `snprintf`s `"alpha$%s"` and calls it **on every SNOBOL4 procedure call**.

Measured: `rt_dyn_alpha_fn` 550,995 calls → `__strncmp_avx2` **269,752,048** calls → **12,170,645,373 Ir = 43.8% of total**. That is **22,089 Ir per procedure call**, scanning **487.8** table entries each time. `__strncmp_avx2` alone is the #1 function in the profile at 26.61%.

⭐ **The lookup is redundant, not merely slow.** The call site is already an indirect `jmp [rip+cell]`; the cell address is knowable at compile time. This is a bake, not a hash — though a hash alone recovers most of it.

## The equalized comparison — the engine is not the problem

Two distortions had to be removed first. (1) SCRIP's mode-3 figure includes compiling the program in-process. (2) ⛔ **This `x64/bin/sbl` oracle is INSTRUMENTED**: `zpmred`/`zpmcll`/`zpmext`/`zpmfal` call `emit_pm` on every pattern-match event — 5,649,600 calls — which calls `pm_check_enabled`, gated on env `SPL_PM_TRACE` (`monitor_ipc_runtime.c`). `emit_pm` + `pm_check_enabled` + `monitor_init` = **189,156,333 Ir = 23.47% of SPITBOL's total, doing nothing.** This is a THIRD oracle-comparison distortion in the same family as the s253 `TIME()` finding — every published ratio is measured against a SPITBOL carrying ~23% dead weight.

Strip both: SCRIP's genuine runtime work **1,272,013,514 Ir** vs SPITBOL's **607,815,068** = **2.1x**. ⭐ **The engine is close to competitive. The 34.5x is overhead, not codegen.**

## ⛔ Two queued campaigns are aimed at the wrong target

- **`kill-the-plt`** — factually correct, worth **≤1.6%**. Measured exactly: the `bb_ab_slot_for` loop is 17 static instructions/iteration and measures **18.02**; the 1.02 delta IS the `jmp *disp(%rip)` PLT stub (callgrind folds stubs into the caller, which is why `@plt` never appears by name). PLT on the dominant path = 269,752,048 Ir = **0.97%**; upper bound over all 435,609,683 dynamic calls = **1.57%**. `libscrip_rt.so` does route its own exports through PLT (1,811 entries).
- **`box-fusion` / `chain-slot-coalescing`** — these optimize **emitted code, which is 0.64% of Ir on this workload**. seat2's measured −19 instr / −7 stores per statement is real but lands on the smallest bucket in the profile. ⚠ Caveat: beauty self-host is compile-dominated; a long-running benchmark would shift the emitted-code share upward. This ranking is workload-specific and must be re-measured on `corpus/benchmarks/` before it is treated as general.

## Ranked by instructions recoverable

1. **Bake or hash `bb_ab_slot_for`** — **12,170,645,373 Ir (43.8%)**. 487.8 strncmp/lookup → ~1.
2. **`codegen_flat_chain_body` + `zd_plan`** — **4,864,273,998 Ir (17.5%)**, compile-side. 3.31 G self over 508 chains / 12,376 nodes = 267 K Ir per node. *Shape inferred* from per-node arithmetic (12,376² x ~20 Ir ~= 3.06 G vs 3.31 G measured), not from reading the loop — **one confirming ablation before acting**.
3. **ζ-storage layout planning** (`zls_node_bytes`, `zls_mark_value_refs`, `zx_cmp`, `zls_build`) — **2,222,859,183 Ir (8.0%)**, compile-phase, 110 K Ir per `zls_node_bytes` call.
4. **Label-pool linear scans** (`emit_label_intern`, `emit_label_lookup_offset`, 23.7 M strcmp) — **~1,490,000,000 Ir (5.4%)**. Same pathology as #1, same cure.
5. **Runtime by-name dispatch family** (`meth_is_user_proc` 12.9 M strcmp, `rt_proc_hash_lookup`, `try_call_builtin_by_name`, `bid_of`, `rt_proc_fnv`) — **~1,270,000,000 Ir (4.6%)**.

**#1, #4 and #5 are one class:** resolving a name by string comparison at a site where the address is already known. 53.8% of all instructions.

## Method note

Inclusive Ir is **unusable** on this program — the flat-wired BB blobs form deep recursive cycles and callgrind reports figures up to 98,938% of total. Self-Ir plus measured call edges is the only sound reading.
