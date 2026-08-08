# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-0 Prerequisites Complete

**Session:** s0 of GOAL-RTCC.md (Sonnet 4.6)
**HEAD:** `2ba70058ba237fda38f95b86ba27fecf83296f49`
**Date:** 2026-08-08 UTC

---

## RC-0(a) — RAIL INSTRUMENT: PASS

`bench_rtx_3arm.sh` gained:
- `--aslr-off` flag: wires `setarch -R` into every `run1` invocation (mirrors `bench_min_of_n.sh` ASLR control)
- `--rtcc` flag: collapses all three arms to the same `.so` with no gate variable (no `SCRIP_RTX_*` exists yet); proves the null floor before any code changes land
- Both flags wire cleanly through `run1` / new `run1_rtcc`; `bash -n` clean

**3 independent invocations × 3 programs (fibonacci, arith_int, func_call) — RT_OPT=-O0 — ASLR=off:**

| invocation | fibonacci ON/PRISTINE | arith_int ON/PRISTINE | func_call ON/PRISTINE |
|---|---|---|---|
| 1 | 0.998× | 1.014× | 1.018× |
| 2 | 0.993× | 0.985× | 0.999× |
| 3 | 0.998× | 0.996× | 1.000× |

All reads within **0.985–1.018×** of 1.000. SPREAD NOTEs fire on most rows (intra-arm spread > inter-arm gap) — this container is noisy, as expected, but the spread never reaches 1.10× and the rail never delivers a false ≥1.10× ratio on an unchanged binary. **The RC-0(a) gate passes: an unchanged binary measures 1.00× ±noise across 3 independent invocations.**

⚠ Container note: spreads of 1.023×–1.108× max/min within one arm are the noise floor here. RC-5 global-assignment rungs must hold ≥5 rounds and be honest about this. "~null (<1.10×)" applies to all RC-5 reads until we are out of this container or thermally pinned.

---

## RC-0(b) — RT-SYMBOL REGISTRY: COMPLETE

**175 unique call targets** from 342 `x86("call",...)` template sites, zero unclassified:

| Category | Count | Notes |
|---|---|---|
| C-RUNTIME (veneered) | 157 | `rt_*`, `scrip_coexpr_*`, `str_concat_d`, `str_repeat_d`, `subscript_*`, `to_int`, `dat_field_get`, `mon_emit_label_bin`, `bb_build_*` |
| LIBC-DIRECT (veneered, no varargs) | 5 | `exit@PLT`, `memcmp`, `putchar`, `strchr`, `strlen` |
| FNPTR-INDIRECT (via `x86_call_ro`) | 7 | `NV_GET_fn`, `NV_SET_fn`, `POWER_fn`, `dtp_fn_of`, `rt_proc_open_fn`, `rt_defer_get_pat_fn`, `rt_match_value_get_pat_fn` — baked pointer inline; still a C-boundary crossing |
| INDIRECT/register | 1 | `rax` — generated-boundary indirect call; NEVER veneered (NEVER-VENEER-A-GENERATED-TARGET law) |
| VARARGS in emitted x86 | 0 | `fprintf`/`printf` only in emit-time C; not emitted |
| XMM-arg calls | 0 | Zero XMM registers used as call arguments |

**R8/R9 arg-staging exceptions (RC-4 registry marks):**
- 5-arg (r8=arg5): `rt_scan_enter`, `rt_scan_lit`
- 6-arg (r8=arg5, r9=arg6): `rt_match_replace`, `rt_rev_swap_fwd`, `rt_rev_swap_undo`

These 5 symbols need per-symbol veneer staging in RC-4. All others are ≤4 SysV args.

---

## RC-0(c) — CHOKE CENSUS: COMPLETE

- Single `x86("call")` dispatch at `x86_asm.h:1482` — **structurally proven**
- **342** `x86("call",...)` call-sites in `src/templates/`, all routing through that one arm
- Zero raw-byte producers outside `x86_asm.h` (greps clean: `seg_byte`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`)
- Only non-`x86()` call emission: `bomb_bytes` in `emit_str.cpp` — documented legacy exception
- TEMPLATE-ONLY EMISSION gate: CLEAN

---

## RC-0(d) — RE-ENTRANCY + THREAD MAP: COMPLETE

**C→generated inbound entry edges (RC-1 veneer worklist denominator — 5 edge classes):**

1. **`rt_chain_enter(fn)`** — primary EVAL/CODE/DEFER dispatch; inline asm in `runtime_eval.c`; pushes 5 callee-saves then `jmp *rax` into generated blob. Called at `runtime_eval.c:213,222,231,303,308,312,379,412`. Inbound stub: must LOAD block→regs before the jmp.

2. **`rt_proc_call_open` / `rt_proc_call_open_slim` / `c_rt_proc_call_open_det`** — return the generated proc body's function pointer as `long`/`void*`; the generated call-side template then `jmp rax` into it. These are outbound calls FROM generated code that trigger inbound re-entry; the LOAD happens at the jmp destination (the proc prologue), not at the open.

3. **`rt_dcap_pump`** (called from `c_rt_dcap_end_ok_open` / `c_rt_dcap_step`, both reached FROM generated code) → `rt_proc_call_open` → generated proc body. Classic bidirectional re-entrancy: generated→C→generated. The BLOCK-CANONICAL model handles this by induction — the block holds latest values at every crossing.

4. **`scrip_coexpr_create` / `scrip_coexpr_activate`** — pthread co-expressions; each coexpr thread is a generated activation running concurrently on the same RTCC block. **OPEN DESIGN ITEM:** one global block races two VM states. Ruling needed from Lon: TLS block (fs-relative addressing) OR block swap folded into existing coexpr context switch (`rt_coexpr.c`).

5. **`rt_call_arr` → `rt_call_arr_impl` → `rt_proc_call_open`** — the hot C-runtime→generated re-entry path; the `string_manip ≈10M calls/run` hotspot. Outbound veneer fires on every rt call; inbound re-entry via proc open at the proc prologue.

**Signal window:** SCRIP handles no async signals that re-enter generated code (confirmed: no `sigaction` installing handlers that call back into generated code). Window is moot — stating from census, not assumption.

---

## RC-0 FLOOR WATERMARK (HEAD `2ba70058`, 2026-08-08)

| Mode | PASS | FAIL | SKIP | DIVERGE |
|---|---|---|---|---|
| m3 (--run) | 259–260* | 57–58 | 0 | 17–18* |
| m4 (--compile) | 241 | 75 | 1 | — |

*Oscillates by 1 on `160_pat_alt_inner_gen_resume` — QUARANTINE flake (documented, non-deterministic on pure-C path).

**141-probe suite:** PASS=0 FAIL=8 — pre-existing ZETA-MECH M-3 crater (cursor note: "record the crater floor honestly"). RC-3/RC-5 gate against this floor, not against identity.

---

## COEXPR/TLS RULING REQUEST (RC-0(d) open item)

Lon: the RTCC block is a single BSS region. Co-expressions are pthreads; two VM states on one block race. Two candidate resolutions:

**Option A — TLS block** (`__thread` or `pthread_key`; fs-relative `mov rax, fs:[offset]` in the encoder): each coexpr thread owns its own block slice. Adds one encoder arm (`x86("load_rtcc_tls")`). Thread-safe by construction. Cost: fs-relative MOV per access (1 insn, usually L1-cached).

**Option B — Block swap in coexpr context switch**: existing `scrip_coexpr_activate` saves/restores the full RTCC block alongside the register state it already saves. Zero new encoder arms. Cost: one `memcpy` of ~136B at each coexpr switch (hot for heavy coexpr use; negligible for non-coexpr programs).

**Standing recommendation:** B (block swap) — it adds no encoding complexity and the existing context switch already pays the save/restore overhead for callee-saves. But Lon routes.

---

## NEXT: RC-0 IS CLOSED (all four sub-tasks done). RC-1 is NOT-CONCURRENCY-SAFE — Lon routes the sole-writer window. RC-1 open items: RTCC block BSS region + coexpr ruling + `x86("call")` dispatch RTCC arm (writes writeback→call→reload behind `SCRIP_RTCC=0` killswitch default).
