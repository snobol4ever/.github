# FINDING — PL-SINK-1: the first emitted Prolog data-plane fast path ($unify), the DT_N lesson, 1.86×

**DATE:** 2026-07-25 (s142)  **AUTHOR:** Claude (Opus)  **DIRECTIVE:** Lon — "Rewrite Prolog to use Byrd Boxes. Move 99% out of the runtime. Continue."

## WHAT LANDED

s141 measured the architectural inversion: mode-4 nrev spends **~86% of leaf samples in the C runtime, ~14% in emitted code** — the exact inverse of SNOBOL4 (97.7% emitted). Verdict: Prolog control is Byrd Boxes but the DATA PLANE (deref, unify, bind+trail, cons, arith) is call-threaded C. PL-SINK is the ladder that inverts it; this session lands rung 1: **the `$unify` box now emits its own fast path** and calls `rt_pl_dop_unify` only as a slow-path oracle.

Files: `SCRIP/src/templates/bb_call_fn.cpp` (five pure emitters — `sink_deref`, `sink_unb`, `sink_trailpush`, `sink_cp16`, `sink_unify2_str` — hooked into the dfp `$unify` route, x86(...) encoders only, one medium-invisible concatenation, internal labels 40–58) and `SCRIP/src/runtime/by_name_dispatch.c` (two `_Static_assert`s anchoring the layouts the template bakes in). Corpus: 22 prolog bench `.s` regenerated.

## THE CONTRACT (bit-identical-by-construction)

The inline path either completes a WHOLE `plw_unify_cells` arm verbatim or jumps to SLOW with **untouched rdi=args** — no partial state ever reaches the leaf. Inline arms, in `plw` order: (1) full deref chase including BOTH `DT_N` forms (slen1 → `p`; slen2 → `VCELL.cellp` at offset 0) and the `DT_PLVAR` chain (`p!=0 && p!=self`); (2) ptr-equal → succeed; (3) exactly one side unbound (`tag∈{SNUL,FAIL}` or PLVAR-self) → inline `pl_trail_push` (uninitialized base or full capacity → SLOW, so C keeps ownership of init and mremap grow; entry = addr + 16-byte old value, 24 bytes, `top` is an int count) then 16-byte bind copy → succeed; (4) both-unbound → SLOW (join/VVB allocation lives in C); (5) `DT_I` vs `DT_I` with q0 exactly 6 on both sides → payload compare → succeed/FAIL (slen≠0 ints → SLOW); (6) PLREF/PLREF → SLOW (recursion); PLREF vs anything else bound → inline FAIL; (7) `DT_R` either side → SLOW (**bit-identical NaN descrs must not fast-succeed** — `rt_descr_equal` uses `r==r`); (8) remaining tags: bit-identical 16 bytes → succeed, else SLOW. Success materializes `rax:rdx = *deref(args[0])` and FAIL materializes `{99,0,0}`, joining the box's existing store/`cmp eax,99` tail — downstream untouched.

Deliberately skipped in the fast path: the GC safepoint and the unwind-floor save/set/restore. Both are alloc/throw-time disciplines; the inline arms allocate nothing and cannot throw, and the floor is only ever read at unwind time. `g_pl_trail` is reached by the dual-medium RIPSEAL load (TEXT `lea r10,[rip+g_pl_trail]`, BINARY movabs of the live address); the symbol is exported from libscrip_rt.so (verified `nm -D`).

## ⚠ THE LESSON: DT_N OR IT NEVER FIRES

First cut bailed to SLOW on tag 9 (`DT_N`), reasoning it rare. Mode-4 A/B: **sink ON was 8% SLOWER** — the marshaled operands of a variable are DT_N name-ref wrappers (that is `plw_entry`'s whole reason to exist), so the fast path tested and then deferred on essentially EVERY unify: pure overhead. Folding both DT_N chase arms into the inline deref (a faithful `plw_cell_deref_slow`, minus the poison read and the 4096 guard) flipped it to **29.5ms vs 55.0ms per run = 1.86×** on a chain bench of 1.28M `$unify` (40³ failure-driven iterations × 20 `=`/2 goals; two mode-4 binaries, sink baked on/off at compile time; 23 sink sites in the ON `.s`, 0 in OFF). Rule for every later rung: **the sink must swallow the operand ENTRY forms, not just the value forms, or it decorates the slow path instead of replacing it.**

## GATES AND HONEST PROFILE

Rung suite **164/164 ×3 modes, run twice** (before and after the DT_N fold). Seven-arm smoke (bind both directions, int-fail + backtrack ACROSS inline trail entries, var-var join, atoms, compound, negation) byte-identical sink-on vs sink-off in mode-3 AND mode-4. All 22 regenerated bench `.s` assemble. Perf: uchain 1.86×; member-style fail-driven m3 −11% (member's own machinery is `$unify_lst`/`$ix_g`, not yet sunk); **nrev flat — exactly what the s141 leaf split predicts** (`dop_unify_lst` + `$mkc` cons carve are nrev's heat). The ladder is validated, not finished.

## BENCH-SHAPE TRAP (pre-existing, measured identical with sink off)

The banked NO-LCO defect is harsher than banked: a 16-conjunct clause body segfaults at recursion depth 10; a 4-conjunct body at ~depth 60; and a shallow 4-wide CALL PYRAMID dies between 64 and 256 total leaf calls — **cumulative frame/arena exhaustion, not depth**. Benchmark Prolog with failure-driven loops (the trail rewinds every iteration) or inside ~64-call envelopes until the LCO rung lands.

## NEXT RUNGS (leaf-heat order)

PL-SINK-2 `$unify_lst` (reuse `sink_deref`/`sink_trailpush` verbatim); PL-SINK-3 `$mkc` bump-carve against the rt_plj frontier; PL-SINK-4 `$is_v`/`$ax_*`/`$cmp_*` int arms; PL-SINK-5 deref-only sites + inlining the ci/cs const-unify hot arms. Then re-run the 44-sample mode-4 leaf split for the KPI: emitted share ≥90% (s141 baseline 14%). Audit `bb_call.cpp`'s byname dfp site (~:303) for whether `$unify` can route there and needs the same hook. Kill switch: `SCRIP_NO_SINK=1` (emit-time); poison-trap sessions must set it.
