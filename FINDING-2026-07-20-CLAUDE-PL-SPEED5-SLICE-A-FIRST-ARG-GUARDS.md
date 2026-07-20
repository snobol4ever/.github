# FINDING — PL-SPEED-5 SLICE A: FIRST-ARG PRE-TRY GUARDS (2026-07-20, Claude Fable 5, session s113)

## WHAT LANDED (3 files, zero emitter/template machinery changes)

Per-clause first-argument indexing **guards** for multi-clause predicates, per gprolog `Pl2Wam/indexing.pl`
(split2 key taxonomy {var, atm(A), int(N), lst, stc(F/N)}) + `Pl_Switch_On_Term` (wam_inst.c:1078) runtime
routing (every tag outside {INT,ATM,LST,STC} — REF/FDV/floats — routes to the try-all path).

1. **`src/lower/lower_prolog.c`** — `pl_no_ix()` hatch + `pl_ix_key()` extractor (TT_ILIT→int,
   TT_FNC/0→atom, TT_MAKELIST/0→atom "[]", TT_MAKELIST→lst, TT_FNC/n→stc; QLIT/FLIT/VAR→unguarded) +
   guard insertion in `lower_pl_pred_graph_new`: clause k with a non-var key gets
   `$ix_g($p0, Kind|Arity<<8, Key)` (γ→head-unify chain, ω→next clause's entry — `centry[k+1]`, or `uwf`
   for the last clause). `centry[k]` and `uw[k]`'s γ both route through the guard, so first-entry AND
   redo-sweep paths benefit. Nothing is bound since the activation's `$trail_mark` on any path reaching a
   guard (verified against the mk→clause0 / fail→`$unwind_nothrow`→clause k+1 graph shape), so the skip
   edge needs no unwind crossing.
2. **`src/runtime/by_name_dispatch.c`** — `dop_ix_g` pure-test leaf (no binds/allocs/trail — the
   cmp-fast-path class, no floor push, no gc safepoint) + `rt_pl_dop_ix_g` wrapper + by-name ladder arm +
   both known-lists. SKIP fires ONLY on arms the unify leaves provably fail: PLREF-vs-const (ci/cs
   PLREF→fail), PLREF slen≠slen (plw_unify_cells:119 requires equality; `$mkc` and the guard intern via
   the same `prolog_atom_intern`), bound-const-vs-compound-key (either-PLREF / lst total-case), same-type
   const mismatch (ci int compare / rt_descr_equal S-S strcmp). **Int↔atom crosses PROCEED** —
   `rt_descr_equal`'s VARVAL arm string-coerces there ("5" unifies with 5 in SCRIP) and the guard must not
   change outcomes. slen≠0 consts, DT_R, NULL strings, unknown tags all PROCEED.
3. **`src/templates/bb_call.cpp`** — extern decl + `dop_direct_fp` row `{"$ix_g", 3, ...}`. The guard
   rides the EXISTING direct-det-leaf template arm (marshal 3 operands; `lea rdi; mov esi,3; call
   rt_pl_dop_ix_g@PLT; cmp eax,99; je <skip>`) — no new emitter shapes.

Hatch: **`SCRIP_NO_IX=1`** (compile-time, lowering-side) = the same-lib twin instrument (SCC/CU/UL
pattern). New harness: `scripts/bench_prolog_ix_ab.sh` — one compiler + one lib, baseline twin emitted
under the hatch, interleaved A,B ×5, median cells, plus a guard-count grep of the emitted `.s`.

## BOARD (all green, semantics-neutral confirmed)

- Rung suite **135/138 in ALL THREE modes** — exactly the pre-existing float trio
  (rung23_arith_ext_power, rung29_number_ops_float_math, rung29_number_ops_float_parts). Zero new.
- Smoke pl **5/5 ×3**; sno **7/7**; icn **14/14 ×2**. no-new-global **PASS floor 14** (leaf's `dot_sl`
  is function-local static — the sanctioned rt_arena.c precedent).
- Purpose-built dispatch test (same-key redo pair, list/nil/struct/int subjects, var-subject try-all):
  byte-identical output across guards-on m3, `SCRIP_NO_IX=1` m3, and m4.
- Prolog bench `.s` artifacts regened: 22 emitted, 21 changed, 0 rejected (corpus commit).

## MEASUREMENT (same-lib twins, interleaved ×5 medians, 1-vCPU container)

| bench | base | ix | ix/base | guard sites | note |
|-------|------|-----|---------|-------------|------|
| qsort | 7.685s | 7.254s | **0.944** | 5 | l__(16384), corpus N |
| nrev  | 1.981s | 1.930s | **0.974** | 8 | l__(8192) scaled copy |
| deriv | 0.235s | 0.178s | **0.757** | 8 | l__(8192) scaled copy; zero run overlap |
| tak   | 1.336s | 1.325s | 0.992 | **0** | all-var heads → correctly no guards; twin-noise floor ≈1% |
| fib   | 1.225s | 1.224s | 0.999 | 2 | int-key pair skipped, flat |

**Completion bar (qsort/nrev/deriv ≥25% each) NOT MET by slice A alone**: deriv 24.3% (at the line),
qsort 5.6%, nrev 2.6%.

## WHY — the pass-tax mechanism (measured, not speculated)

A guard is a marshaled C-call crossing — the SAME cost class as the failed `$unify_ci`/`$unify_lst` it
replaces (s105/s106 made failed tries one cheap call with no pattern build). So a **skip** is roughly
cost-neutral per event, and a **pass** (hot path, e.g. qsort's cons subject through its cons-first
clause) is pure addition. nc=2 predicates therefore net ≈ wash. deriv wins because a bound-struct
subject skips MANY clauses per call and each skipped struct clause also skips its `$mkc` pattern BUILD
(allocation + kid joins) — one guard call replaces several calls plus allocation.

## ESCALATION PATH (next rungs, in payoff order)

1. **INLINE GUARD EMISSION** — turn the guard from marshal+call into ~5 inline instructions (tag load,
   compare, jcc), making the pass path near-free and every nc=2 predicate net-positive.
   **CONSTRAINT DISCOVERED THIS SESSION: functor intern ids are RUNTIME-assigned** (first-intern order in
   the running process), so struct/list keys' packed `slen` and atom identity CANNOT be baked into mode-4
   `.s` as immediates. The inline slice needs a lazy-intern data cell per key (RO-seal string + one
   writable slot patched on first execution, `.Lrkfn` rodata idiom + a `.bss` word) or a per-pred key
   table prepared at registration. INT keys alone are trivially bakeable. This is a real design rung —
   read the BB-CODEGEN DESIGN SET first (R7: new encoder + dispatch case in x86_asm.h).
2. **UNIQUE-CANDIDATE DET DELIVERY** — the rung text's deeper half ("NO choice point when unique — skip
   `$trail_mark`/MOVE_LABEL machinery for that path"): when the guard chain proves the delivered clause is
   the LAST candidate for this activation's bound arg0, deliver via the existing per-delivery det arm
   (`bcps_det_arm`, flat_gen=0 epilogue) instead of IR_SUSPEND. This is where qsort/nrev's ≥25% most
   plausibly lives (they are nondet and pay the gen rail per delivery).

## BANKED (container/ops findings)

- **Background processes DIE between tool calls** in this container — every long build must run
  foreground in `timeout`-chunked calls.
- The `out/libscrip_rt.so` Makefile rule is ONE monolithic gcc (non-resumable under timeout). Chunked
  per-file harness at `/tmp/rt_chunk.sh` + `/tmp/rt_pic_objs/` (210 objects; flags extracted from
  `make -n`; watch the `.S` trampoline source when tokenizing). Link:
  `gcc -shared -fPIC /tmp/rt_pic_objs/*.o -lm -lstdc++ -lpthread -o out/libscrip_rt.so`.
- `/usr/bin/time` absent — `date +%s%N` deltas instead.
- Bench copies with scaled `l__(N)` live in `/tmp/ixsrc/` (nrev/deriv 65536→8192); ratios unaffected,
  chunk-window friendly.
