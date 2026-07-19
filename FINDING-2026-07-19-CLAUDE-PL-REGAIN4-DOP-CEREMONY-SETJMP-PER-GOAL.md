# FINDING 2026-07-19 (Claude Fable 5, s104) — PL-REGAIN-4: the per-goal dop_call ceremony (setjmp + errjmp + double-setjmp arith) was the payload, not the crossings; fib 20→10 ms/it (2.0×)

Session ask (Lon): improve Prolog speed. Continue. Rung: REGAIN-4 per the s102 cursor.

## 1. Measurement first (LD_PRELOAD rdtsc interposer; no perf/valgrind in container)

fib rail wrapper (bench_prolog_ab_pregut.sh recipe, N=64, ~21,891 calls/iter), HEAD `f7b198fa`, baseline 20–22 ms/it (±2 ms band):

| helper | calls/64it | avg cyc | share |
|---|--:|--:|--|
| rt_pl_dop_unify | 4,636,032 | 255 | **~30–40% of wall — THE hotspot** |
| rt_pl_dop_unwind_nothrow | 1,833,984 | 127 | |
| rt_pl_dop_trail_mark | 1,401,091 | 118 | one per call |
| rt_proc_call_open_det2 | 1,401,024 | 93 | whole open+record path ≈9% |

Probes that KILLED suspects: (a) env-gating `rt_value_trail_tidy_dead_below` = **~0% wall** — the RSP-F-2 death tidy is not a cost; (b) the REGAIN-4 crossing fusion alone (stage×n+open → one `open_detN`) = noise-level wall, confirming REGAIN-1A's own "wall NEUTRAL" note a second time. Crossings are skeleton.

## 2. Root cause — ceremony per goal

Every det opcode routed through `dop_call` (by_name_dispatch.c): **a full setjmp + errjmp push/pop + floor save/set/restore + gc safepoint PER GOAL** — per unify, per trail_mark, per arith. Worse: the classic `is`/2 path ran **two** setjmps (dop_call's + `rt_num_arith`'s own) plus a strcmp op ladder (`dop_ax`) and a second strcmp ladder (`pl_is_op_code`). fib executes 7 such ceremonies per call ({is×3, sub×2, add, gt}).

Throw-reachability audit: `dop_unify` (plj_alloc / trail_push / descr_equal / poison-trap all abort-not-throw), `dop_trail_mark`, `dop_trail_unwind`, `dop_unwind_nothrow` (reads `rt_pl_throw_pending` as a FLAG) — **cannot longjmp**. `is`/cmp/arith CAN (`plc_iso_evaluable`), rail must stay for non-numeric operands only.

## 3. What landed (fib 20→10 ms/it ×6 zero-variance; tak →45 ms/it; output byte-identical at every step)

1. **Fused det open** — `rt_proc_call_open_det0..det4(idx, DESCR_t *a0..)` (rt.c) + `det_fuse` arm in `bcps_det_arm`: site leas caller-frame CELL POINTERS into rsi/rdx/rcx/r8, leaf copies through them into `g_call_args`. Arg MEDIUM unchanged — the slice-B residency decision (slab rehome vs register ABI) stays Lon's call. Caller det crossings 4→2 (`open_detN` + epilogue); `rt_arg_stage` in fib `.s` 7→1 (gen arm only). tak exercises `open_det4` (5 sites).
2. **Nothrow dop rail** — `dop_call_nothrow` keeps the s102 gateway-floor discipline + gc safepoint verbatim, drops the jmp machinery; unify + trail_mark flattened fully inline (4 frames → wrapper+work); the two unwinds via the rail. Impossible-throw safety: an escaping longjmp lands in the next outer dop_call/rt_call_arr catcher, whose own `fl` restore re-seats the floor chain.
3. **Guarded arith fast paths** — is (numeric guard; floor+gc kept, it binds cells), add/sub/mul (`__builtin_*_overflow` reroute; `rt_num_arith`'s int arm is plain `INTVAL(li±ri)` wraparound, so the fallback is bit-identical on every input), six cmps mirroring `pl_num_cmp`'s DOUBLE compare verbatim (ints past 2^53 stay lossy — board-identical, not "fixed"). Non-numeric falls to `dop_call` verbatim.
4. **Int==int terminal** in `plw_unify_cells` before the `rt_descr_equal` extern (slen==0 guard, conservative).
5. **Both-media lazy frame seed** (pre-compaction half of this rung): `flat_seed_off` (emit.h/emit.cpp) + xa_flat binary-medium `rt_jmp_frame_lexprep2` arm — rep-stosb gone in mode 3, matching the mode-4 text arm; seed = slot0 + [suffix,region) only, `SCRIP_ZLS_POISON=1` lane inside the leaf.

Post-rail profile: unify 255→223 avg (interposer-inflated ~40–60), still the top block — see §5.

## 4. Board (all on my build; 3-fail set verified IDENTICAL on pristine `f7b198fa` via stash/rebuild)

rung suite 135/138 ×3 all modes — the 3 fails (`rung23_arith_ext_power`, `rung29_number_ops_float_math`, `rung29_number_ops_float_parts`) are one pre-existing bug: **integral floats print `2.` not `2.0`** (ISO write). s103's cursor says 138/138 at `b917c463`; pristine present-HEAD `f7b198fa` measures 135/138 — the drift predates this session and is banked as its own small rung. smoke pl 5/5 ×3; no-new-global 14/14 (leaves + one file-static fn, zero new globals); sno 7/7; icn 14/14 ×2; fib/tak m3==m4 byte-identical; prolog bench regen 22/22 + 16 sno stale artifacts caught up (dead-β pruning from a prior emitter change; the det arm is a no-op for dyn procs by construction — `is_dyn` ⇒ `det_idx=-1` ⇒ no fuse).

## 5. Residue → next levers

- **REGAIN-4b (small):** callee `lexprep2` is still a crossing (3 total per call; caller-side is at the ≤2 bar). Inlining its seed+bind needs the callee blob to reach `g_call_args`/pcall-top — same residency question as slice B; parked with it.
- **REGAIN-5 (the lever):** unify internals now dominate — var-var join does `rt_plj_alloc` per fresh output arg (~1/call on fib) + deref chains + trail pushes. Port `rt_pl_unify_cell_const` per the PREGUT finding; qsort/nrev are its completion programs.
- Float-format 3-fail fix: separate rung, writer-side.
