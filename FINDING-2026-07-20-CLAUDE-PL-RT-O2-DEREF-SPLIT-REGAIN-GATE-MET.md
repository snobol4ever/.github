# FINDING 2026-07-20 (Claude, session s112) — PL: runtime -O2 + deref fast-path split; REGAIN-GATE geomean 1.67× → 0.65× (MET)

## Context
s107's cursor named REGAIN-1 SLICE C (direct det call) as next; a parallel session ALREADY LANDED it as s108 (SCRIP `7626fee0` — dcα stub, `call proc_X_dcα`, one `rt_pl_dc_prep` crossing, `SCRIP_NO_DC` hatch, trail-tidy exactness fix) but its .github cursor update was never pushed — the record lived only in the commit message. This session absorbed that record and continued the same rung: the completion bar (fib/tak ≤1.3× OLD on the rail) was still open (fib 6.71 / tak 31.1 ms/it on this container at HEAD `85a631c2`).

## The measured root cause
callgrind on fib m4 (exact, 4 iters, 297M Ir total): the emitted blob is ~6% of instructions; the C runtime is everything else — and **`libscrip_rt.so` builds `-O0 -g`** (Makefile CBASE-era default; OLD 7ec7305a identical). At -O0 nothing inlines: `plw_cell_deref` 15.6%, `plw_entry` 7.3% (3 compares, un-inlined), `pl_trail_push` 6.2% (`static inline` ignored), and **`plw_poison_trap` 5.5% — an off-by-default debug hatch being CALLED once per deref STEP**. No directive pins -O0; the object-byte-identity proof machinery that leans on -O0 concerns the compiler binary's TUs (BB-REVAMP C2), not the runtime .so; Lon's verbatim top priority is benchmark performance.

## Landed (3 edits)
1. **Makefile `RT_OPT` knob** — `RT_OPT ?= -O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`, applied to the `libscrip_rt.so` rule ONLY. Compiler binary build untouched; emitted `.s` artifacts are flag-independent; `make RT_OPT="-O0 -g"` restores the debug build (gdb-heavy hunts). `-fno-strict-aliasing` covers the pervasive DESCR/word punning; `-fwrapv` covers the documented INTVAL-wraparound reliance (REGAIN-4's `__builtin_*_overflow` note). **-Wclobbered audit: zero warnings across all six setjmp TUs at -O2** (the classic -O2 breakage class, pre-cleared).
2. **Poison-trap hoist** (`by_name_dispatch.c`): the hatch read moves out of the per-step loop.
3. **Deref fast-path split**: `plw_cell_deref` becomes a `static inline` zero-hop test (non-DT_N, non-live-PLVAR returns immediately); DT_N indirections, live PLVAR chains, and the ARMED poison hatch all route to `plw_cell_deref_slow` (the original 4096-guard walker) — trap fidelity exact, semantics identical.

## Measured (m4, this container, per-iteration; outputs byte-identical at every step)
| step | fib | tak |
|---|---|---|
| HEAD 85a631c2 (-O0) | 6.71 | 31.1 |
| + RT_OPT -O2 + hoist | 3.82 | 15.2 |
| + deref split | **3.60** | **14.5** |

Ir total 297M → 169M. Post-O2 profile #1 was the un-inlined deref walker at 22.6% (gcc declines the guard-loop+abort body), motivating the split.

## REGAIN-GATE (same-container A/B vs OLD 7ec7305a, rail wrappers, OLD GC-presized per its method)
**Measurement trap re-confirmed (s105's, now on the rail itself):** the pregut rail's single-run-per-cell method is invalid at ratios <2× on this 1-vCPU container — its NEW fib cell read 7.66 ms/it where an identical-protocol rerun reads 4.70 (throttle window). At contested ratios use **interleaved twins ×5, medians** (s105 protocol):
- fib: NEW 257ms/64 = 4.02 vs OLD 282/64 = 4.41 → **0.91× (BEATS OLD)**
- tak: NEW 1064/64 = 16.6 vs OLD 1075/64 = 16.8 → **0.99× (MATCHES OLD)**

Rail rows where ratios are noise-immune (all NEW-favoring ≥1.2×): qsort 0.210/0.611 = **0.34×**, nrev 0.164/0.213 = **0.77×**, deriv 0.024/0.029 = **0.83×**, queens_8 9.14/22.75 = **0.40×**. Geomean over 6: **0.65×** — gate ≤1.3× MET; s107's 1.67× closed, NEW now beats the pre-gutting engine overall. vs gprolog (same rail): fib ~1.28×, tak 1.71×, queens 2.7×, qsort 6×, deriv 8×, nrev 23× — the PL-SPEED-META gp gates remain future rungs.

## Board (final artifact)
Prolog rung suite **×3: 135/138 run + 135/138 compile every run** (pre-existing float-writer trio, zero new). Smoke pl 5/5 ×3 modes; sno 7/7; icn 14/14 ×2 (re-run at final artifact). fib+tak **m3==m4 byte-identical** at final. no-new-global PASS floor 14. Outputs byte-identical -O0↔-O2↔split on fib/tak/noop.

## Banked
- **`rt_str_alloc`/`rt_jct_relop` implicit-decl in `by_name_dispatch.c`** (`||` concat arm, rt_call_arr_impl ~:3509): int-returning-pointer truncation landmine at ANY opt level, hidden by `-w`. Needs proper decls.
- Rail method note: single-run cells → order-of-magnitude only; contested ratios need interleaved twins (above).
- -O2 -g DWARF-under-inlining ballooned the .so to 175MB; `objcopy --strip-debug` applied (sidecar `libscrip_rt.so.dbg` kept); startup measured 3ms fat OR stripped (mmap lazy) — size was cosmetic, `-g1` optional.
- Pregut worktree build needs `make OBJ=/tmp/si_objs_old` (both Makefiles share `/tmp/si_objs` — clobber) and `libgc-dev` (OLD's Boehm heap; rail's `GC_INITIAL_HEAP_SIZE=1G` is that).
- This container: **nproc=1**; monolithic rt rebuild ~13min — plan sessions around it.
- Cross-language note: -O2 rt.so speeds SNOBOL4/Icon benches too — their banked numbers (claws5/treebank vs SPITBOL) will shift favorably; SN4 session should re-time before quoting.

## Next
tak residue vs gp (1.71×): clause-try `unify_ci` + per-try trail mark/unwind = SPEED-5 first-arg indexing territory; `dc_prep` NULVCL-seed inline into the stub template; RSP-F-4 register residency (H/TR) still queued. Lon ratified the -O2 default this session ("All your choices. I'm with you on this.").
