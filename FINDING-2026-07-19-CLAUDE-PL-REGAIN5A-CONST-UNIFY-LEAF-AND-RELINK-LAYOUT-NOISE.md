# FINDING 2026-07-19 (Claude Fable 5, s105) — PL-REGAIN-5 slice A: const-unify leaf 232→83 cyc on 3.24M fib sites (~17% same-lib); AND the relink-layout noise trap that nearly caused a wrong revert

## 1. What landed

`rt_pl_dop_unify_ci(args, imm64)` / `rt_pl_dop_unify_cs(args, ro_str)` (by_name_dispatch.c) + a const-detection arm in `bb_call_fn.cpp`: when one `$unify` side is an emit-time `IR_LIT_INTEGER`/`IR_LIT_STRING` (atoms incl. `[]` lower as LIT_STRING — verified in lower_prolog.c), the const rides in a REGISTER, only the other side is marshaled (to args[0]), and the leaf runs the hot arms inline (unbound→bind with cell content bit-identical to marshal_call_arg's operand {DT_I,0,imm}/{DT_S,0,s}; same-shape int compare; PLREF→fail) with `plw_unify_vals` as the VERBATIM fallback for every other shape. Nothrow-rail discipline as the s104 leaves. Compile-time hatch `SCRIP_NO_CU` (SCC-off pattern); rides under the existing SCRIP_NO_DOP/DOP_SKIP hatches too. Both media (movabs imm64 = LIT_I idiom; RO string = LIT_S in-band seal idiom, ids cui*2/cui*2+1 free exactly because that arg's LIT marshal is skipped).

## 2. Measured (interposer, fib rail N=64)

Generic `rt_pl_dop_unify` 4.64M→1.40M calls (the one var-var head unify/call remains); **`unify_ci` 3.24M calls @83 avg cyc vs the 232 those sites cost generically** — 149 cyc × 3.24M ≈ 2.4 ms/it, matching the observed same-lib wall 12→10 ms/it (~17%). The 2.31 ci/call is the clause-TRY machinery (unify(N,0), unify(N,1) failing into clause 3) — this is the workload first-arg indexing (SPEED-5) will eventually delete; until then ci makes each try ~3× cheaper. Site count: fib 76 ci, qsort 72 ci + 4 cs, nrev 5 cs. Outputs byte-identical on fib/tak/qsort/nrev at every step.

## 3. THE MEASUREMENT TRAP (do not re-step): relink layout noise

The first cross-lib comparison showed fib "regressing" 10→11.4 under the new leaves. FALSE: rebuilding libscrip_rt.so alone moved the GENERIC build 10→12 ms/it (and tak 45→52!) — pure code-layout luck. Against the SAME .so, ci wins 12→10. nrev showed "-6%" in a sequential A/B, then r5 won or tied ALL FIVE interleaved rows. **Protocol now: deltas at the ±20% (fib) / ±15% (tak) / ±6% (nrev) relink-noise scale are only claimable from same-lib A/B (SCRIP_NO_CU twin binaries) with interleaved runs.** The interposer's per-helper cycles are the layout-robust instrument.

## 4. Rung status — honest

REGAIN-5's completion bar (qsort/nrev ≥2× on the rail) is **NOT met**: both flat/within noise (~588/~530 µs/it). Their cost lives in [H|T] STRUCTURE head-unify (list decomposition) + the var-var join `rt_plj_alloc` — slice B. Board: rung 135/138 ×3 (pre-existing float-writer set), smoke pl 5/5 ×3, no-new-global 14/14, sno 7/7, icn 14/14 ×2, m3==m4 on fib/qsort/nrev; prolog regen 20/22 changed (2 const-free programs unchanged — determinism ✓), sno artifacts untouched (cui can never fire for non-`$unify` names).
